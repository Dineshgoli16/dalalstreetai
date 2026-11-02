"""cPanel Phusion Passenger WSGI entry point for Dalal Street AI.

Converts FastAPI ASGI application into a WSGI callable using a2wsgi for
seamless hosting under CloudLinux / cPanel 'Setup Python App'.
"""

import sys
import os

# Ensure the application root directory is first on the Python module search path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    env_path = os.path.join(APP_DIR, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
except Exception as e:
    sys.stderr.write(f"Warning: Failed to load .env file: {e}\n")

# Import FastAPI instance and wrap with a2wsgi
try:
    from a2wsgi import ASGIMiddleware
    from server import app

    # Phusion Passenger requires a WSGI callable named 'application'
    application = ASGIMiddleware(app)

except Exception as err:
    import traceback
    error_traceback = traceback.format_exc()
    sys.stderr.write(f"Fatal Startup Error in passenger_wsgi.py:\n{error_traceback}\n")

    # Fallback WSGI application displaying diagnosis message in browser
    def application(environ, start_response):
        status = '500 Internal Server Error'
        output = (
            f"Dalal Street AI - cPanel Startup Error\n\n"
            f"Error details:\n{error_traceback}\n\n"
            f"Check your virtualenv, requirements.txt, and .env configuration."
        ).encode('utf-8')
        response_headers = [
            ('Content-type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output]
