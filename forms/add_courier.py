from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash


class CourierForm(FlaskForm):
    courier_type = StringField('Courier Type(bike, foot, car)', validators=[DataRequired()])
    time = StringField("Time format: 'hh:mm-hh:mm hh:mm-hh:mm'", validators=[DataRequired()])
    regions = StringField("Regions format: 'region region'", validators=[DataRequired()])
    submit = SubmitField('Submit')