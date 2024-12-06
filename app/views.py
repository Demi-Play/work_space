from flask import render_template, redirect, url_for, flash
from app import app, db
from app.models import User, Department, Project, Message, Chat
from app.forms import LoginForm, DepartmentForm, ProjectForm, RegistrationForm
from flask_login import login_user, logout_user, login_required

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # Проверка пароля (должен быть хэширован!)
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Неверный email или пароль')
    
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    departments = Department.query.all()
    return render_template('dashboard.html', departments=departments)

@app.route('/department/new', methods=['GET', 'POST'])
@login_required
def new_department():
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department = Department(name=form.name.data,
                                description=form.description.data)
        db.session.add(department)
        db.session.commit()
        flash('Отдел успешно создан!')
        return redirect(url_for('dashboard'))
    
    return render_template('department.html', form=form)

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
    
    return render_template('project.html', form=form)

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
                    department_id=form.department_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь успешно зарегистрирован!')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

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
    
    return render_template('edit_user.html', form=form, user=user)

@app.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь успешно удален!')
    return redirect(url_for('users'))