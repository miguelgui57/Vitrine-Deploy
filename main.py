import os
from flask import Flask, render_template, request, redirect, session 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] ='414a00877d54dfbbe5f189ca7c3b8b3f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

class Todo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100))
  price = db.Column(db.String(100))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  email = db.Column(db.String(100))
  password = db.Column(db.String(200)) 
 
@app.route('/')
def index():
  if 'user_id' not in session:
    return redirect('/login')
  user_id = session['user_id']
  products = Todo.query.filter_by(user_id=user_id).all()
  return render_template('index.html', products=products)

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/signin', methods=['POST'])
def signin():
  email = request.form.get('email')
  password = request.form.get('password')
  user = User.query.filter_by(email=email).first()
  if not user:
    return redirect('/login')
  if not check_password_hash(user.password, password):
    return redirect('/login')
  session['user_id'] = user.id
  return redirect('/')

@app.route('/register')
def register():
  return render_template('register.html')    

@app.route('/signup', methods=['POST'])
def signup():
  name= request.form.get('name')
  email = request.form.get('email')
  password = request.form.get('password')
  user = User.query.filter_by(email=email).first()
  if user:
    return redirect('/register')
  new_user = User(
    name=name,
    email=email,
    password=generate_password_hash(password, method='sha256')
  )
  db.session.add(new_user)
  db.session.commit()
  return redirect('/login')  

@app.route('/logout')
def logout():
  if 'user_id' in session:
    session.pop('user_id', None)
  return redirect('/login')  

@app.route('/create', methods=['POST'])
def create():
  if 'user_id' not in session:
    return redirect('/login')
  user_id = session['user_id']

  title = request.form.get('title')
  price = request.form.get('price')
  new_todo = Todo(title=title, price=price, user_id=user_id)
  db.session.add(new_todo)
  db.session.commit()
  return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
  todo = Todo.query.filter_by(id=id).first()
  db.session.delete(todo)
  db.session.commit()
  return redirect('/')

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
  title = request.form.get('title')
  price = request.form.get('price')
  todo= Todo.query.filter_by(id=id).first()
  todo.title = title
  todo.price = price
  db.session.commit()
  return redirect('/')  

if __name__ == '__main__':
  db.create_all()
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port = port)