from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, IntegerField, StringField, FileField, FloatField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    book = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    weight = FloatField('Weight', validators=[DataRequired()])
    genre = StringField('Genres', validators=[DataRequired()])
    sub = SubmitField('Submit')