from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
from hashlib import sha1

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'admin'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/admin'

mongo = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('int_page.html')
    return render_template('login_page.html')
    

    
@app.route('/login',methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if sha1(request.form['pass']).hexdigest() == login_user['password']:
            session['username'] = request.form['username']
            
            return render_template('int_page.html')
    else:
        return 'Invalid Login Credentials/ User does not exist'

@app.route('/logout', methods = ['GET'])
def logout():
    session.pop('username')
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = sha1(request.form['pass'])
            users.insert({'name' : request.form['username'], 'password' : hashpass.hexdigest()})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('signup_page.html')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)