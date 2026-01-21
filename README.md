# E-RAIL SENTRY Email Gateway

Production-ready Flask application for sending emails via HTTP API.

## Quick Start

### 1. Setup Gmail App Password

1. Go to Google Account Settings
2. Security → 2-Step Verification
3. App Passwords → Generate new password
4. Copy the 16-character password

### 2. Configure Environment
```bash
cp .env.example .env
nano .env
```

Update these values:
- `API_KEY`: Generate a secure random key
- `SMTP_USER`: Your Gmail address
- `SMTP_PASSWORD`: Gmail app password (16 chars)

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test Locally
```bash
python flask_app.py
```

## API Usage

### Send Email

**Endpoint:** `POST /send-email`

**Request:**
```json
{
  "api_key": "your-api-key",
  "to": "recipient@example.com",
  "subject": "Test Email",
  "body": "This is a test email",
  "from_name": "E-RAIL SENTRY"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Email sent successfully",
  "timestamp": "2024-01-17T14:30:25Z",
  "recipient": "recipient@example.com"
}
```

## Security

- API key authentication required
- Rate limiting: 100 emails/hour
- Input validation
- HTTPS enforced (on PythonAnywhere)

## Monitoring

View logs:
```bash
tail -f email_gateway.log
```

Check stats:
```bash
curl -X POST https://yourusername.pythonanywhere.com/stats \
  -H "Content-Type: application/json" \
  -d '{"api_key":"your-key"}'
```