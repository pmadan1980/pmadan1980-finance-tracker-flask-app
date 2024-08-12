from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 's3cr3t!k3y#1234567890abcdef'  # Replace with a securely generated secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)

# Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        # Hash the password using scrypt
        password = generate_password_hash(request.form['password'], method='scrypt')

        # Check if the user already exists
        user_exists = User.query.filter_by(username=username).first()

        if user_exists:
            flash('Username already exists!')
            return redirect(url_for('login'))

        # Create a new user and add to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.filter_by(id=user_id).first()
    expenses = Expense.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        description = request.form['expense_description']
        amount = request.form['expense_amount']
        new_expense = Expense(description=description, amount=amount, user_id=user_id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('home.html', expenselist=expenses, datetoday2='Today')

@app.route('/delexpense')
def delexpense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    expense_id = request.args.get('delexpenseid')
    expense = Expense.query.filter_by(id=expense_id, user_id=session['user_id']).first()
    
    if expense:
        db.session.delete(expense)
        db.session.commit()
    
    return redirect(url_for('home'))

@app.route('/clear')
def clear():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    Expense.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
