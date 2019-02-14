from flask import Flask
from flask_restful import Api,Resource,reqparse

app=Flask(__name__)
api=Api(app)


users = [
    {
        "username":"Sanat",
        "password":"sanat123"
       
    },
    {
        "username":"Shivani",
        "password":"shiv123"
        
    },
    {
        "username":"Sandhya",
        "password":"sand123"
        

    },
    {
        "username":"Shreya",
        "password":"shre123",
        
    }

]

class User(Resource):
    def get(self,name):
        for user in users:
            if(name==user["username"]):
                return user,200
        return "User not found",400

    def post(self,name):
        parser = reqparse.RequestParser()
        parser.add_argument("password")
        args=parser.parse_args()
        for user in users:
            if(name==user["username"]):
                return "User with name {} already exists!".format(name),400
        user={
            "username":name,
            "password":args["password"],
            
        }
        users.append(user)
        return user,201
        

    def put(self,name):
        parser = reqparse.RequestParser()
        
        
        args=parser.parse_args("password")
        for user in users:
            if(name==user["username"]):
                user["password"]=args["password"]
                return user,200
        user={
            "username":name,
            "password":args["password"],
           
        }
        users.append(user)
        return user,201

    def delete(self,name):
        global users
        users=[user for user in users if user["username"]!=name]
        return "{} is deleted.".format(name), 200


api.add_resource(User,"/user/<string:name>")
app.run(debug=True)
