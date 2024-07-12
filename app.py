from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes import routes
from flask_cors import CORS
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load configuration from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
from models import db  # Import db after app initialization
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints
app.register_blueprint(routes)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)