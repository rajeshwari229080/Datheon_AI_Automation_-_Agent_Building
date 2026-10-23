import time
import httpx
from typing import Any, Dict, List, Optional
from app.adapters.base import BaseAdapter
from app.config import settings, logger

class SlackAdapter(BaseAdapter):
    """Adapter for Slack Webhooks and Web API with deterministic mock fallback."""

    def __init__(self):
        super().__init__("SlackAdapter")
        self.bot_token = settings.slack_bot_token
        self.webhook_url = settings.slack_webhook_url
        self.default_channel = settings.slack_default_channel
        self.mock_sent_messages: List[Dict[str, Any]] = []
        self.mock_channels: Dict[str, Dict[str, Any]] = {}

    def is_configured(self) -> bool:
        return bool((self.webhook_url or self.bot_token) and not self.is_demo_mode)

    def health_check(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "status": "DEMO_MODE",
                "configured": False,
                "message": "Running mock Slack adapter. Provide SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN for live mode.",
                "channel": self.default_channel
            }
        return {"status": "HEALTHY", "configured": True, "channel": self.default_channel}

    def send_lead_alert(self, lead_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Send a formatted new qualified lead alert."""
        priority_emoji = "🔴" if lead_summary.get("priority") == "HIGH" else ("🟡" if lead_summary.get("priority") == "MEDIUM" else "🟢")
        text = (
            f"{priority_emoji} *New Inbound Lead Qualified*\n"
            f"• *Name*: {lead_summary.get('name')} ({lead_summary.get('company')})\n"
            f"• *Email*: {lead_summary.get('email')} | *Phone*: {lead_summary.get('phone') or 'N/A'}\n"
            f"• *Budget*: ${lead_summary.get('budget', 0):,.2f} | *Score*: {lead_summary.get('score')}/100\n"
            f"• *Priority*: `{lead_summary.get('priority')}` | *Status*: `{lead_summary.get('qualification_status')}`\n"
            f"• *Summary*: {lead_summary.get('qualification_summary')}\n"
            f"• *Sales Talking Points*:\n  - " + "\n  - ".join(lead_summary.get("talking_points", ["Standard sales intake"]))
        )
        return self._dispatch_message(text=text, channel=self.default_channel)

    def send_approval_notification(self, title: str, details: Dict[str, Any], channel: Optional[str] = None) -> Dict[str, Any]:
        """Send an urgent human approval notification."""
        ch = channel or self.default_channel
        text = f"⚠️ *ACTION REQUIRED: {title}*\n" + "\n".join([f"• *{k}*: {v}" for k, v in details.items()])
        return self._dispatch_message(text=text, channel=ch)

    def provision_project_channel(self, project_name: str, client_name: str) -> Dict[str, Any]:
        """Provision a dedicated Slack channel for an onboarding customer project."""
        channel_name = f"proj-{project_name.lower().replace(' ', '-')}"[:30]
        if not self.is_configured():
            mock_id = f"C_MOCK_{int(time.time()*1000)}"
            self.mock_channels[channel_name] = {
                "id": mock_id,
                "name": channel_name,
                "project": project_name,
                "client": client_name,
                "created_at": time.time()
            }
            logger.info(f"[SlackAdapter-MOCK] Provisioned channel #{channel_name} ({mock_id})")
            return {
                "success": True,
                "mode": "MOCK",
                "channel_id": mock_id,
                "channel_name": channel_name
            }

        # Live Slack Web API channel creation
        url = "https://slack.com/api/conversations.create"
        headers = {"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json"}
        payload = {"name": channel_name, "is_private": False}
        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, headers=headers, json=payload)
            data = res.json()
            if data.get("ok"):
                ch_info = data.get("channel", {})
                return {
                    "success": True,
                    "mode": "LIVE",
                    "channel_id": ch_info.get("id"),
                    "channel_name": ch_info.get("name")
                }
            if data.get("error") == "name_taken":
                return {
                    "success": True,
                    "mode": "LIVE",
                    "channel_id": "existing",
                    "channel_name": channel_name,
                    "note": "Channel already exists"
                }
            raise RuntimeError(f"Slack API error: {data.get('error')}")

    def _dispatch_message(self, text: str, channel: str) -> Dict[str, Any]:
        payload = {"channel": channel, "text": text}
        if not self.is_configured():
            msg_id = f"msg_mock_{int(time.time()*1000)}"
            self.mock_sent_messages.append({
                "id": msg_id,
                "channel": channel,
                "text": text,
                "timestamp": time.time()
            })
            logger.info(f"[SlackAdapter-MOCK] Message dispatched to {channel}")
            return {"success": True, "mode": "MOCK", "message_id": msg_id, "channel": channel}

        if self.webhook_url:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(self.webhook_url, json={"text": text})
                if res.status_code == 200:
                    return {"success": True, "mode": "LIVE", "delivery": "webhook"}
                raise RuntimeError(f"Slack webhook error ({res.status_code}): {res.text}")

        url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json"}
        with httpx.Client(timeout=5.0) as client:
            res = client.post(url, headers=headers, json=payload)
            data = res.json()
            if data.get("ok"):
                return {"success": True, "mode": "LIVE", "message_id": data.get("ts"), "channel": channel}
            raise RuntimeError(f"Slack API error: {data.get('error')}")

slack_adapter = SlackAdapter()
