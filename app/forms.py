from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
    
class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    department_id = SelectField('Отдел', coerce=int)  # Заполнить позже в представлении
    submit = SubmitField('Зарегистрироваться')

class DepartmentForm(FlaskForm):
    name = StringField('Название отдела', validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Создать отдел')

class ProjectForm(FlaskForm):
    title = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Описание')
    department_id = SelectField('Отдел', coerce=int)  # Заполнить позже в представлении
    submit = SubmitField('Создать проект')

class ChatForm(FlaskForm):
    title = StringField('Название чата', validators=[DataRequired()])
    description = TextAreaField('Описание чата')
    project_id = SelectField('Выберите проект', coerce=int)  # Добавляем выбор проекта
    submit = SubmitField('Создать чат')

class MessageForm(FlaskForm):
    text = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить сообщение')

class UserSettingsForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Новый пароль (оставьте пустым, если не хотите менять)')
    submit = SubmitField('Сохранить настройки')
    
class SettingForm(FlaskForm):
    key = StringField('Ключ настройки', validators=[DataRequired()])
    value = StringField('Значение настройки', validators=[DataRequired()])
    submit = SubmitField('Добавить настройку')