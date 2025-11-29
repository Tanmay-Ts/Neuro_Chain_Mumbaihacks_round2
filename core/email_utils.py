import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_alert_email(to_email, company_name, post_url, claim, verdict, explanation, pr_response):
    sender = getattr(config, 'EMAIL_SENDER', '')
    password = getattr(config, 'EMAIL_PASSWORD', '').replace(" ", "")
    
    if not sender or "your_email" in sender:
        print(f"⚠️ Email not configured. Simulated send to {to_email}")
        return False

    subject = f"🚨 NeuroChain Alert: {verdict} Claim Detected for {company_name}"
    
    body = f"""
    <html><body>
        <h2>NeuroChain Intelligence Report</h2>
        <p><strong>Company:</strong> {company_name}</p>
        <p><strong>Detected Post:</strong> <a href="{post_url}">{post_url}</a></p>
        <hr>
        <h3>Analysis</h3>
        <ul>
            <li><strong>Claim:</strong> {claim}</li>
            <li><strong>Verdict:</strong> <span style="color: red;">{verdict}</span></li>
        </ul>
        <p><strong>Explanation:</strong><br>{explanation}</p>
        <hr>
        <h3>Recommended Response</h3>
        <p style="background-color: #f0f0f0; padding: 10px;">{pr_response}</p>
    </body></html>
    """

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
        print(f"📧 Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False