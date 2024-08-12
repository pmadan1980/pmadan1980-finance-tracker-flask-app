import os
from flask import Flask, request, render_template
from datetime import date

#### Defining Flask App
app = Flask(__name__)

#### Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")

#### If this file doesn't exist, create it
if 'expenses.txt' not in os.listdir('.'):
    with open('expenses.txt', 'w') as f:
        f.write('')

def get_expenselist():
    with open('expenses.txt', 'r') as f:
        expenselist = f.readlines()
    return expenselist

def create_new_expenselist():
    os.remove('expenses.txt')
    with open('expenses.txt', 'w') as f:
        f.write('')

def update_expenselist(expenselist):
    os.remove('expenses.txt')
    with open('expenses.txt', 'w') as f:
        f.writelines(expenselist)

################## ROUTING FUNCTIONS #########################

#### Our main page
@app.route('/')
def home():
    return render_template('home.html', datetoday2=datetoday2, expenselist=get_expenselist(), l=len(get_expenselist()))

# Function to clear the expense list
@app.route('/clear')
def clear_list():
    create_new_expenselist()
    return render_template('home.html', datetoday2=datetoday2, expenselist=get_expenselist(), l=len(get_expenselist()))

# Function to add an expense to the list
@app.route('/addexpense', methods=['POST'])
def add_expense():
    expense_description = request.form.get('expense_description')
    expense_amount = request.form.get('expense_amount')
    expense_entry = f"{expense_description} - ${expense_amount}\n"
    with open('expenses.txt', 'a') as f:
        f.writelines(expense_entry)
    return render_template('home.html', datetoday2=datetoday2, expenselist=get_expenselist(), l=len(get_expenselist()))

# Function to remove an expense from the list
@app.route('/delexpense', methods=['GET'])
def remove_expense():
    expense_index = int(request.args.get('delexpenseid'))
    expenselist = get_expenselist()
    if expense_index < 0 or expense_index >= len(expenselist):
        return render_template('home.html', datetoday2=datetoday2, expenselist=expenselist, l=len(expenselist), mess='Invalid Index...')
    else:
        expenselist.pop(expense_index)
    update_expenselist(expenselist)
    return render_template('home.html', datetoday2=datetoday2, expenselist=expenselist, l=len(expenselist))

#### Our main function which runs the Flask App
if __name__ == '__main__':
    app.run(debug=True)
