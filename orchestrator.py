from flask import Flask, request, jsonify, render_template, redirect, url_for, abort, Response, make_response
import numpy as np
import docker
import threading
import os
import time
import requests


app = Flask('__main__', template_folder='./')

host_ip = "0.0.0.0"

host_port = 80
request = 0
portList = {}  # 8000 after init_container
container_id_List = {}
first_request = 0 
count = 0
portList_lock = threading.Lock()
container_id_List_lock = threading.Lock()
request_lock = threading.Lock()


@app.route('/', methods=['POST', 'GET'])
def index():
	return 'orchestrator home'


def init_container():
	build_cmd = os.popen("sudo docker build -t acts:latest .").read()
	run_cmd = os.popen("sudo docker run -p 8000:80 acts:latest").read()
	container_id = run_cmd.rstrip()
	portList[8000] = 8000
	container_id_List[8000] = container_id

@app.route('/api/v1/categories', methods=['GET'])
def list_category():
	#lock acquire
	request_lock.acquire()
	global request,portList,container_id_List,count
	if(first_request == 0):
		first_request = 1
		request = 1
		#implement auto scaler
	portList_lock.acquire()
	count = (count+1)%len(portList)
	url =  ("http://0.0.0.0:" + str(count+8000) +"/api/v1/categories")
	portList_lock.release()
	resp = requests.request(
		method=request.method,
		url= new_url,
		headers={key: value for (key, value) in request.headers if key != 'Host'},
		data=request.get_data())
	headers = [(name, value) for (name, value) in resp.raw.headers.items()]
	response = Response(resp.content, resp.status_code, headers)
	request = request + 1
	#lock release
	request_lock.release()
	return response

#to be implemented for all APIs in the same format

if __name__ == "__main__":
	init_container()
	#implement fault tolerator
	app.run(host = "0.0.0.0", port = 80,debug = True)