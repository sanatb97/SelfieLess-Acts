from flask import Flask, jsonify, request
import pymongo
from flask_pymongo import PyMongo
import json
from bson import json_util
import datetime
import base64
from flask import Flask, render_template, url_for, request, session, redirect, flash
from hashlib import sha1

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'data'
app.config['MONGO_URI'] = 'mongodb://172.31.32.90:27017/data'
mongo = PyMongo(app)
#HTTP Requests count
def incrementHTTP():
	mongo.db.http.insert_one({'http': 1})

@app.route('/api/v1/users', methods=['POST'])
def add_user():
    incrementHTTP()
    user = mongo.db.users
    username = request.json['username']
    password = request.json['password']
    old_user = user.find_one({'username' : username})
    response = jsonify({})

    #If User already exists
    if (old_user):
        response.status_code = 405
        return response

    #Checking for SHA1 Hash Hex format of password
    if len(password)!=40:
        response.status_code = 400
        return response
    for a in password:
        if a not in "1234567890abcdef":
            response.status_code = 400
            return response

    user_id = user.insert({'username' : username, 'password' : password})
    new_user = user.find_one({'_id' : user_id})
    output = {'username' : new_user['username'], 'password' : new_user['password']}
    return jsonify({}), 201

@app.route('/api/v1/users/<name>', methods=['DELETE'])
def delete_user(name):
    incrementHTTP()
    user = mongo.db.users
    old_user = user.find_one({'username' : name})
    response = jsonify({})
    #Delete only if user exists     
    if (old_user):
        user.remove({"username":name})
        status_msg ="Deleted user "+name
        return jsonify({}), 200

    else:
        response.status_code = 405
        return response


@app.route('/api/v1/users', methods=['GET'])
def list_all_users():
    incrementHTTP()
    user = mongo.db.users
    #print("inside")
    response = jsonify({})
    users_all = list(user.find({}))
    if(len(users_all)==0):
        response.status_code = 204
        return response	
    users_list = []
    for i in users_all:
        users_list.append(i['username'])
    if not users_list:
        response.status_code = 404
    else:
        return jsonify(users_list), 200

@app.route('/api/v1/_count', methods=['GET'])
def requestsCount():
    counts = mongo.db.http.count()
	if(counts>=0):
    	return jsonify([counts]),200
    else:
    	return jsonify({}),405

@app.route('/api/v1/_count', methods=['DELETE'])
def resetCount():
    r = mongo.db.http.drop()
    return jsonify({}), 200 

if __name__ == '__main__':
        app.run('0.0.0.0',port=80)

