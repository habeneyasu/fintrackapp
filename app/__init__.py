
def create_app():
    app = Flask(__name__)
    
    # Lazy import to prevent circular imports
    from app.core.config import settings
    app.config.from_mapping(
        SECRET_KEY=settings.SECRET_KEY.get_secret_value(),
        SQLALCHEMY_DATABASE_URI=settings.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize extensions
    from app.core.database import db
    db.init_app(app)
    
    return app