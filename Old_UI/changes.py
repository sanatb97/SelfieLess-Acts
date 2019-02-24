// UPVOTE ACT

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
        
        
// LIST ACTS GIVEN A CATEGORY (COUNT<100)
        
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
    
    
// LIST NUMBER OF ACTS FOR A GIVEN CATEGORY

@app.route('/api/v1/categories/<categoryName>/acts/size', methods=['GET'])

def get_acts_count(categoryName):

	act = mongo.db.acts
	
	count = act.count_documents({"category": categoryName})

    return jsonify({"result":count})
    

// LIST ACTS IN A GIVEN RANGE

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
