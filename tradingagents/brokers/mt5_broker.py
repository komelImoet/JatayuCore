import logging
import os
import re
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv

from tradingagents.trade_journal import TradeJournal

load_dotenv()

logger = logging.getLogger(__name__)

EXECUTABLE_RATINGS: dict[str, str] = {
    "Buy": "Buy",
    "Overweight": "Buy",
    "Underweight": "Sell",
    "Sell": "Sell",
}


def _parse_field(text: str, field: str) -> str | None:
    m = re.search(
        rf"\*{{0,2}}{re.escape(field)}\*{{0,2}}\s*:\s*(.+?)(?:\n|$)",
        text,
        re.IGNORECASE,
    )
    return m.group(1).strip() if m else None


def _parse_qty_pct(raw: str, equity: float | None = None) -> int | None:
    """Extract integer percentage (0-100). Default 1%."""
    raw = raw.strip().lower().replace(",", "")
    m_pct = re.search(r"(\d+(?:\.\d+)?)\s*%", raw)
    if m_pct:
        return int(float(m_pct.group(1)))
    return None


def _positions_summary(positions: list) -> str:
    if not positions:
        return "📭 No open positions"
    lines = [f"<b>Open Positions: {len(positions)}</b>"]
    for p in positions:
        side = "🟢" if p.type == 0 else "🔴"  # POSITION_TYPE_BUY=0
        lines.append(
            f"{side} {p.symbol}: {p.volume}× @ ${p.price_open:.2f} "
            f"| P&L ${p.profit:.2f}"
        )
    return "\n".join(lines)


