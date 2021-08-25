from datetime import datetime
from movie import Movie
from flask import current_app, render_template, request, redirect, url_for, abort, flash, session
from forms import MovieEditForm, LoginForm, RegistrationForm
from user import get_user
from flask_login import login_user, logout_user, login_required, current_user
from passlib.hash import sha256_crypt as hasher
from database import connect
from MySQLdb import escape_string as thwart
import gc

def home_page():
    today = datetime.today()
    day_name = today.strftime("%A")
    return render_template("home.html", day=day_name)

def movies_page():
    db = current_app.config["db"]
    if request.method == "GET":
        movies = db.get_movies()
        return render_template("movies.html", movies=sorted(movies))
    else:
        form_movie_keys = request.form.getlist("movie_keys")
        for form_movie_key in form_movie_keys:
            db.delete_movie(int(form_movie_key))
        return redirect(url_for("movies_page"))

def movie_page(movie_key):
    db = current_app.config["db"]
    if request.method == "GET":
        movie = db.get_movie(movie_key)
        return render_template("movie.html", movie=movie)
    else:
        if not current_user.is_admin:
            abort(401)
        form_movie_keys = request.form.getlist("movie_keys")
        for form_movie_key in form_movie_keys:
            db.delete_movie(int(form_movie_key))
        flash("%(num)d movies deleted." % {"num": len(form_movie_keys)})
        return redirect(url_for("movies_page"))
        
@login_required
def movie_add_page():
    if not current_user.is_admin:
        abort(401)
    form = MovieEditForm()
    if form.validate_on_submit():
        title = form.data["title"]
        year = form.data["year"]
        movie = Movie(title, year=year)
        db = current_app.config["db"]
        movie_key = db.add_movie(movie)
        flash("Movie added.")
        return redirect(url_for("movie_page", movie_key=movie_key))
    return render_template("movie_edit.html", form=form)

@login_required
def movie_edit_page(movie_key):
    db = current_app.config["db"]
    movie = db.get_movie(movie_key)
    form = MovieEditForm()
    if form.validate_on_submit():
        title = form.data["title"]
        year = form.data["year"]
        movie = Movie(title, year=year)
        db.update_movie(movie_key, movie)
        flash("Movie data updated.")
        return redirect(url_for("movie_page", movie_key=movie_key))
    form.title.data = movie.title
    form.year.data = movie.year if movie.year else ""
    return render_template("movie_edit.html", form=form)

def validate_movie_form(form):
    form.data = {}
    form.errors = {}

    form_title = form.get("title", "").strip()
    if len(form_title) == 0:
        form.errors["title"] = "Title can not be blank."
    else:
        form.data["title"] = form_title

    form_year = form.get("year")
    if not form_year:
        form.data["year"] = None
    elif not form_year.isdigit():
        form.errors["year"] = "Year must consist of digits only."
    else:
        year = int(form_year)
        if (year < 1887) or (year > datetime.now().year):
            form.errors["year"] = "Year not in valid range."
        else:
            form.data["year"] = year

    return len(form.errors) == 0

def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.data["username"]
        user = get_user(username)
        if user is not None:
            password = form.data["password"]
            if hasher.verify(password, user.password):
                login_user(user)
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
        flash("Invalid credentials.")
    return render_template("login.html", form=form)


def logout_page():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home_page"))


def register_page():
    #try:
    form = RegistrationForm(request.form)

    if request.method == "POST" and form.validate_on_submit():
        username  = form.username.data
        email = form.email.data
        password = hasher.encrypt((str(form.password.data)))
        c, conn = connect()

        query = "SELECT * FROM USER WHERE USERNAME = %s"
        x = c.execute(query, (thwart(username),))

        if int(x) > 0:
            flash("That username is already taken, please choose another")
            return render_template('register.html', form=form)

        else:
            query = "INSERT INTO USER (username, email, password) VALUES (%s, %s, %s)"
            c.execute(query, (thwart(username), thwart(email), thwart(password),))
                
            conn.commit()
            flash("Thanks for registering!")
            c.close()
            conn.close()
            gc.collect()

            session['logged_in'] = True
            session['username'] = username
            
            user = get_user(username)
            if user is not None:
                password = form.data["password"]
                if hasher.verify(password, user.password):
                    login_user(user)
                    flash("You have logged in.")
                    next_page = request.args.get("next", url_for("home_page"))
                    return redirect(next_page)
            #return redirect(url_for('home_page'))
    return render_template("register.html", form=form)

    #except Exception as e:
        #return(str(e))
		