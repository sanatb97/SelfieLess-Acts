from flask import Flask, jsonify, request
import pymongo
from flask_pymongo import PyMongo
import json
from bson import json_util
import datetime
import base64
from flask import Flask, render_template, url_for, request, session, redirect, flash
from hashlib import sha1
import requests

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'data'
app.config['MONGO_URI'] = 'mongodb://172.17.0.2:27017/data'
mongo = PyMongo(app)

def check_user(username):
    users_all = requests.get("http://172.17.0.1:8080/api/v1/users")
    users_all = users_all.json()
    if username in users_all:
        return 1
    else: 
        return 0

@app.route('/api/v1/categories', methods=['GET'])
def get_categories():
    categories = mongo.db.categories    
    act = mongo.db.acts
    docs_list  = list(categories.find())
    output=[]

    #If no categories have been added as of yet, return No Content Status Code    
    if(len(docs_list)==0):    
        response = jsonify({})        
        response.status_code = 204
        return response     

    for i in docs_list:        
        acts_list = list(act.find({"categoryName":i["categoryName"]}))
        output.append({i['categoryName']:len(acts_list)})
    return jsonify(output), 200

@app.route('/api/v1/categories', methods=['POST'])
def add_category():
    categories = mongo.db.categories
    name = request.json[0]
    old_user = categories.find_one({'categoryName' : name})
    response = jsonify({})

    #If category already exists
    if (old_user):
        response.status_code = 405
        return response
    uid = categories.insert({"categoryName":name})
    new_cat = categories.find_one({"_id":uid})
    return jsonify({}), 201

@app.route('/api/v1/categories/<name>', methods=['DELETE'])
def delete_category(name):
    categories = mongo.db.categories
    old_user = categories.find_one({'categoryName' : name})
    response = jsonify({})

    #Delete only if category exists
    if (old_user):
        categories.remove({"categoryName":name})
        status_msg ="Deleted category "+name
        return jsonify({}), 200
    else:
        response.status_code = 405
        return response

@app.route('/api/v1/acts', methods=['POST'])
def upload_acts():
    act = mongo.db.acts
    users = mongo.db.users
    cats = mongo.db.categories    
    response = jsonify({})    
    act_id = request.json['actId']
    name = request.json['username']
    imgB64 = str(request.json['imgB64'])
    
    #If imgB64 is not in base64 format
    if not (base64.b64encode(base64.b64decode(imgB64)) == imgB64):
        response.status_code = 400
        return response
    
    caption = request.json['caption']
    cat = request.json['categoryName']

    #validating category name
    b = cats.find_one({'categoryName':cat})
    if not b:
        response.status_code = 400
        return response

    time = request.json['timestamp']
    lis=time.split(':')
    timing = lis[1].split('-')
    date_flg = 1
    time_flg = 0
    def validate(date):
        try:
            datetime.datetime.strptime(date,'%d-%m-%Y')
        except:
            date_flg=0
    if(len(timing)==3):
        if(int(timing[0])>=0 and int(timing[0])<=59 and int(timing[1])>=0 and int(timing[1])<=59 and int(timing[2])>=0 and int(timing[2])<=23):
            time_flg = 1
            validate(lis[0])
    if(date_flg==1):
        year = (lis[0].split('-'))[2]
        day = int((lis[0].split('-'))[0])
        month = int((lis[0].split('-'))[1])
        year = int(year)
        print(day,month,year)
        if(year%4==0 and year%100!=0 or year%400==0):
            if(month==2 and day>29):
                date_flg=0
        else:
            if(month==2 and day>28):
                date_flg=0
    if not(time_flg==1 and date_flg==1):
        response.status_code = 405

    upvote = 0

    #Validate actid
    a = act.find_one({'actId':act_id})
    if(a):
        response.status_code = 400
        return response

    #Validate username
    b = users.find_one({'username':name})
    if (check_user(name)):
        act.insert({'username':name, 'actId':act_id, 'imgB64':str(imgB64), 'caption':caption, 'categoryName':cat, 'timestamp':time , 'upvote':upvote})
        return jsonify({}), 201
        
    #User does not exist
    else:
        response.status_code = 400
        return response
    return jsonify({})

@app.route('/api/v1/acts/<id>', methods=['DELETE'])
def remove_acts(id):
    act = mongo.db.acts
    new_act = act.find({"actId":id})
    if(new_act):
        act.remove({"actId":id})
        status_msg ="Deleted act "+id
        return jsonify({}), 200
    else:
        response = jsonify({})
        response.status_code = 400
        return response

@app.route('/api/v1/acts/upvote', methods=['POST'])
def upvote_acts():
    act = mongo.db.acts
    id = request.json[0]
    result = act.update_one({'actId': id}, {'$inc': {'upvote': 1}})
    if(result.modified_count == 1):     
        new_act = act.find_one({"actId":id})
        print new_act        
        count = new_act['upvote']        
        return jsonify({})
    else:
        response = jsonify({})
        response.status_code = 405
        return response
                
@app.route('/api/v1/categories/<categoryName>/acts', methods=['GET'])
def get_acts(categoryName):
    #If category name doesn't exist
    categ = mongo.db.categories
    c_name = categ.find_one({"categoryName":categoryName})
    if not c_name:
        response = jsonify({})
        response.status_code = 405
        return response

    if len(request.args)!=0:
        act = mongo.db.acts
        docs_list  = list(act.find({"categoryName": c_name}).sort("timestamp",-1))
        
        
        endRange = int(request.args['end'])
        startRange = int(request.args['start'])

        expr1 = not (startRange>=1)
        expr2 = not (endRange<=len(docs_list))
        expr3 = not (endRange-startRange+1<=100)
        

        if ( expr1 or expr2 or expr3) :
            response = jsonify({})
            response.status_code = 400
            return response        
        else:        
            output = []
            for i in range(startRange-1,endRange):
                output.append({'username':docs_list[i]['username'],'imgB64': docs_list[i]['imgB64'], 'timestamp':docs_list[i]['timestamp'],'caption':docs_list[i]['caption'],'upvote':docs_list[i]['upvote'], 'category':docs_list[i]['category'], 'actId': docs_list[i]['actId']}) 
        return jsonify(output)
    else:
        act = mongo.db.acts
        docs_list  = list(act.find({"categoryName": categoryName}))

        #No Acts found under the category        
        if(len(docs_list)==0):
            response = jsonify({})
            response.status_code = 204
            return response
        if(len(docs_list)<100):
            output=[]       
            for i in docs_list:
                output.append({'username':i['username'],'imgB64': i['imgB64'], 'timestamp':i['timestamp'],'caption':i['caption'],'upvote':i['upvote'], 'categoryName':i['categoryName'], 'actId': i['actId']})
            return jsonify(output)       
        response = jsonify({})
        
        #Request Entity too large
        if(len(docs_list)>=100):
            response.status_code = 413
            return response

@app.route('/api/v1/categories/<categoryName>/acts/size', methods=['GET'])
def get_acts_count(categoryName):
#If category name doesn't exist
    categ = mongo.db.categories
    c_name = categ.find_one({"categoryName":categoryName})
    if not c_name:
        response = jsonify({})
        response.status_code = 405
        return response
    act = mongo.db.acts
    count = act.count_documents({"categoryName": c_name})
    return jsonify([count]), 200
    

app.run('0.0.0.0',port = 80)

