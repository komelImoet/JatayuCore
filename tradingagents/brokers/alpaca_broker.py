import logging
import os
from typing import Any

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

RATING_ACTION = {"Buy": OrderSide.BUY, "Overweight": OrderSide.BUY}
EXECUTABLE_RATINGS = frozenset(RATING_ACTION.keys())


def _parse_field(text: str, field: str) -> str | None:
    import re
    m = re.search(
        rf"\*{{0,2}}{re.escape(field)}\*{{0,2}}\s*:\s*(.+?)(?:\n|$)",
        text,
        re.IGNORECASE,
    )
    return m.group(1).strip() if m else None


def _parse_qty(raw: str) -> int | None:
    """Extract integer quantity from strings like '5%', '10 shares', '2'."""
    import re
    raw = raw.strip().lower().replace(",", "")
    m = re.search(r"\d+", raw)
    return int(m.group()) if m else None


class AlpacaBroker:
    """Places trades on Alpaca based on agent decisions.

    Implements the same ``send_decision`` protocol used by notifiers so it can
    be passed directly into the notifiers list of TradingAgentsGraph.
    """

    def __init__(
        self,
        api_key: str | None = None,
        secret_key: str | None = None,
        paper: bool = True,
        notifier=None,
    ):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY", "")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY", "")
        self.paper = paper
        self.notifier = notifier

        if not self.api_key or not self.secret_key:
            logger.warning("ALPACA_API_KEY or ALPACA_SECRET_KEY not set — broker disabled")
            return

        self._client: TradingClient | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.secret_key)

    @property
    def client(self) -> TradingClient:
        if self._client is None:
            self._client = TradingClient(
                api_key=self.api_key,
                secret_key=self.secret_key,
                paper=self.paper,
            )
        return self._client

    def account_info(self) -> dict:
        info = self.client.get_account()
        return {
            "equity": float(info.equity),
            "cash": float(info.cash),
            "buying_power": float(info.buying_power),
            "status": info.status,
        }

    def send_decision(self, state: dict[str, Any]) -> bool:
        """Match the notifier protocol — called after each propagation."""
        if not self.enabled:
            return False

        ticker = state.get("company_of_interest", "")
        final_text = state.get("final_trade_decision", "")
        trader_text = state.get("trader_investment_decision", "")

        rating = (_parse_field(final_text, "Rating") or "Hold").strip()
        if rating not in EXECUTABLE_RATINGS:
            logger.info("Alpaca: %s rating %s → no action", ticker, rating)
            return False

        sizing_raw = _parse_field(trader_text, "Position Sizing") or ""
        qty = _parse_qty(sizing_raw)

        if qty is None:
            logger.warning("Alpaca: could not parse qty from '%s'", sizing_raw)
            if self.notifier:
                self.notifier.send_error(ticker, f"Cannot parse qty: {sizing_raw}")
            return False

        side = RATING_ACTION[rating]
        return self._place_order(ticker, qty, side)

    def _place_order(self, ticker: str, qty: int, side: OrderSide) -> bool:
        try:
            order_req = MarketOrderRequest(
                symbol=ticker,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
            )
            order = self.client.submit_order(order_req)
            msg = (
                f"<b>Alpaca Order Placed</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{'🟢' if side == OrderSide.BUY else '🔴'} <b>Side:</b> {side.name}\n"
                f"<b>Ticker:</b> {ticker}\n"
                f"<b>Qty:</b> {qty}\n"
                f"<b>Order:</b> #{order.id}"
            )
            if self.notifier:
                self.notifier._send(msg)
            logger.info(
                "Alpaca: %s %d × %s → order #%s",
                side.name, qty, ticker, order.id,
            )
            return True
        except Exception as e:
            logger.error("Alpaca order failed for %s: %s", ticker, e)
            if self.notifier:
                self.notifier.send_error(ticker, f"Order failed: {e}")
            return False
