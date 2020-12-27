from flask import Flask, render_template, request, url_for, redirect, session, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
import MySQLdb
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = 'Thisismysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///hackathonproj.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def loader(user_id):
    return User.query.get(int(user_id))

# User class/table


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    name = db.Column(db.String(50))
    bio = db.Column(db.String(75))
    location = db.Column(db.String(40))
    phone_number = db.Column(db.String(40))
    posts = db.relationship('Post', backref='user')
    comments = db.relationship('Comment', backref='user')

# Post class/table


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    description = db.Column(db.String(1000))
    author = db.Column(db.String(20))
    location = db.Column(db.String(50))
    comments = db.relationship('Comment', backref='post')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Comment class/table


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(20))
    text = db.Column(db.String(100))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# LoginForm


class LoginForm(FlaskForm):
    username = StringField('', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('', validators=[
                             InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('')

# RegisterForm


class RegisterForm(FlaskForm):
    email = StringField('', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('', validators=[
                             InputRequired(), Length(min=4, max=80)])

# Editprofile form


class EditProfile(FlaskForm):
    email = StringField('', validators=[Length(min=0, max=50)])
    name = StringField('', validators=[Length(min=0, max=50)])
    username = StringField('', validators=[Length(min=0, max=15)])
    password = PasswordField('', validators=[Length(min=0, max=80)])
    location = StringField('', validators=[Length(
        min=0, max=40)])
    bio = StringField('', validators=[Length(min=0, max=75)])
    phone_number = StringField('', validators=[
        Length(min=0, max=40)])
    password = PasswordField('', validators=[Length(min=0, max=80)])

# Posts form


class PostForm(FlaskForm):
    title = StringField('', validators=[Length(
        min=4, max=30)])
    description = StringField('', validators=[Length(min=4, max=1000)])
    author = StringField('', validators=[Length(min=0, max=200)])
    location = StringField('', validators=[Length(min=4, max=20)])

# Createcomments form


class CreateComment(FlaskForm):
    text = StringField('', validators=[InputRequired(), Length(max=100)])
    author = StringField('', validators=[
        InputRequired(), Length(max=20)])

# search posts form


class SearchForm(FlaskForm):
    words = StringField('', validators=[Length(max=50)])

# Index route (main page)


@ app.route('/')
def index():
    return render_template('index.html', current_user=current_user)

# profile route


@ app.route('/profile', methods=['GET', 'POST'])
@ login_required
def profile():
    return render_template("profile.html", current_user=current_user)


@ app.route('/profile/yourposts')
@login_required
def userposts():
    results = db.engine.execute("SELECT * FROM post")
    posts = [dict(ID=row[0],
                  Title=row[1],
                  Description=row[2],
                  Author=row[3],
                  Location=row[4],
                  user_id=row[5]) for row in results.fetchall()]
    user_results = db.engine.execute(
        f"SELECT * FROM post WHERE user_id={current_user.id}")
    user_posts = [dict(ID=row[0],
                       Title=row[1],
                       Description=row[2],
                       Author=row[3],
                       Location=row[4],
                       user_id=row[5]) for row in user_results.fetchall()]
    return render_template("viewposts.html", posts=posts, current_user=current_user, len=len(user_posts))

# Editrprofile route


@ app.route('/profile/edit', methods=['GET', 'POST'])
@ login_required
def editprofile():
    form = EditProfile()
    # check if form is all good
    if form.validate_on_submit():
        update_userinfo = User.query.filter_by(id=current_user.id).first()
        if len(form.username.data) > 0:
            update_userinfo.username = form.username.data
        else:
            update_userinfo.username = current_user.username
        if len(form.password.data) > 0:
            update_userinfo.password = new_hashed_pwd = generate_password_hash(
                form.password.data, method='sha256')
        else:
            update_userinfo.password = current_user.password
        if len(form.name.data) > 0:
            update_userinfo.name = form.name.data
        else:
            update_userinfo.name = current_user.name
        if len(form.email.data) > 0:
            update_userinfo.email = form.email.data
        else:
            update_userinfo.email = current_user.email
        if len(form.location.data) > 0:
            update_userinfo.location = form.location.data
        else:
            update_userinfo.location = current_user.location
        if len(form.phone_number.data) > 0:
            update_userinfo.phone_number = form.phone_number.data
        else:
            update_userinfo.phone_number = current_user.phone_number
        if len(form.bio.data) > 0:
            update_userinfo.bio = form.bio.data
        else:
            update_userinfo.bio = current_user.bio
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('editprofile.html', form=form)

# signup route


@ app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        try:
            new_user = User(username=form.username.data,
                            email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
        except IntegrityError:
            db.session.rollback()
            return render_template('integrityerror.html')
        return redirect(url_for("profile"))

    return render_template('sign-up.html', form=form, current_user=current_user)

# login route


@ app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('profile'))
    return render_template('login.html', form=form, current_user=current_user)

# createpost route


@ app.route('/createpost', methods=['GET', 'POST'])
@ login_required
def createpost():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(title=form.title.data, description=form.description.data,
                        author=form.author.data, location=form.location.data, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    return render_template('createpost.html', form=form)


@ app.route('/deletepost/<postid>', methods=['GET', 'POST'])
@login_required
def deletepost(postid):
    db.engine.execute(f"DELETE FROM post WHERE id={postid}")
    return redirect('/posts')
    # all the posts route


@ app.route('/posts', methods=['GET', 'POST'])
def posts():
    form = SearchForm()
    if request.method == 'POST' and form.words.data:
        search = form.words.data
        search.split()
        search.join('+')
        return redirect(f"/searchposts?s={search}")
    results = db.engine.execute("SELECT * FROM post")
    comments_results = db.engine.execute("SELECT * FROM comment")
    posts = [dict(ID=row[0],
                  Title=row[1],
                  Description=row[2],
                  Author=row[3],
                  Location=row[4],
                  User_id=row[5]) for row in results.fetchall()]
    comments = [dict(ID=row[0],
                     Author=row[1],
                     Text=row[2],
                     post_id=row[3],
                     user_id=row[4]) for row in comments_results.fetchall()]

    return render_template('posts.html', posts=posts, comments=comments, form=form, length_comments=len(comments), length_posts=len(posts), current_user=current_user)

# searchposts route


@ app.route('/searchposts', methods=['GET', 'POST'])
def searchposts():
    form = SearchForm()
    search_words = request.args['s']
    if request.method == 'POST':
        if search_words == '':
            return redirect("/posts")
        search = form.words.data
        search.split()
        search.join('+')
        return redirect(f"/searchposts?s={search}")
    results = db.engine.execute("SELECT * FROM post")
    comments_results = db.engine.execute("SELECT * FROM comment")
    posts = [dict(ID=row[0],
                  Title=row[1],
                  Description=row[2],
                  Author=row[3],
                  Location=row[4]) for row in results.fetchall()]
    comments = [dict(ID=row[0],
                     Author=row[1],
                     Text=row[2],
                     post_id=row[3],
                     user_id=row[4]) for row in comments_results.fetchall()]
    search_words_list = search_words.split()
    return render_template("searchposts.html", search_words=search_words, posts=posts, form=form, search_words_list=search_words_list, comments=comments, length_comments=len(comments), length_searchwordslist=len(search_words_list))


@app.route('/deletecomment/<commentid>', methods=['GET', 'POST'])
def deletecomment(commentid):
    db.engine.execute(f"DELETE FROM comment WHERE id={commentid}")
    return redirect('/posts')

# createcomment route


@ app.route('/createcomment/<postid>', methods=['GET', 'POST'])
@ login_required
def createcomment(postid):
    form = CreateComment()
    post_getting_commented = Post.query.filter_by(
        id=postid).first()
    comments_results = db.engine.execute("SELECT * FROM comment")
    comments = [dict(ID=row[0],
                     Author=row[1],
                     Text=row[2],
                     post_id=row[3],
                     user_id=row[4]) for row in comments_results.fetchall()]
    if form.validate_on_submit():
        new_comment = Comment(author=form.author.data,
                              text=form.text.data, post=post_getting_commented, user=current_user)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(f"/createcomment/{postid}")
    return render_template("createcomment.html", post=post_getting_commented, form=form, comments=comments, length_comments=len(comments), current_user=current_user)

# logout route


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/deleteAccount/<userid>', methods=['GET', 'POST'])
@login_required
def deleteaccount(userid):
    db.engine.execute(f"DELETE FROM user WHERE id={userid}")
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
