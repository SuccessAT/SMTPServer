"""
Email sending functionality
Handles SMTP connection and email delivery
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config


class EmailSender:
    """Email sending service"""
    
    def __init__(self):
        self.stats = {
            'total_sent': 0,
            'total_failed': 0,
            'last_sent': None
        }
    
    def is_configured(self):
        """Check if SMTP is properly configured"""
        return bool(Config.SMTP_USER and Config.SMTP_PASSWORD)
    
    def send(self, to_email, subject, body, from_name='E-RAIL SENTRY'):
        """
        Send email via SMTP
        
        Args:
            to_email (str): Recipient email
            subject (str): Email subject
            body (str): Email body (plain text)
            from_name (str): Sender name
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validate configuration
            if not self.is_configured():
                return False, 'SMTP not configured'
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = '{} <{}>'.format(from_name, Config.SMTP_FROM)
            msg['To'] = to_email
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            # Add plain text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Optional: Add HTML version
            html_body = body.replace('\n', '<br>')
            html_part = MIMEText(
                '<html><body><pre>{}</pre></body></html>'.format(html_body),
                'html'
            )
            msg.attach(html_part)
            
            # Connect to SMTP server
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
            server.ehlo()
            
            if Config.SMTP_USE_TLS:
                server.starttls()
                server.ehlo()
            
            # Login
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            # Update stats
            self.stats['total_sent'] += 1
            self.stats['last_sent'] = datetime.utcnow().isoformat()
            
            return True, 'Email sent successfully'
        
        except smtplib.SMTPAuthenticationError:
            self.stats['total_failed'] += 1
            return False, 'SMTP authentication failed'
        
        except smtplib.SMTPException as e:
            self.stats['total_failed'] += 1
            return False, 'SMTP error: {}'.format(str(e))
        
        except Exception as e:
            self.stats['total_failed'] += 1
            return False, 'Unexpected error: {}'.format(str(e))
    
    def get_stats(self):
        """Get email sending statistics"""
        return self.stats