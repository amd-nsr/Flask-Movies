from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, EqualTo, Length
from wtforms_components import IntegerField

from datetime import datetime

#from wtforms import PasswordField, validators

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])

class MovieEditForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    year = IntegerField("Year",
                                validators=[Optional(),
                                NumberRange(min=1887, max=datetime.now().year),
                                ],)

class RegistrationForm(FlaskForm):
    username = StringField('Username', [Length(min=4, max=20)])
    email = StringField('Email Address', [Length(min=6, max=50)])
    password = PasswordField('Password',
            [
            DataRequired(message="Please enter a password."),
            ]
        )
    confirm = PasswordField('Repeat Password',
            [
            EqualTo('password', message='Passwords must match.'),
            ]
        )
    
