from flask import Flask, jsonify, request
import pymongo
from flask_pymongo import PyMongo
import json
from bson import json_util
import datetime
import base64
from hashlib import sha1
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'admin'
app.config['MONGO_URI'] = "mongodb://localhost/admin"
mongo = PyMongo(app)

@app.route('/api/v1/users', methods=['POST'])
def add_user():
    user = mongo.db.users
    username = request.json['username']
    password = request.json['password']
    old_user = user.find_one({'username' : username})
    if (old_user):
        
        return 400

    user_id = user.insert({'username' : username, 'password' : password})
    new_user = user.find_one({'_id' : user_id})
    output = {'username' : new_user['username'], 'password' : new_user['password']}
    return jsonify({'result' : output})



@app.route('/api/v1/users/<name>', methods=['DELETE'])
def delete_user(name):
    user = mongo.db.users
    old_user = user.find_one({'username' : name})
    if (old_user):
        user.remove({"username":name})
        status_msg ="Deleted user "+name
        return jsonify({"result":status_msg})
    else:
       
        return 400


@app.route('/api/v1/categories', methods=['GET'])
def get_categories():
    categories = mongo.db.categories
    cats  = list(categories.find())
    output=[]
    for i in cats:
        output.append({i['id']:i['name']})
    return jsonify({"categories": output})


@app.route('/api/v1/categories', methods=['POST'])
def add_category():
    categories = mongo.db.categories
    c_id = request.json['id']
    name = request.json['name']
    old_user = categories.find_one({'name' : name})
    
    if (old_user):
        
        return 400
    uid = categories.insert({"id":c_id,"name":name})
    new_cat = categories.find_one({"_id":uid})
    output = {"id":new_cat['id'], "name":new_cat['name']}
    return jsonify({"new category added": output}), 201

@app.route('/api/v1/categories/<name>', methods=['DELETE'])
def delete_category(name):
    categories = mongo.db.categories
    old_user = categories.find_one({'name' : name})
    
    if (old_user):
        categories.remove({"name":name})
        status_msg ="Deleted category "+name
        return jsonify({"result":status_msg})
    else:
        
        return 400

@app.route('/api/v1/acts', methods=['POST'])
def upload_acts():
    act = mongo.db.acts
    users = mongo.db.users

    id = request.json['actId']
    name = request.json['username']
    imgB64 = base64.encodestring(unicode.encode(request.json['imgB64']))
    caption = request.json['caption']
    cat = request.json['category']
    time = datetime.datetime.now().strftime("%d-%B-%Y:%S-%M-%I")
    #Validate actid
    a = act.find_one({'actid':id})
    
    if(a):
        
        return 400
    b = users.find_one({'username':name})
    if(b):
        uid = act.insert({'username':name, 'actId':id, 'imgB64':str(imgB64), 'caption':caption, 'category':cat, 'timestamp':time})
        new_act = act.find_one({"_id":uid})
        output = {"Caption":new_act['caption'], "Image":new_act['imgB64']}
        return jsonify({"result":output}), 201
    else:
       
        return 400

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
        return 400

@app.route('/api/v1/acts/upvote', methods=['POST'])

def upvote_acts():

    act = mongo.db.acts
    
    id = request.json['actId']
    
    result = act.update_one({'actId': id}, {'$inc': {'upvote': 1}})

    if(result.modified_count == 1):
      
        new_act = act.find({"actId":id})
        
        count = new_act['upvote']

        return jsonify({"result":count})

    else:

        response = jsonify({})

        response.status_code = 400

        return response
        
                
@app.route('/api/v1/categories/<categoryName>/acts', methods=['GET'])

def get_acts(categoryName):

    act = mongo.db.acts

    docs_list  = list(act.find({"category": categoryName}))
    
    if(len(docs_list)<100):
    
        output=[]
    
        for i in docs_list:
    
            output.append(i)

    else:

        response = jsonify({})

        response.status_code = 400

        return response
        
    return jsonify(output)


@app.route('/api/v1/categories/<categoryName>/acts/size', methods=['GET'])

def get_acts_count(categoryName):

    act = mongo.db.acts
    
    count = act.count_documents({"category": categoryName})

    return jsonify({"result":count})
    


@app.route('/api/v1/categories/<categoryName>/acts?start={startRange}&end={endRange}', methods=['GET'])

def get_acts_range(categoryName):
    act = mongo.db.acts
    docs_list  = list(act.find({"category": categoryName}).sort("timestamp",-1))
    if( !(startRange>=1) or !(endRange<=len(docs_list)) or !(endRange-startRange+1<=100) ):
        response = jsonify({})
        response.status_code = 400
        return response
    
    else:
        
        output = []
        
        for i in range(startRange-1,endRange+1):
            
            output.append( docs_list[i] )
            
    return jsonify(output)   

app.run(debug=True)