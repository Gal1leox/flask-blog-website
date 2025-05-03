from mailjet_rest import Client

from website.config import Config


class MailjetService:
    def __init__(self):
        self.client = Client(
            auth=(Config.MAILJET_API_KEY, Config.MAILJET_API_SECRET), version="v3.1"
        )

    def send_email(self, to: str, subject: str, html_body: str):
        data = {
            "Messages": [
                {
                    "From": {"Email": Config.ADMIN_EMAIL},
                    "To": [{"Email": to}],
                    "Subject": subject,
                    "HTMLPart": html_body,
                }
            ]
        }
        return self.client.send.create(data=data)
