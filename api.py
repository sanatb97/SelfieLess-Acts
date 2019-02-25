from flask import Flask, jsonify, request
import pymongo
from flask_pymongo import PyMongo
import json
from bson import json_util
import datetime
import base64
from flask import Flask, render_template, url_for, request, session, redirect, flash

import bcrypt
from hashlib import sha1


app = Flask(__name__)



app.config['MONGO_DBNAME'] = 'admin'

app.config['MONGO_URI'] = 'mongodb://localhost:27017/admin'

mongo = PyMongo(app)



@app.route('/api/v1/users', methods=['POST'])

def add_user():

    user = mongo.db.users
    print(user)

    username = request.json['username']


    password = request.json['password']
    hashpass = sha1(password)
 

    old_user = user.find_one({'username' : username})

    response = jsonify({})

    if (old_user):
        response.status_code = 400
        return response

    user_id = user.insert({'username' : username, 'password' : hashpass.hexdigest()})

    new_user = user.find_one({'_id' : user_id})



    output = {'username' : new_user['username'], 'password' : new_user['password']}

    return jsonify({})



@app.route('/api/v1/users/<name>', methods=['DELETE'])

def delete_user(name):

    user = mongo.db.users

    old_user = user.find_one({'username' : name})

    response = jsonify({})

    if (old_user):

        user.remove({"username":name})

        status_msg ="Deleted user "+name

        return jsonify({})

    else:

        response.status_code = 400

        return response



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
        
        acts_list = list(act.find({"category":i["name"]}))

        output.append({i['name']:len(acts_list)})

    return jsonify(output), 200



@app.route('/api/v1/categories', methods=['POST'])

def add_category():

    categories = mongo.db.categories

    id = request.json['id']

    name = request.json['name']

    old_user = categories.find_one({'name' : name})

    response = jsonify({})

    if (old_user):

        response.status_code = 400

        return response

    uid = categories.insert({"id":id,"name":name})

    new_cat = categories.find_one({"_id":uid})

    output = {"id":new_cat['id'], "name":new_cat['name']}

    return jsonify({"new category added": output}), 201





@app.route('/api/v1/categories/<name>', methods=['DELETE'])

def delete_category(name):

    categories = mongo.db.categories

    old_user = categories.find_one({'name' : name})

    response = jsonify({})

    if (old_user):

        categories.remove({"name":name})

        status_msg ="Deleted category "+name

        return jsonify({"result":status_msg})

    else:

        response.status_code = 400

        return response



@app.route('/api/v1/acts', methods=['POST'])

def upload_acts():

    act = mongo.db.acts

    users = mongo.db.users



    id = request.json['actId']

    name = request.json['username']

    imgB64 = base64.encodestring(str.encode(str(request.json['imgB64'])))

    caption = request.json['caption']

    cat = request.json['category']

    time = datetime.datetime.now().strftime("%d-%B-%Y:%S-%M-%I")

    upvote = 0
    #Validate actid

    a = act.find_one({'actid':id})

    response = jsonify({})

    if(a):

        response.status_code = 400

        return response

    #Validate username

    b = users.find_one({'username':name})

    if(b):

        uid = act.insert({'username':name, 'actId':id, 'imgB64':str(imgB64), 'caption':caption, 'category':cat, 'timestamp':time , 'upvote':upvote})

        new_act = act.find_one({"_id":uid})

        output = {"Caption":new_act['caption'], "Image":new_act['imgB64']}

        return jsonify({"result":output}), 201

    else:

        response.status_code = 400

        return response



    return jsonify({"result":"done"})



@app.route('/api/v1/acts/<id>', methods=['DELETE'])

def remove_acts(id):

    act = mongo.db.acts

    new_act = act.find({"actId":id})

    if(new_act):

        act.remove({"actId":id})

        status_msg ="Deleted act "+id

        return jsonify({"result":status_msg})

    else:

        response = jsonify({})

        response.status_code = 400

        return response

# UPVOTE ACT

@app.route('/api/v1/acts/upvote', methods=['POST'])

def upvote_acts():

    act = mongo.db.acts
    
    id = request.json['actId']
    
    result = act.update_one({'actId': id}, {'$inc': {'upvote': 1}})

    if(result.modified_count == 1):
      
        new_act = act.find_one({"actId":id})
        print new_act
        
        count = new_act['upvote']
        
        return jsonify({"result":count})

    else:

        response = jsonify({})

        response.status_code = 405

        return response
        
        
# LIST ACTS GIVEN A CATEGORY (COUNT<100)
        
@app.route('/api/v1/categories/<categoryName>/acts', methods=['GET'])

def get_acts(categoryName):

    #If category name doesn't exist
    categ = mongo.db.categories
    c_name = categ.find_one({"name":categoryName})
    if not c_name:
        print "in here"
        print categoryName
        response = jsonify({})
        response.status_code = 405
        return response

    

    if len(request.args)!=0:
        act = mongo.db.acts
        docs_list  = list(act.find({"category": categoryName}).sort("timestamp",-1))
        print len(docs_list)
        
        endRange = int(request.args['end'])
        startRange = int(request.args['start'])

        expr1 = not (startRange>=1)
        expr2 = not (endRange<=len(docs_list))
        expr3 = not (endRange-startRange+1<=100)
        print expr1,expr2,expr3

        if ( expr1 or expr2 or expr3) :
            
            response = jsonify({})

            response.status_code = 400

            return response
        
        else:
            print "here, it"
            output = []
            
            for i in range(startRange-1,endRange):
                output.append({'username':docs_list[i]['username'],'imgB64': docs_list[i]['imgB64'], 'timestamp':docs_list[i]['timestamp'],'caption':docs_list[i]['caption'],'upvote':docs_list[i]['upvote'], 'category':docs_list[i]['category'], 'actId': docs_list[i]['actId']})
                
                
        return jsonify(output)
    else:
        act = mongo.db.acts
        docs_list  = list(act.find({"category": categoryName}))
        print docs_list
        #No Acts found under the category
        
        if(len(docs_list)==0):
        
            response = jsonify({})
            
            response.status_code = 204

            return response
        
        if(len(docs_list)<100):
        
            output=[]
        
            for i in docs_list:
                output.append({'username':i['username'],'imgB64': i['imgB64'], 'timestamp':i['timestamp'],'caption':i['caption'],'upvote':i['upvote'], 'category':i['category'], 'actId': i['actId']})
                   
            return jsonify(output)
        
        response = jsonify({})
        
        #Request Entity too large
        
        if(len(docs_list)>=100):
            
            response.status_code = 413

            return response
    
    
# LIST NUMBER OF ACTS FOR A GIVEN CATEGORY

@app.route('/api/v1/categories/<categoryName>/acts/size', methods=['GET'])

def get_acts_count(categoryName):
#If category name doesn't exist
    categ = mongo.db.categories
    c_name = categ.find_one({"name":categoryName})
    if not c_name:
        response = jsonify({})
        response.status_code = 405
        return response
    act = mongo.db.acts
    count = act.count_documents({"category": categoryName})

    return jsonify([count])
    

# LIST ACTS IN A GIVEN RANGE





















app.run(debug=True)