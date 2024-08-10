import pickle
import numpy as np

# Load your model
with open('random_forest_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Check the type of the model
print("Type of the model:", type(model))

# Check if the loaded model is a NumPy array
if isinstance(model, np.ndarray):
    print("The model is a NumPy array")
    print("Shape:", model.shape)
    print("Data type:", model.dtype)
    print("First element:", model[0] if model.size > 0 else "Array is empty")
else:
    print("The model is not a NumPy array")

# Check for common methods in machine learning models
if hasattr(model, 'predict'):
    print("Model has a predict method")
    print(model.predict)
elif hasattr(model, 'fit'):
    print("Model has a fit method")
    print(model.fit)
else:
    print("Model does not have typical methods like predict or fit")
