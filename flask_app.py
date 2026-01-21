"""
E-RAIL SENTRY Email Gateway
Production-ready Flask application for sending emails via HTTP API
"""

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
from functools import wraps

# Import custom modules
from config import Config
from email_sender import EmailSender
from logger_config import setup_logger

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup logger
logger = setup_logger()

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use Redis in production: redis://localhost:6379
)

# Initialize email sender
email_sender = EmailSender()


# ============================================================================
# Authentication Decorator
# ============================================================================

def require_api_key(f):
    """Decorator to validate API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.json.get('api_key') if request.json else None

        if not api_key:
            logger.warning('Missing API key in request from {}'.format(
                request.remote_addr))
            return jsonify({
                'status': 'error',
                'message': 'API key required',
                'error_code': 401
            }), 401

        if api_key != Config.API_KEY:
            logger.warning('Invalid API key attempt from {}'.format(
                request.remote_addr))
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key',
                'error_code': 403
            }), 403

        return f(*args, **kwargs)

    return decorated_function


# ============================================================================
# API Routes
# ============================================================================

@app.route('/')
def home():
    """Home page with API documentation"""
    return jsonify({
        'service': 'E-RAIL SENTRY Email Gateway',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            '/health': 'Health check',
            '/send-email': 'Send email (POST)',
            '/stats': 'API statistics'
        },
        'documentation': 'POST to /send-email with JSON body'
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'service': 'email-gateway',
        'smtp_configured': email_sender.is_configured()
    })


@app.route('/send-email', methods=['POST'])
@limiter.limit("100 per hour")  # Per-route rate limit
@require_api_key
def send_email():
    """
    Send email endpoint

    Expected JSON:
    {
        "api_key": "your-secret-key",
        "to": "recipient@example.com",
        "subject": "Email Subject",
        "body": "Email body text",
        "from_name": "Sender Name (optional)"
    }
    """
    try:
        # Validate request
        if not request.json:
            return jsonify({
                'status': 'error',
                'message': 'JSON body required',
                'error_code': 400
            }), 400

        # Extract data
        data = request.json
        to_email = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        from_name = data.get('from_name', 'E-RAIL SENTRY')

        # Validate required fields
        if not all([to_email, subject, body]):
            missing = []
            if not to_email: missing.append('to')
            if not subject: missing.append('subject')
            if not body: missing.append('body')

            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: {}'.format(', '.join(missing)),
                'error_code': 400
            }), 400

        # Validate email format
        if '@' not in to_email or '.' not in to_email:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email format',
                'error_code': 400
            }), 400

        # Length validation
        if len(subject) > 200:
            return jsonify({
                'status': 'error',
                'message': 'Subject too long (max 200 characters)',
                'error_code': 400
            }), 400

        if len(body) > 10000:
            return jsonify({
                'status': 'error',
                'message': 'Body too long (max 10000 characters)',
                'error_code': 400
            }), 400

        # Send email
        logger.info('Sending email to {} from {}'.format(to_email, request.remote_addr))

        success, message = email_sender.send(
            to_email=to_email,
            subject=subject,
            body=body,
            from_name=from_name
        )

        if success:
            logger.info('Email sent successfully to {}'.format(to_email))
            return jsonify({
                'status': 'success',
                'message': 'Email sent successfully',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'recipient': to_email
            }), 200
        else:
            logger.error('Failed to send email to {}: {}'.format(to_email, message))
            return jsonify({
                'status': 'error',
                'message': 'Failed to send email: {}'.format(message),
                'error_code': 500
            }), 500

    except Exception as e:
        logger.error('Unexpected error in send_email: {}'.format(str(e)))
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'error_code': 500
        }), 500


@app.route('/stats')
@require_api_key
def stats():
    """Get API statistics"""
    return jsonify({
        'status': 'success',
        'stats': email_sender.get_stats(),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    logger.warning('Rate limit exceeded from {}'.format(request.remote_addr))
    return jsonify({
        'status': 'error',
        'message': 'Rate limit exceeded. Try again later.',
        'error_code': 429
    }), 429


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'error_code': 404
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error('Internal server error: {}'.format(str(e)))
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error_code': 500
    }), 500


# ============================================================================
# Run Application
# ============================================================================

if __name__ == '__main__':
    # This is for local testing only
    # PythonAnywhere uses WSGI
    app.run(debug=False, host='0.0.0.0', port=5000)
