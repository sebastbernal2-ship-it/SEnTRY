"""
Email and notification services for S.E.N.T.R.Y. alerts.
Provides a clean interface for sending alerts via email and webhooks.
"""
import os
import logging
import time
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class EmailNotificationService:
    """
    Handles sending email alerts.
    
    Credentials are provided via environment variables:
    - SENTRY_EMAIL_PROVIDER: 'smtp' or 'sendgrid' (default: 'smtp')
    - SENTRY_SMTP_HOST: SMTP server hostname
    - SENTRY_SMTP_PORT: SMTP server port (default: 587)
    - SENTRY_SMTP_USER: SMTP username
    - SENTRY_SMTP_PASSWORD: SMTP password
    - SENTRY_SENDGRID_API_KEY: SendGrid API key
    - SENTRY_EMAIL_FROM: Sender email address
    - SENTRY_EMAIL_TO: Recipient email address (comma-separated)
    """

    def __init__(self):
        """Initialize email service from environment variables."""
        self.provider = os.getenv("SENTRY_EMAIL_PROVIDER", "smtp")
        self.from_email = os.getenv("SENTRY_EMAIL_FROM", "sentry@alerts.local")
        self.to_emails = os.getenv("SENTRY_EMAIL_TO", "").split(",") if os.getenv("SENTRY_EMAIL_TO") else []
        self.enabled = bool(self.to_emails)

        if self.provider == "sendgrid":
            self.api_key = os.getenv("SENTRY_SENDGRID_API_KEY")
            if not self.api_key and self.enabled:
                logger.warning("SendGrid provider selected but SENTRY_SENDGRID_API_KEY not set")
                self.enabled = False
        elif self.provider == "smtp":
            self.smtp_host = os.getenv("SENTRY_SMTP_HOST", "smtp.gmail.com")
            self.smtp_port = int(os.getenv("SENTRY_SMTP_PORT", "587"))
            self.smtp_user = os.getenv("SENTRY_SMTP_USER")
            self.smtp_password = os.getenv("SENTRY_SMTP_PASSWORD")
            if not (self.smtp_user and self.smtp_password) and self.enabled:
                logger.warning("SMTP provider selected but credentials not set")
                self.enabled = False

    def send_alert_email(self, alert: Dict[str, Any]) -> bool:
        """
        Send an alert email.
        
        Args:
            alert: Alert dict with id, module, title, description, severity, score, etc.
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Email notifications disabled. Would send: {alert['title']}")
            return False

        subject = f"[S.E.N.T.R.Y. {alert['severity'].upper()}] {alert['title']}"
        body = self._format_email_body(alert)

        try:
            if self.provider == "sendgrid":
                return self._send_sendgrid(subject, body)
            else:
                return self._send_smtp(subject, body)
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_batch_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Send multiple alerts.
        
        Args:
            alerts: List of alert dicts
        
        Returns:
            Number of alerts successfully sent
        """
        count = 0
        for alert in alerts:
            if self.send_alert_email(alert):
                count += 1
        return count

    def _format_email_body(self, alert: Dict[str, Any]) -> str:
        """Format alert as email body HTML."""
        severity_color = {
            "low": "#00FF41",
            "medium": "#facc15",
            "high": "#f87171",
        }.get(alert.get("severity", "medium"), "#94a3b8")

        return f"""
<html>
  <body style="font-family: monospace; background: #000; color: #94a3b8; padding: 20px;">
    <div style="border-left: 4px solid {severity_color}; padding-left: 16px;">
      <h2 style="color: {severity_color}; margin-top: 0;">{alert.get('title', 'Alert')}</h2>
      
      <p><strong>Module:</strong> {alert.get('module', 'unknown')}</p>
      <p><strong>Severity:</strong> <span style="color: {severity_color};">{alert.get('severity', 'unknown').upper()}</span></p>
      <p><strong>Score:</strong> <span style="color: {severity_color};">{alert.get('score', 0)}/100</span></p>
      <p><strong>Label:</strong> {alert.get('label', 'Unknown')}</p>
      <p><strong>Timestamp:</strong> {alert.get('timestamp', 'unknown')}</p>
      
      <hr style="border: none; border-top: 1px solid #1e293b; margin: 20px 0;">
      
      <p><strong>Description:</strong></p>
      <p>{alert.get('description', 'No description available.')}</p>
      
      <hr style="border: none; border-top: 1px solid #1e293b; margin: 20px 0;">
      <p style="font-size: 12px; color: #475569;">
        This is an automated S.E.N.T.R.Y. alert. Do not reply to this email.
      </p>
    </div>
  </body>
</html>
        """

    def _send_smtp(self, subject: str, body: str) -> bool:
        """Send email via SMTP (Gmail, Amazon SES, etc.)."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)

            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, self.to_emails, msg.as_string())

            logger.info(f"Email sent to {self.to_emails}")
            return True
        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return False

    def _send_sendgrid(self, subject: str, body: str) -> bool:
        """Send email via SendGrid API."""
        try:
            import requests

            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "personalizations": [{"to": [{"email": email} for email in self.to_emails]}],
                "from": {"email": self.from_email},
                "subject": subject,
                "content": [{"type": "text/html", "value": body}],
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()

            logger.info(f"SendGrid email sent to {self.to_emails}")
            return True
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            return False


class WebhookNotificationService:
    """
    Handles sending alerts to webhook endpoints (Discord, Slack, etc.).
    
    Webhook URLs provided via:
    - SENTRY_WEBHOOK_URL: Webhook endpoint URL
    """

    def __init__(self):
        """Initialize webhook service."""
        self.webhook_url = os.getenv("SENTRY_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)
        self.timeout_seconds = float(os.getenv("SENTRY_WEBHOOK_TIMEOUT_SECONDS", "10"))
        self.max_retries = int(os.getenv("SENTRY_WEBHOOK_MAX_RETRIES", "3"))
        self.min_interval_seconds = float(os.getenv("SENTRY_WEBHOOK_MIN_INTERVAL_SECONDS", "0.35"))
        self.base_retry_seconds = float(os.getenv("SENTRY_WEBHOOK_BASE_RETRY_SECONDS", "1.5"))

    def _is_discord_webhook(self) -> bool:
        """Return True when webhook URL points to Discord."""
        return bool(self.webhook_url and "discord.com/api/webhooks" in self.webhook_url)

    def _discord_color(self, severity: str) -> int:
        """Map severity to Discord embed color."""
        mapping = {
            "low": 0x00FF41,
            "medium": 0xFACC15,
            "high": 0xF87171,
        }
        return mapping.get((severity or "").lower(), 0x94A3B8)

    def _discord_payload(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Build Discord-compatible webhook payload."""
        severity = (alert.get("severity") or "unknown").upper()
        score = alert.get("score", 0)
        module = alert.get("module", "unknown")
        label = alert.get("label", "Unknown")
        timestamp = alert.get("timestamp")

        return {
            "username": "S.E.N.T.R.Y.",
            "content": f"[{severity}] {alert.get('title', 'Alert')}",
            "embeds": [
                {
                    "title": alert.get("title", "Alert"),
                    "description": alert.get("description", "No description available."),
                    "color": self._discord_color(alert.get("severity", "medium")),
                    "fields": [
                        {"name": "Module", "value": str(module), "inline": True},
                        {"name": "Severity", "value": str(severity), "inline": True},
                        {"name": "Score", "value": f"{score}/100", "inline": True},
                        {"name": "Label", "value": str(label), "inline": True},
                    ],
                    "timestamp": timestamp,
                }
            ],
        }

    def _generic_payload(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Build generic JSON payload for non-Discord webhooks."""
        return {
            "alert_id": alert.get("id"),
            "module": alert.get("module"),
            "title": alert.get("title"),
            "description": alert.get("description"),
            "severity": alert.get("severity"),
            "score": alert.get("score"),
            "label": alert.get("label"),
            "timestamp": alert.get("timestamp"),
        }

    @staticmethod
    def _parse_retry_after_seconds(response: Any) -> Optional[float]:
        """Extract Retry-After seconds from headers or JSON body when present."""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass

        try:
            payload = response.json()
            value = payload.get("retry_after")
            if value is None:
                return None
            # Discord may provide milliseconds in some responses.
            value = float(value)
            return value / 1000.0 if value > 100 else value
        except Exception:
            return None

    def send_alert_webhook(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert to webhook.
        
        Args:
            alert: Alert dict
        
        Returns:
            True if webhook called successfully
        """
        if not self.enabled:
            logger.debug(f"Webhook notifications disabled")
            return False

        try:
            import requests

            payload = (
                self._discord_payload(alert)
                if self._is_discord_webhook()
                else self._generic_payload(alert)
            )

            for attempt in range(self.max_retries + 1):
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=self.timeout_seconds,
                )

                if response.status_code < 400:
                    logger.info(f"Webhook alert sent to {self.webhook_url}")
                    return True

                if response.status_code == 429 and attempt < self.max_retries:
                    retry_after = self._parse_retry_after_seconds(response)
                    sleep_for = retry_after if retry_after is not None else self.base_retry_seconds * (2 ** attempt)
                    sleep_for = max(0.25, sleep_for)
                    logger.warning(
                        f"Webhook rate-limited (429). Retrying in {sleep_for:.2f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(sleep_for)
                    continue

                if 500 <= response.status_code < 600 and attempt < self.max_retries:
                    sleep_for = self.base_retry_seconds * (2 ** attempt)
                    logger.warning(
                        f"Webhook server error ({response.status_code}). Retrying in {sleep_for:.2f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(sleep_for)
                    continue

                response.raise_for_status()

            return False
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return False

    def send_batch_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """Send multiple webhook alerts with pacing to reduce rate-limit failures."""
        sent = 0
        for index, alert in enumerate(alerts):
            if self.send_alert_webhook(alert):
                sent += 1
            if index < len(alerts) - 1 and self.min_interval_seconds > 0:
                time.sleep(self.min_interval_seconds)
        return sent


def send_notifications(
    alerts: List[Dict[str, Any]],
    email_enabled: bool = True,
    webhook_enabled: bool = True,
) -> Dict[str, int]:
    """
    Send notifications for a batch of alerts.
    
    Args:
        alerts: List of alert dicts
        email_enabled: Whether to attempt email sending
        webhook_enabled: Whether to attempt webhook sending
    
    Returns:
        Dict with counts of sent notifications
    """
    result = {"email": 0, "webhook": 0}

    if email_enabled:
        try:
            email_service = EmailNotificationService()
            result["email"] = email_service.send_batch_alerts(alerts)
        except Exception as e:
            logger.error(f"Email service error: {e}")

    if webhook_enabled:
        try:
            webhook_service = WebhookNotificationService()
            max_webhook_alerts = int(os.getenv("SENTRY_MAX_WEBHOOK_ALERTS", "50"))
            alerts_for_webhook = alerts[:max_webhook_alerts] if max_webhook_alerts >= 0 else alerts
            dropped_count = max(0, len(alerts) - len(alerts_for_webhook))
            if dropped_count > 0:
                logger.warning(
                    f"Skipping {dropped_count} webhook alerts due to SENTRY_MAX_WEBHOOK_ALERTS={max_webhook_alerts}"
                )
            result["webhook"] = webhook_service.send_batch_alerts(alerts_for_webhook)
        except Exception as e:
            logger.error(f"Webhook service error: {e}")

    return result
