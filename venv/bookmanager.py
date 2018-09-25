import os
from flask import (
    Flask,
    render_template,
    request,
    redirect
)

from flask_sqlalchemy import SQLAlchemy


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Author(db.Model):
    fullname = db.Column(db.String(200), unique=True, nullable=False, primary_key=False)
    id = db.Column(db.Integer, primary_key=True)
    books = db.relationship('Book', backref='author', lazy=True, cascade="all, delete-orphan")
    def __repr__(self):
        return "<Name: {} Id: {} Books: {} >".format(self.fullname, self.id, self.books)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    def __repr__(self):
        return "<Title: {}>".format(self.title)

def get_or_create_author(fullname):
    author = db.session.query(Author).filter_by(fullname=fullname).first()
    if author:
        return author
    else:
        author = Author(fullname=fullname)
        db.session.add(author)
        db.session.commit()
        return author


@app.route("/", methods=["GET", "POST"])
def home():
    if request.form:
        try:
            author = get_or_create_author(fullname=request.form.get("author"))
            print(author)
            book = Book(title=request.form.get("title"), author_id=author.id)
            author.books = author.books + book
            print(book)
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            print("Failed to add book")
            print(e)
    books = Book.query.all()
    authors = Author.query.all()
    return render_template("home.html", books=books, authors=authors)


@app.route("/search")
def search():
    return render_template("search.html", results=[])

@app.route("/results")
def results():
    if request.args['searchInput']:
        print(request.args['searchInput'])
        try:
            results = db.session.query(Book).filter(Book.title.contains(request.args['searchInput']))
            print(results)
            return render_template("searchResults.html", results=results)
        except Exception as e:
            print("Failed to search items")
            print(e)



@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        book = Book.query.filter_by(title=oldtitle).first()
        book.title = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update book title")
        print(e)
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)