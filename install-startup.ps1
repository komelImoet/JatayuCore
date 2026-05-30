# JatayuCore Auto-Start — Windows Task Scheduler
# Run this PowerShell script AS ADMINISTRATOR once.
# It creates a task that starts WSL + JatayuCore at every Windows boot.

$taskName = "JatayuCore-Trading"
$distro = "Arch"
$wslPath = "$env:SystemRoot\System32\wsl.exe"
$action = New-ScheduledTaskAction -Execute $wslPath -Argument "-d $distro -- sudo systemctl start jatayu"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force

Write-Host "✅ Task '$taskName' created – will auto-start JatayuCore at every Windows boot."
