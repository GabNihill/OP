import os
from flask import (
    Flask,
    render_template,
    request,
    redirect
)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "OPDB.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(200), nullable=False, unique=True)
    items = db.relationship('Item', backref='user', lazy=True)

class Item(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    barcode = db.Column(db.String(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    type = db.Column(db.String(50))
    date_borrow = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return "<Name: {} type: {} barcode: {} >".format(self.name, self.type, self.barcode)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'item'
    }

class TechItem(Item):
    subject = db.Column(db.String(100))

    __mapper_args__ = {
        'polymorphic_identity': 'tech'
    }

class LeisureItem(Item):
    subtype = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'leisure'
    }

@app.route("/", methods=["GET", "POST"])
def home():
    if request.form:
        try:
            print(request.form)
            type = request.form.get("type")
            name = request.form.get("title")
            tech = request.form.get("tech")
            subtype = request.form.get("subtype")
            barcode = request.form.get("barcode")
            item = None
            if not type or not name or not barcode:
                raise Exception("Missing fields in form")
            if (type == "leisure"):
                if not subtype:
                    raise Exception("Missing fields in form")
                item = LeisureItem(name=name, barcode=barcode, type=type, subtype=subtype)
            else:
                if not tech:
                    raise Exception("Missing fields in form")
                item = TechItem(name=name, barcode=barcode, type=type, subject=tech)
            print(item)
            db.session.add(item)
            db.session.commit()
        except Exception as e:
            print("Failed to add book")
            print(e)
    items = Item.query.all()
    return render_template("home.html", items=items)


@app.route("/search")
def search():
    return render_template("search.html", results=[])

@app.route("/results")
def results():
    if request.args['searchInput']:
        print(request.args['searchInput'])
        try:
            results = db.session.query(Item).filter(or_(Item.name.contains(request.args['searchInput']),
                                                        TechItem.subject.contains(request.args['searchInput']),
                                                        LeisureItem.subtype.contains(request.args['searchInput']),
                                                        Item.barcode.contains(request.args['searchInput'])))
            print(results)
            return render_template("searchResults.html", results=results)
        except Exception as e:
            print("Failed to search items")
            print(e)



@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        barcode = request.form.get("barcode")
        item = Item.query.filter_by(barcode=barcode).first()
        item.name = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update item title")
        print(e)
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    barcode = request.form.get("barcode")
    book = Item.query.filter_by(barcode=barcode).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)