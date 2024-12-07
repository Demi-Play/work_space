from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin.contrib.sqla import ModelView
from app.config import Config
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin
from werkzeug.security import generate_password_hash

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

admin = Admin(app, name='Панель админа', template_mode='bootstrap3')

# Класс для администраторов
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin  # Проверка на администратора

    column_list = ('id', 'name', 'email', 'role_id', 'department_id', 'registered_on')
    form_columns = ('name', 'email', 'password', 'role_id', 'department_id', 'registered_on')

# Класс для ролей
class RoleModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin  # Проверка на администратора

    column_list = ('id', 'name')
    form_columns = ('name',)

# Добавляем модели для администраторов
admin.add_view(AdminModelView(models.User, db.session))
admin.add_view(RoleModelView(models.Role, db.session))
admin.add_view(ModelView(models.Project, db.session)) 
admin.add_view(ModelView(models.Chat, db.session))
admin.add_view(ModelView(models.Setting, db.session))


# Обратите внимание: сообщения не добавляются ни в один из классов,
# так как они недоступны для администраторов и модераторов.

# Создание базы данных и миграций (выполняется в терминале)
# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade