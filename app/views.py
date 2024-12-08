from flask import render_template, redirect, request, url_for, flash
from app import app, db
from app.models import Setting, User, Department, Project, Message, Chat
from app.forms import ChatForm, LoginForm, DepartmentForm, MessageForm, ProjectForm, RegistrationForm, SettingForm, UserSettingsForm
from flask_login import current_user, login_user, logout_user, login_required

def get_theme_value():
    if current_user.is_authenticated:  # Проверяем, аутентифицирован ли пользователь
        theme_setting = Setting.query.filter_by(user_id=current_user.id, key='theme').first()
        return theme_setting.value == 'dark' if theme_setting else False
    return False  # Если пользователь не аутентифицирован, возвращаем значение по умолчанию

@app.route('/')
def index():
    return render_template('index.html', theme_value=get_theme_value())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        # Получаем пользователя по email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Проверяем, существует ли пользователь и правильный ли пароль
        if user and user.check_password(form.password.data):
            login_user(user)  # Вход пользователя
            flash('Успешный вход!')  # Уведомление об успешном входе
            return redirect(url_for('dashboard'))  # Перенаправление на главную страницу
        
        flash('Неверный email или пароль')  # Уведомление об ошибке входа
    
    return render_template('login.html', form=form, theme_value=get_theme_value())

@app.route('/dashboard')
# @login_required
def dashboard():
    departments = Department.query.all()
    return render_template('dashboard.html', departments=departments, theme_value=get_theme_value())

@app.route('/department/new', methods=['GET', 'POST'])
# @login_required
def new_department():
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department = Department(name=form.name.data,
                                description=form.description.data)
        db.session.add(department)
        db.session.commit()
        flash('Отдел успешно создан!')
        return redirect(url_for('new_department'))
    
    departments = Department.query.all()
    
    return render_template('department.html', form=form, departments=departments, theme_value=get_theme_value())

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm()
    
    # Заполнение списка отделов для выбора в форме проекта.
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        project = Project(title=form.title.data,
            description=form.description.data,
            department_id=form.department_id.data)
        db.session.add(project)
        db.session.commit()
        flash('Проект успешно создан!')
        return redirect(url_for('dashboard'))
    
    projects = Project.query.all()
    
    return render_template('project.html', form=form, projects=projects, theme_value=get_theme_value())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        user = User(name=form.name.data,
                    email=form.email.data,
                    role_id=3)  # Предполагаем, что роль 3 - это обычный пользователь
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()  # Сначала сохраняем пользователя, чтобы получить его ID
        
        # Создаем начальные настройки для нового пользователя
        default_settings = [
            Setting(user_id=user.id, key='theme', value='light'),
            Setting(user_id=user.id, key='notifications_enabled', value='true')
        ]
        
        db.session.bulk_save_objects(default_settings)  # Добавляем настройки в сессию
        db.session.commit()  # Сохраняем изменения в базе данных
        
        flash('Пользователь успешно зарегистрирован!')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form, theme_value=get_theme_value())

@app.route('/users')
@login_required
def users():
    form = RegistrationForm()
    users = User.query.all()
    return render_template('users.html', users=users, form=form, theme_value=get_theme_value())

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = RegistrationForm(obj=user)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.department_id = form.department_id.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Пользователь успешно обновлен!')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', form=form, user=user, theme_value=get_theme_value())

@app.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь успешно удален!')
    return redirect(url_for('users'))

@app.route('/chat/new', methods=['GET', 'POST'])
@login_required
def new_chat():
    form = ChatForm()
    
    # Заполняем список проектов для выбора в форме
    form.project_id.choices = [(p.id, p.title) for p in Project.query.all()]
    
    if form.validate_on_submit():
        chat = Chat(title=form.title.data,
                    description=form.description.data,
                    project_id=form.project_id.data)  # Привязываем чат к проекту
        db.session.add(chat)
        db.session.commit()
        flash('Чат успешно создан!')
        return redirect(url_for('chat_list'))  # Перенаправление на список чатов
    
    return render_template('new_chat.html', form=form, theme_value=get_theme_value())

@app.route('/chats')
@login_required
def chat_list():
    chats = Chat.query.all()
    return render_template('chat_list.html', chats=chats, theme_value=get_theme_value())

@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    form = MessageForm()
    
    if form.validate_on_submit():
        # Создаем новое сообщение
        message = Message(
            text=form.text.data,
            user_id=current_user.id,
            chat_id=chat.id
        )
        
        # Добавляем сообщение в сессию и коммитим изменения
        try:
            db.session.add(message)
            db.session.commit()  # Попытка сохранить изменения в базе данных
            flash('Сообщение отправлено!')
            return redirect(url_for('chat', chat_id=chat.id))
        except Exception as e:
            db.session.rollback()  # Откат изменений в случае ошибки
            flash(f'Ошибка при отправке сообщения: {str(e)}')
    
    # Получаем все сообщения для текущего чата
    messages = Message.query.filter_by(chat_id=chat.id).all()
    
    for message in messages:
        message.sender_name = User.query.get(message.user_id).name
    
    return render_template('chat.html', chat=chat, messages=messages, form=form, theme_value=get_theme_value())

@app.route('/settings/account', methods=['GET', 'POST'])
@login_required
def edit_account():
    form = UserSettingsForm()
    
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        
        if form.password.data:  # Если новый пароль введен
            current_user.set_password(form.password.data)
        
        db.session.commit()  # Сохраняем изменения в базе данных
        flash('Данные аккаунта успешно обновлены!')
        return redirect(url_for('edit_account'))
    
    return render_template('edit_account.html', form=form, theme_value=get_theme_value())

@app.route('/settings/theme', methods=['POST'])
@login_required
def toggle_theme():
    theme_setting = Setting.query.filter_by(user_id=current_user.id, key='theme').first()
    
    if theme_setting is None:
        theme_setting = Setting(user_id=current_user.id, key='theme', value='light')
        db.session.add(theme_setting)

    # Переключаем тему
    if theme_setting.value == 'dark':
        theme_setting.value = 'light'
    else:
        theme_setting.value = 'dark'
    
    db.session.commit()
    flash('Тема успешно изменена!')
    return redirect(url_for('settings'))

@app.route('/settings/notifications', methods=['POST'])
@login_required
def toggle_notifications():
    notifications_setting = Setting.query.filter_by(user_id=current_user.id, key='notifications_enabled').first()
    
    if notifications_setting is None:
        notifications_setting = Setting(user_id=current_user.id, key='notifications_enabled', value='true')
        db.session.add(notifications_setting)

    # Переключаем уведомления
    notifications_setting.value = 'false' if notifications_setting.value == 'true' else 'true'
    
    db.session.commit()
    flash('Настройки уведомлений успешно изменены!')
    return redirect(url_for('settings'))

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    form = UserSettingsForm()

    # Получаем настройки текущего пользователя
    theme_setting = Setting.query.filter_by(user_id=current_user.id, key='theme').first()
    notifications_setting = Setting.query.filter_by(user_id=current_user.id, key='notifications_enabled').first()

    # Устанавливаем значения по умолчанию, если настройки отсутствуют
    if theme_setting is None:
        theme_setting = Setting(user_id=current_user.id, key='theme', value='light')
        db.session.add(theme_setting)

    if notifications_setting is None:
        notifications_setting = Setting(user_id=current_user.id, key='notifications_enabled', value='true')
        db.session.add(notifications_setting)

    db.session.commit()  # Сохраняем новые настройки по умолчанию в базе данных

    return render_template('settings.html', 
                           name=current_user.name,  # Передаем имя пользователя в шаблон
                           form=form,
                           notifications_value=(notifications_setting.value == 'true'), 
                           theme_value=get_theme_value())
    
    
@app.route('/moderator')
@login_required
def moderator():
    return render_template('moderator.html')

# Управление отделами
@app.route('/moderator/departments', methods=['GET', 'POST'])
@login_required
def manage_departments():
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data, description=form.description.data)
        db.session.add(department)
        db.session.commit()
        flash('Отдел успешно добавлен!')
        return redirect(url_for('manage_departments'))
    
    departments = Department.query.all()
    return render_template('manage_departments.html', form=form, departments=departments)

@app.route('/moderator/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        db.session.commit()
        flash('Отдел успешно обновлен!')
        return redirect(url_for('manage_departments'))
    
    return render_template('manage_departments.html', form=form, departments=Department.query.all(), edit_id=id)

@app.route('/moderator/departments/delete/<int:id>', methods=['POST'])
@login_required
def delete_department(id):
    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    flash('Отдел успешно удален!')
    return redirect(url_for('manage_departments'))

# Управление проектами
@app.route('/moderator/projects', methods=['GET', 'POST'])
@login_required
def manage_projects():
    form = ProjectForm()
    form.department_id.choices = [(p.id, p.name) for p in Department.query.all()]
    
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data, department_id=form.department_id.data)
        db.session.add(project)
        db.session.commit()
        flash('Проект успешно добавлен!')
        return redirect(url_for('manage_projects'))
    
    projects = Project.query.all()
    return render_template('manage_projects.html', form=form, projects=projects)

@app.route('/moderator/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    form.department_id.choices = [(p.id, p.name) for p in Department.query.all()]
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.department_id = form.department_id.data
        db.session.commit()
        flash('Проект успешно обновлен!')
        return redirect(url_for('manage_projects'))
    
    return render_template('manage_projects.html', form=form, projects=Project.query.all(), edit_id=id)

@app.route('/moderator/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Проект успешно удален!')
    return redirect(url_for('manage_projects'))

# Управление чатами
@app.route('/moderator/chats', methods=['GET', 'POST'])
@login_required
def manage_chats():
    form = ChatForm()
    form.project_id.choices = [(p.id, p.title) for p in Project.query.all()]

    
    if form.validate_on_submit():
        chat = Chat(title=form.title.data, description=form.description.data, project_id=form.project_id.data)
        db.session.add(chat)
        db.session.commit()
        flash('Чат успешно добавлен!')
        return redirect(url_for('manage_chats'))
    
    chats = Chat.query.all()
    return render_template('manage_chats.html', form=form, chats=chats)

@app.route('/moderator/chats/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_chat(id):
    chat = Chat.query.get_or_404(id)
    form = ChatForm(obj=chat)
    form.project_id.choices = [(p.id, p.title) for p in Project.query.all()]
    
    if form.validate_on_submit():
        chat.title = form.title.data
        chat.description = form.description.data
        chat.project_id = form.project_id.data
        db.session.commit()
        flash('Чат успешно обновлен!')
        return redirect(url_for('manage_chats'))
    
    return render_template('manage_chats.html', form=form, chats=Chat.query.all(), edit_id=id)

@app.route('/moderator/chats/delete/<int:id>', methods=['POST'])
@login_required
def delete_chat(id):
    chat = Chat.query.get_or_404(id)
    db.session.delete(chat)
    db.session.commit()
    flash('Чат успешно удален!')
    return redirect(url_for('manage_chats'))

@app.route('/moderator/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    form = SettingForm()
    if form.validate_on_submit():
        setting = Setting(key=form.key.data, value=form.value.data)
        db.session.add(setting)
        db.session.commit()
        flash('Настройка успешно добавлена!')
        return redirect(url_for('manage_settings'))
    
    settings = Setting.query.all()
    return render_template('manage_settings.html', form=form, settings=settings)

@app.route('/moderator/settings/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_setting(id):
    setting = Setting.query.get_or_404(id)
    form = SettingForm(obj=setting)
    if form.validate_on_submit():
        setting.key = form.key.data
        setting.value = form.value.data
        db.session.commit()
        flash('Настройка успешно обновлена!')
        return redirect(url_for('manage_settings'))
    
    return render_template('edit_setting.html', form=form)

@app.route('/moderator/settings/delete/<int:id>', methods=['POST'])
@login_required
def delete_setting(id):
    setting = Setting.query.get_or_404(id)
    db.session.delete(setting)
    db.session.commit()
    flash('Настройка успешно удалена!')
    return redirect(url_for('manage_settings'))