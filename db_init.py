from app import create_app
from models import db

app = create_app()

print("→ Using database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    db.create_all()
    print("Database created.")