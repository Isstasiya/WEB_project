from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash


class BuyerForm(FlaskForm):
    region = StringField('Region', validators=[DataRequired()])
    submit = SubmitField('Submit')