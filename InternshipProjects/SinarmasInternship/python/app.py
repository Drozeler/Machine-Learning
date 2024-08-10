from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId  # Import ObjectId

app = Flask(__name__)

# Configure MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.house_prices
predictions_collection = db.predictions

# Load the trained model
with open('random_forest_model.pkl', 'rb') as file:
    random_forest_model = pickle.load(file)
with open('gradient_boosting_model.pkl', 'rb') as file:
    gradient_boost_model = pickle.load(file)
with open('random_search_model.pkl', 'rb') as file:
    random_search_model = pickle.load(file)
with open('extra_tree_model.pkl', 'rb') as file:
    extra_tree_model = pickle.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json

    model_type = data.get('model')
    if model_type == 'random_forest':
        model = random_forest_model  # Load your random forest model
    elif model_type == 'gradient_boost':
        model = gradient_boost_model  # Load your linear regression model
    elif model_type == 'random_search':
        model = random_search_model  # Load your SVM model
    elif model_type == 'extra_tree':
        model = extra_tree_model  # Load your neural network model
    else:
        return jsonify({'error': 'Invalid model type'})
    
    # Extract features from the request
    OverallQual = data['OverallQual']
    TotalBsmtSF = data['TotalBsmtSF']
    FirstFlrSF = data['1stFlrSF']
    SecondFlrSF = data['2ndFlrSF']
    GrLivArea = data['GrLivArea']
    GarageCars = data['GarageCars']
    GarageArea = data['GarageArea']

    # Calculate derived features
    TotalSF = TotalBsmtSF + FirstFlrSF + SecondFlrSF
    TotalLivingArea = TotalBsmtSF + FirstFlrSF + SecondFlrSF + GrLivArea
    GarageScore = GarageCars * GarageArea

    # Create DataFrame for model prediction
    input_data = pd.DataFrame([{
        'OverallQual': OverallQual,
        'TotalSF': TotalSF,
        'TotalLivingArea': TotalLivingArea,
        'GrLivArea': GrLivArea,
        'GarageScore': GarageScore,
        'GarageCars': GarageCars,
        'GarageArea': GarageArea,
        'TotalBsmtSF': TotalBsmtSF,
        '1stFlrSF': FirstFlrSF
    }])

    # Make prediction
    prediction = model.predict(input_data)[0]

    # Return the prediction
    return jsonify({'predictedPrice': prediction})

@app.route('/api/store_data', methods=['POST'])
def store_data():
    data = request.json
    data['dateTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    predictions_collection.insert_one(data)
    return jsonify({'status': 'Data stored successfully'})

@app.route('/api/view_data', methods=['GET'])
def view_data():
    data = predictions_collection.find()
    results = []
    for item in data:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
        results.append(item)
    return jsonify(results)

@app.route('/api/delete_data/<id>', methods=['DELETE'])
def delete_data(id):
    result = predictions_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'status': 'Data deleted successfully'})
    else:
        return jsonify({'status': 'Data not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)