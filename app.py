import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-dtf-app")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_path = os.path.join(os.getcwd(), "tasas.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Import and schedule DTF data collection
    from dtf_collector import collect_dtf_data
    
    # Schedule daily collection at 9:00 AM
    scheduler.add_job(
        func=collect_dtf_data,
        trigger="cron",
        hour=9,
        minute=0,
        id='dtf_daily_collection',
        name='Collect DTF data daily',
        replace_existing=True
    )
    
    # Also run immediately on startup if no data exists
    from models import TasaDTF
    if TasaDTF.query.count() == 0:
        logger.info("No DTF data found, collecting initial data...")
        collect_dtf_data()

# Start scheduler
if not scheduler.running:
    scheduler.start()
    logger.info("DTF data collection scheduler started")

# Shut down scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Import routes
from routes import *
