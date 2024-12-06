from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
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