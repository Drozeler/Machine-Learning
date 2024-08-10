import joblib

# Load the saved model
loaded_model = joblib.load('random_forest_model_new.pkl')

print("Loaded model type:", type(loaded_model))