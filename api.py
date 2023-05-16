from flask import Flask,request,jsonify
from app4 import get_response
from auth import signUp,login,validate_token
from datasetFile import read_file,write_file
from db import db
from bson import ObjectId
import json
app = Flask(__name__)

conversations = db['conversations']


@app.route('/hello')
def hello():
    res = get_response("do you sell macbook")
    return res['result']

@app.route('/send-message', methods=['POST'])
def post_example():
    try:
        # Get the request data
        data = request.json
        message = data['message']
        email = data['email']

        # Validate the token
        # token = request.headers.get('Authorization')
        # if not validate_token(token):
        #     return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
         # check userEmail and message
        if not email or not message:
            return jsonify({'message': 'Invalid request'}), 400
        
        # Find the conversation for this user
        conversation = conversations.find_one({'email': email})
        if not conversation:
            conversations.insert_one({'email': email, 'messages': []})

        # Add the user's message to the conversation
        userMessage = {'role': 'user', 'content': message}
        conversations.update_one({'email': email}, {'$push': {'messages': userMessage}})

        print("here")
        # Do something with the data (e.g. process the message)
        if conversation:
            response_message = get_response(message,conversation['messages'])
        else:
            response_message = get_response(message,[])

        # Check for errors
        if 'error' in response_message:
            return jsonify({'message': response_message['error']}), 500
        
        aiMessage = {'role': 'ai', 'content': response_message['answer']}
        
        # Add the answer to the conversation in db
        conversations.update_one({'email': email}, {'$push': {'messages': aiMessage}})

        # Return a JSON response
        response = {
            'status': 'success',
            'message': response_message['answer']
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/signup', methods=['POST'])
def sign_up():
    # Get the request data
    data = request.json
    email = data['email']
    password = data['password']
    
    try:
        response = signUp(email, password)
        return response
    except Exception as e:
        # If an error occurs, return a 400 error code with an error message
        return {'error': str(e)}, 400
    

@app.route('/login', methods=['POST'])
def logIn():
    # Get the request data
    data = request.json
    email = data['email']
    password = data['password']
    
    # Check if user exists and password matches
    response = login(email, password)
    return response
    
@app.route('/get-dataset',methods=['GET'])
def get_dataset():
    try:
        token = request.headers.get('Authorization')
        if not validate_token(token):
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        return {'dataset':read_file()}
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/update-dataset',methods=['POST'])
def update_dataset():
    try:
        data = request.json
        update_dataset = data['dataset']
        token = request.headers.get('Authorization')
        if not validate_token(token):
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        return {'updated-dataset':write_file(update_dataset)}
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/conversations',methods=['GET'])
def get_conversations():
    try:
        # token = request.headers.get('Authorization')
        # if not validate_token(token):
        #     return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        conversation_cursor = conversations.find({},{"messages":0})
        convLists = list(conversation_cursor)


        # Convert ObjectId instances to strings
        for conv in convLists:
            conv['_id'] = str(conv['_id'])

        
        
        return json.dumps({'conversations': convLists})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/conversation/<id>',methods=['GET'])
def get_conversation(id):
    try:
        # token = request.headers.get('Authorization')
        # if not validate_token(token):
        #     return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

        if not id or len(id) != 24:
            return jsonify({'status': 'error', 'message': 'Invalid id'}), 400
        
        # Find the conversation for this user
        idObject = ObjectId(id)
        conversation = conversations.find_one({'_id': idObject})

        if not conversation:
            return jsonify({'status': 'error', 'message': 'Conversation not found'}), 400
        
        conversation['_id'] = str(conversation['_id'])
        
        return json.dumps({'conversation': conversation})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
