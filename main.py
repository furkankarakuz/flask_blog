from flask import Flask, render_template, request , session , redirect , url_for
from wtforms import Form, TextAreaField, StringField, PasswordField, EmailField, validators , FileField , SelectField
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.datastructures import CombinedMultiDict
from flask_ckeditor import CKEditor , CKEditorField


class LoginForm(Form):
    username = StringField("", [validators.Length(
        min=5, max=39), validators.DataRequired()])
    password = PasswordField("", validators=[validators.Length(
        min=5, max=30), validators.DataRequired()])


class RegisterForm(Form):
    name = StringField("", [validators.Length(
        min=2, max=20), validators.DataRequired()])
    surname = StringField("", [validators.Length(
        min=2, max=20), validators.DataRequired()])
    username = StringField("", [validators.Length(
        min=5, max=30), validators.DataRequired()])
    email = EmailField("", [validators.Length(
        min=5, max=30), validators.DataRequired()])
    password = PasswordField("", [validators.DataRequired()])

class ArticleForm(Form):
    title = StringField("",[validators.Length(min=15,max=50),validators.DataRequired()])
    content = TextAreaField("",[validators.Length(min=30,max=1000),validators.DataRequired()])
    tag = SelectField("",choices=["Web","Desktop","AI","Mobile","Other"])
    image_file = FileField(validators=[validators.DataRequired()],name="file")

db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////Users/furkan/Desktop/GithubProjects/flask_blog/blog.db"
db.init_app(app)

app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String)
    password = db.Column(db.String)

class Article(db.Model):
    id_article = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.String)
    title = db.Column(db.String)
    content = db.Column(db.String)
    tag = db.Column(db.String)
    image_file = db.Column(db.String)
    created_date=db.Column(db.String)


@app.route("/", methods=["GET", "POST"])
def index():
    text = "Welcome to Website"
    register_form = RegisterForm(request.form)
    if request.method == "POST" and register_form.validate():
        create_user = User(name=register_form.name.data,
                           surname=register_form.surname.data,
                           username=register_form.username.data,
                           email=register_form.email.data,
                           password=register_form.password.data)
        db.session.add(create_user)
        db.session.commit()
        return redirect(url_for("index"))
    else:
        login_form = LoginForm(request.form)
        if request.method == "POST" and login_form.validate():
            get_user = User.query.filter_by(
                username=login_form.username.data , password =login_form.password.data).first()
            if get_user:
                session["check_login"] = True
                session["username"] = get_user.username
                text = "Welcome %s"%(session["username"])
                return redirect(url_for("index"))
    if "username" in session:
        text = "Welcome %s"%(session["username"])
    return render_template("index.html", login_form=login_form, register_form=register_form,text=text)

@app.route("/logout")
def logout():
    session["check_login"]=False
    session.clear()
    return redirect(url_for("index"))

@app.route("/articles",methods=["GET", "POST"])
def articles():
    register_form = RegisterForm(request.form)
    login_form = LoginForm(request.form)
    articles_data = Article.query.all()
    return render_template("articles.html",login_form=login_form, register_form=register_form,articles=articles_data)

@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    my_articles = Article.query.filter_by(user=session["username"]).all()
    return render_template("dashboard.html",my_articles=my_articles)


@app.route("/addarticle",methods=["GET","POST"])
def add_article():
    article_form = ArticleForm(request.form)
    image = ArticleForm(CombinedMultiDict((request.files, request.form)))
    if request.method == "POST" or image.validate():
        create_article =  Article(user=session["username"],
                                  title=article_form.title.data,
                                  content=article_form.content.data,
                                  tag=article_form.tag.data,
                                  image_file=article_form.image_file.data,
                                  created_date=datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        
        
        db.session.add(create_article)
        db.session.commit()

        create_article.image_file="static/images/%s"%(str(create_article.id_article)+".png")
        f = request.files['file']
        f.save("static/images/%s"%(str(create_article.id_article)+".png"))
        db.session.commit()
        return redirect(url_for("articles"))
    return render_template("add_article.html",form=article_form)

@app.route("/detail<int:id>")
def article_detail(id):
        my_article = Article.query.filter_by(id_article=id).first()
        print(my_article.title)
        return render_template("article_detail.html",my_article=my_article)
        


@app.route("/update<int:id>",methods=["GET","POST"])
def update_article(id):
    my_article = Article.query.filter_by(id_article=id).first()
    if request.method=="GET":
        article_form = ArticleForm()
        article_form.title.data = my_article.title
        article_form.content.data = my_article.content
        article_form.tag.data = my_article.tag
        article_form.image_file.filename = my_article.image_file

    
        return render_template("update_article.html",form=article_form)
    else:
        article_form = ArticleForm(request.form)
        if request.method == "POST":
            my_article.title = article_form.title.data
            my_article.content = article_form.content.data
            my_article.tag = article_form.tag.data
            my_article.image_file = article_form.image_file.data
            my_article.created_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

            db.session.commit()
            my_article.image_file="static/images/%s"%(str(my_article.id_article)+".png")
            f = request.files['file']
            f.save("static/images/%s"%(str(my_article.id_article)+".png"))
            db.session.commit()
            return redirect(url_for("articles"))
        return render_template("update_article.html",form=article_form)


@app.route("/delete<int:id>",methods=["GET","POST"])
def delete_article(id):
    my_article = Article.query.filter_by(id_article=id).first()
    db.session.delete(my_article)
    db.session.commit()
    return redirect(url_for("dashboard"))
        

if __name__ == "__main__":
    app.run(debug=True)
    with app.app_context():
        db.create_all()
