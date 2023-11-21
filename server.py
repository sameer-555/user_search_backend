from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from urllib.parse import quote_plus
from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
CORS(app)

client = MongoClient(f"mongodb+srv://{quote_plus(os.getenv('USERNAME'))}:{quote_plus(os.getenv('PASSWORD'))}@{os.getenv('CLUSTER_NAME')}.mqrj53v.mongodb.net/?retryWrites=true&w=majority")

db = client[os.getenv('DB_NAME')]
collection = db[os.getenv('COLLECTION')]

def validate_user_data(user_data):
    if 'name' not in user_data or not user_data['name'].strip():
        return False
    for field in ['age', 'weight', 'height']:
        if field in user_data:
            try:
                user_data[field] = int(user_data[field])
            except ValueError:
                return False
    return True

@app.route('/user/add', methods=['POST'])
def add_user():
    user_data = request.json
    if not validate_user_data(user_data):
        return jsonify({'message': 'Invalid user data. Check the requirements.'}), 400
    result = collection.insert_one(user_data)

    if result.inserted_id:
        return jsonify({'message': 'User added successfully', 'user_id': str(result.inserted_id)})
    else:
        return jsonify({'message': 'Failed to add user'})


@app.route('/user', methods=['GET'])
def get_users():
    user_name_prefix = request.args.get('name', '')
    if user_name_prefix:
        users = list(collection.find({'name': {'$regex': f'^{user_name_prefix}', '$options': 'i'}}))
    else:
        users = list(collection.find({}))
    # Convert objectid to str for serialization
    for user in users:
        user['_id'] = str(user['_id'])

    return jsonify({'users': users})


if __name__ == '__main__':
    app.run(port=8000, debug=True)