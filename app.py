from datetime import datetime
from flask import Flask, flash, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bhand.db"
db = SQLAlchemy(app)
app.secret_key = 'your_secret_key'

class DBSet(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return f'{self.client_id} - {self.name}'
    

@app.route("/")
def home():
    db.create_all()
    return render_template('index.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/delete/<int:id>")
def deleteval(id:int):
    val = DBSet.query.filter_by(client_id=id).first()
    db.session.delete(val)
    db.session.commit()
    flash('Query deleted successfully!', 'danger')
    return redirect('/show')

@app.route("/update/<id>",methods=['GET','POST'])
def update(id:int):
    if request.method == 'POST':
        
        val = DBSet.query.filter_by(client_id=id).first()
        val.name=request.form['name']
        val.email=request.form['email']
        val.message=request.form['message']
        db.session.add(val)
        db.session.commit()
        flash('Query updated successfully!', 'success') 
        return redirect('/show')
    val = DBSet.query.filter_by(client_id=id).first()
    return render_template('update.html',client=val)

@app.route("/show",methods=['GET','POST'])
def show():
    if request.method == 'POST':
        queries = DBSet(name=request.form['name'],email=request.form['email'], message = request.form['message'])
        db.session.add(queries)
        db.session.commit()
    queries =DBSet.query.all()
    print(queries)
    return render_template('details.html', allVal=queries)

with app.app_context():
    db.create_all()

app.run(debug=True)