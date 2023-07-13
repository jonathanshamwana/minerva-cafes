from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from forms import AddForm, SignupForm, LoginForm, ReviewForm
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import flash
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

bootstrap = Bootstrap(app)
login_manager = LoginManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

my_api_key = os.getenv("API_KEY")


gravatar = Gravatar(app,
                    size=50,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    map_url = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.Text, nullable=False)
    coffee_price = db.Column(db.Text, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(500), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'), nullable=False)
    cafe = db.relationship('Cafe', backref=db.backref('comments', lazy=True))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    cafes_per_page = 12
    cafes = Cafe.query.paginate(page=page, per_page=cafes_per_page)
    return render_template("index.html", cafes=cafes, current_user=current_user)

@app.route("/add", methods=["Post", "GET"])
def add_cafe():
    form = AddForm()

    if form.validate_on_submit():

        sockets = True if form.has_sockets.data == "Yes" else False
        toilet = True if form.has_toilet.data == "Yes" else False
        wifi = True if form.has_wifi.data == "Yes" else False
        calls = True if form.can_take_calls.data == "Yes" else False

        new_cafe = Cafe(
            name=form.name.data.title(),
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data.title(),
            has_sockets=sockets,
            has_toilet=toilet,
            has_wifi=wifi,
            can_take_calls=calls,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add.html", form=form)

@app.route("/cafe/<int:id>", methods=["GET", "POST"])
def show_cafe(id):
    cafe = Cafe.query.get(id)
    form = ReviewForm()

    if current_user.is_authenticated and form.validate_on_submit():
        new_comment = Comment(
            comment=form.review.data,
            cafe_id=id,
            author_id=current_user.id,
        )

        db.session.add(new_comment)
        db.session.commit()

        flash("Comment added successfully!", "success")
        return redirect(url_for('show_cafe', id=cafe.id))

    elif form.validate_on_submit() and not current_user.is_authenticated:
        flash("Error: You must be logged in to leave a comment", "error")
        # return redirect(url_for('show_cafe', id=cafe.id))

    return render_template("cafedetails.html", cafe=cafe, form=form, cform=form)

@app.route("/search", methods=["GET"])
def search_cafes():
    location = request.args.get("location").title()
    cafes = Cafe.query.filter_by(location=location).all()
    return render_template("search.html", cafes=cafes, location=location)

@app.route("/signup", methods=["GET", "POST"])
def create_account():
    form = SignupForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home'))

    return render_template("signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def user_login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password_attempt = form.password.data

        user = User.query.filter_by(email=email).first()
        if check_password_hash(pwhash=user.password, password=password_attempt):
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form)

@app.route("/logout")
def log_out():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)