class MT5Broker:
    """Places trades on MT5 based on agent decisions.

    Connects directly to the MetaTrader5 terminal running on the same machine.
    Supports Buy/Overweight (long) and Sell/Underweight (close long).
    Implements the ``send_decision`` protocol used by notifiers.
    """

    def __init__(
        self,
        notifier=None,
        circuit_breaker=None,
        trade_journal: TradeJournal | None = None,
        magic: int = 250430,
        deviation: int = 20,
    ):
        self._mt5 = None
        self.notifier = notifier
        self.circuit_breaker = circuit_breaker
        self.journal = trade_journal or TradeJournal()
        self.magic = magic
        self.deviation = deviation
        self._connected = False

    @property
    def enabled(self) -> bool:
        return True

    def _ensure_connected(self):
        if self._connected and self._mt5:
            try:
                info = self._mt5.account_info()
                if info is not None:
                    return
            except Exception:
                pass
            self._connected = False
            self._mt5 = None

        import MetaTrader5 as mt5
        self._mt5 = mt5
        ok = mt5.initialize()
        if not ok:
            err = mt5.last_error()
            raise ConnectionError(f"MT5 initialize failed: {err}")

        login = int(os.getenv("MT5_LOGIN", 0))
        password = os.getenv("MT5_PASSWORD", "")
        server = os.getenv("MT5_SERVER", "")
        if login and password:
            ok = mt5.login(login=login, password=password, server=server)
            if not ok:
                err = mt5.last_error()
                raise ConnectionError(f"MT5 login failed: {err}")

        self._connected = True
        logger.info("MT5 connected (account #%s)", os.getenv("MT5_LOGIN", "local"))

    def account_info(self) -> dict:
        self._ensure_connected()
        info = self._mt5.account_info()
        return {
            "balance": info.balance,
            "equity": info.equity,
            "margin": info.margin,
            "free_margin": info.margin_free,
        }

    def get_positions(self) -> list:
        self._ensure_connected()
        positions = self._mt5.positions_get()
        return positions or []

    def get_positions_normalized(self) -> list[dict]:
        positions = self.get_positions()
        result = []
        for p in positions:
            qty = float(p.volume)
            result.append({
                "symbol": p.symbol,
                "qty": qty,
                "avg_entry_price": float(p.price_open),
                "current_price": float(p.price_current),
                "unrealized_pl": float(p.profit),
                "side": "long" if p.type == 0 else "short",
            })
        return result

    def positions_summary(self) -> str:
        return _positions_summary(self.get_positions())

    def has_position(self, symbol: str) -> bool:
        self._ensure_connected()
        positions = self._mt5.positions_get(symbol=symbol)
        return len(positions) > 0 if positions else False

    def close_position(self, symbol: str) -> bool:
        self._ensure_connected()
        positions = self._mt5.positions_get(symbol=symbol)
        if not positions:
            return False

        for pos in positions:
            tick = self._mt5.symbol_info_tick(symbol)
            close_type = (
                self._mt5.ORDER_TYPE_SELL if pos.type == self._mt5.POSITION_TYPE_BUY
                else self._mt5.ORDER_TYPE_BUY
            )
            price = tick.bid if close_type == self._mt5.ORDER_TYPE_SELL else tick.ask
            request = {
                "action": self._mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": price,
                "deviation": self.deviation,
                "magic": self.magic,
                "comment": "JatayuCore close",
                "type_time": self._mt5.ORDER_TIME_GTC,
                "type_filling": self._mt5.ORDER_FILLING_IOC,
            }
            result = self._mt5.order_send(request)
            if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
                logger.error("MT5 close failed for %s: retcode=%s", symbol, result.retcode if result else "None")
                return False
        return True

    def send_decision(self, state: dict[str, Any]) -> bool:
        if self.circuit_breaker and self.circuit_breaker.is_triggered():
            logger.warning("CircuitBreaker active — skipping trade")
            if self.notifier:
                self.notifier._send(
                    f"<b>MT5 Skip</b>\n━━━━━━━━━━━━━━━━━━\n"
                    f"<b>Reason:</b> Circuit breaker active — max SL hit today"
                )
            return False

        try:
            self._ensure_connected()
        except ConnectionError as e:
            logger.error("MT5 not available: %s", e)
            if self.notifier:
                self.notifier.send_error("MT5", f"Connection failed: {e}")
            return False

        ticker = state.get("company_of_interest", "")
        final_text = state.get("final_trade_decision", "")
        trader_text = state.get("trader_investment_decision", "")

        rating = (_parse_field(final_text, "Rating") or "Hold").strip()
        action = EXECUTABLE_RATINGS.get(rating)
        if action is None:
            logger.info("MT5: %s rating %s → skip", ticker, rating)
            return False

        info = self.account_info()
        equity = info["equity"]

        if action == "Buy":
            if self.has_position(ticker):
                logger.info("MT5: %s → already have position, skip Buy", ticker)
                if self.notifier:
                    self.notifier._send(
                        f"<b>MT5 Skip</b>\n━━━━━━━━━━━━━━━━━━\n"
                        f"<b>Ticker:</b> {ticker}\n"
                        f"<b>Reason:</b> Already have position"
                    )
                return False

            sizing_raw = _parse_field(trader_text, "Position Sizing") or ""
            pct = _parse_qty_pct(sizing_raw) or 1
            return self._place_order(ticker, equity, pct)

        if action == "Sell":
            if not self.has_position(ticker):
                logger.info("MT5: %s → no position to sell", ticker)
                return False
            return self._close_and_notify(ticker)

        return False

    def _calc_lot(self, symbol: str, equity: float, pct: int) -> float | None:
        sym_info = self._mt5.symbol_info(symbol)
        if sym_info is None:
            logger.error("MT5: symbol %s not found", symbol)
            return None

        if not self._mt5.symbol_select(symbol, True):
            logger.error("MT5: symbol %s not available in Market Watch", symbol)
            return None

        tick = self._mt5.symbol_info_tick(symbol)
        price = (tick.ask + tick.bid) / 2 or tick.ask

        dollar_amount = equity * pct / 100
        contract_size = sym_info.trade_contract_size  # e.g., 100,000 for forex
        raw_lot = dollar_amount / (contract_size * price)
        lot_step = sym_info.volume_step
        min_lot = sym_info.volume_min
        max_lot = sym_info.volume_max

        lot = round(raw_lot / lot_step) * lot_step
        lot = max(min_lot, min(lot, max_lot))
        return lot

    def _place_order(self, symbol: str, equity: float, pct: int) -> bool:
        lot = self._calc_lot(symbol, equity, pct)
        if lot is None or lot <= 0:
            logger.error("MT5: invalid lot size for %s (pct=%d)", symbol, pct)
            return False

        tick = self._mt5.symbol_info_tick(symbol)
        price = tick.ask
        request = {
            "action": self._mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": self._mt5.ORDER_TYPE_BUY,
            "price": price,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "JatayuCore buy",
            "type_time": self._mt5.ORDER_TIME_GTC,
            "type_filling": self._mt5.ORDER_FILLING_IOC,
        }

        result = self._mt5.order_send(request)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            err_msg = f"retcode={result.retcode}" if result else "None"
            logger.error("MT5 buy failed for %s: %s", symbol, err_msg)
            if self.notifier:
                self.notifier.send_error(symbol, f"Buy failed: {err_msg}")
            return False

        fill_price = float(result.price)
        self.journal.record_entry(symbol, "buy", lot, fill_price, str(result.order))
        msg = (
            f"<b>MT5 Order Placed</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🟢 <b>Side:</b> Buy\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Lot:</b> {lot}\n"
            f"<b>Fill:</b> ${fill_price:.5f}\n"
            f"<b>Ticket:</b> #{result.order}"
        )
        if self.notifier:
            self.notifier._send(msg)
        logger.info("MT5: Buy %s %s lot @ %.5f → #%s", symbol, lot, fill_price, result.order)
        return True

    def _close_and_notify(self, symbol: str) -> bool:
        positions = self._mt5.positions_get(symbol=symbol)
        if not positions:
            return False

        pos = positions[0]
        tick = self._mt5.symbol_info_tick(symbol)
        close_type = (
            self._mt5.ORDER_TYPE_SELL if pos.type == self._mt5.POSITION_TYPE_BUY
            else self._mt5.ORDER_TYPE_BUY
        )
        price = tick.bid if close_type == self._mt5.ORDER_TYPE_SELL else tick.ask
        request = {
            "action": self._mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": close_type,
            "position": pos.ticket,
            "price": price,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": "JatayuCore close",
            "type_time": self._mt5.ORDER_TIME_GTC,
            "type_filling": self._mt5.ORDER_FILLING_IOC,
        }

        result = self._mt5.order_send(request)
        if result is None or result.retcode != self._mt5.TRADE_RETCODE_DONE:
            logger.error("MT5 close failed for %s", symbol)
            return False

        fill_price = float(result.price)
        self.journal.record_exit(symbol, fill_price, reason="signal")
        msg = (
            f"<b>MT5 Position Closed</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔴 <b>Symbol:</b> {symbol}\n"
            f"<b>Fill:</b> ${fill_price:.5f}\n"
            f"<b>Reason:</b> Sell/Underweight signal"
        )
        if self.notifier:
            self.notifier._send(msg)
        logger.info("MT5: closed %s @ %.5f", symbol, fill_price)
        return True
