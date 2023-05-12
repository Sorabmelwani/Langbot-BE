from flask import Flask,request,jsonify
from app4 import get_response
from auth import signUp,login,validate_token
from datasetFile import read_file,write_file
app = Flask(__name__)


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

        # Validate the token
        token = request.headers.get('Authorization')
        if not validate_token(token):
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

        # Do something with the data (e.g. process the message)
        response_message = get_response(message)

        # Return a JSON response
        response = {
            'status': 'success',
            'message': response_message['result']
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/sign-up', methods=['POST'])
def sign_up():
    # Get the request data
    data = request.json
    email = data['email']
    password = data['password']
    
    try:
        signUp(email, password)
    except Exception as e:
        # If an error occurs, return a 400 error code with an error message
        return {'error': str(e)}, 400
    
    # Return a response
    response = {
        'status': 'success',
        'message': 'User signed up successfully'
    }
    return response

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

if __name__ == '__main__':
    app.run(debug=True)
