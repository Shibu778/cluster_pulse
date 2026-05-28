import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(config, subject, body_content):
    email_config = config['notifications']['email']
    
    msg = MIMEMultipart()
    msg['From'] = email_config['sender']
    msg['To'] = email_config['receiver']
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body_content, 'plain'))
    
    try:
        # Establish secure connection
        server = smtplib.SMTP(email_config['smtp_server'], email_config['port'])
        server.starttls() 
        server.login(email_config['sender'], email_config['password'])
        
        server.sendmail(email_config['sender'], email_config['receiver'], msg.as_string())
        server.quit()
        print("📊 Notification sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")