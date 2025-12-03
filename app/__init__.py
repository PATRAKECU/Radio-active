import secrets
from flask import Flask

# Create the Flask app instance
app = Flask(__name__)
# Generate a secure secret key
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Import route definitions
from app import routes
