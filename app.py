from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager

login = LoginManager()
login.login_view = 'main.login'

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)
    login.init_app(app)

    from routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)