import httpx
from typing import Optional
from ..core import settings


class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, message: str) -> bool:
        """
        Send a message via Telegram bot.
        """
        if not self.bot_token or not self.chat_id:
            print("Telegram bot token or chat ID not configured")
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    async def send_alert(
        self,
        server_name: str,
        alert_name: str,
        metric_name: str,
        value: float,
        threshold: float,
        comparison: str,
        status: str,
    ) -> bool:
        """
        Send an alert notification.
        """
        status_emoji = "🔴" if status == "triggered" else "🟢"
        message = f"""
{status_emoji} <b>Alert {status.upper()}</b>

<b>Server:</b> {server_name}
<b>Alert:</b> {alert_name}
<b>Metric:</b> {metric_name}
<b>Current Value:</b> {value:.2f}
<b>Threshold:</b> {comparison} {threshold}

<i>Timestamp: {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>
"""
        return await self.send_message(message.strip())


telegram_service = TelegramService()
