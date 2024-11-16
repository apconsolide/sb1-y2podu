from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import os
from pathlib import Path

class EmailSender:
    def __init__(self):
        self.email = os.getenv('GMAIL_EMAIL')
        self.password = os.getenv('GMAIL_APP_PASSWORD')
        self.cv_templates_dir = Path('cv_templates')

    def send_cv(self, recipient_email: str, cv_type: str) -> bool:
        """Send CV template to user's email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient_email
            msg['Subject'] = f"Your {cv_type.capitalize()} CV Template from CV_UP"

            body = f"""
            Thank you for using CV_UP!

            Please find attached your {cv_type} CV template.

            Best regards,
            CV_UP Team
            """
            msg.attach(MIMEText(body, 'plain'))

            # Attach CV file
            cv_path = self.cv_templates_dir / f"{cv_type.lower()}_template.docx"
            with open(cv_path, 'rb') as f:
                cv_attachment = MIMEApplication(f.read(), _subtype="docx")
                cv_attachment.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=f'cv_template_{cv_type.lower()}.docx'
                )
                msg.attach(cv_attachment)

            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False