from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

class AddForm(FlaskForm):
    name = StringField("Cafe name", validators=[DataRequired()])
    map_url = StringField("Map URL", validators=[DataRequired(), URL()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    location = StringField("Location", validators=[DataRequired()])
    has_sockets = SelectField("Sockets", choices=["Yes", "No"], validators=[DataRequired()])
    has_toilet = SelectField("Toilet", choices=["Yes", "No"], validators=[DataRequired()])
    has_wifi = SelectField("Wifi", choices=["Yes", "No"], validators=[DataRequired()])
    can_take_calls = SelectField("Take Calls", choices=["Yes", "No"], validators=[DataRequired()])
    seats = StringField("No. of seats", validators=[DataRequired()])
    coffee_price = StringField("Coffee Price", validators=[DataRequired()])
    submit = SubmitField('Submit')

class SignupForm(FlaskForm):
    name = StringField("First name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")

class ReviewForm(FlaskForm):
    review = CKEditorField("Leave a review", validators=[DataRequired()])
    submit = SubmitField("Submit")
