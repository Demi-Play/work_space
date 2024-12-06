from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin.contrib.sqla import ModelView
from app.config import Config
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='./static', template_folder='./templates')
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
csrf = CSRFProtect(app)
csrf.init_app(app)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
from app import views, models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


# Создание базы данных и миграций (выполняется в терминале)
# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade