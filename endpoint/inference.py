import os
import joblib
import pandas as pd

def model_fn(model_dir):
    """
    Loads the trained model from the model directory.
    """
    print("Loading model.")
    
    #for test_server
    #model = joblib.load("model.joblib")
    
    #for endpoint
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    print("Model loaded.")
    return model

def predict_fn(input_data, model):
    """
    Makes a prediction with the loaded model.
    """
    print("Making prediction.")
    # The input data is expected as a single value, but the model expects a DataFrame
    input_df = pd.DataFrame([input_data], columns=['avg_temperature'])
    prediction = model.predict(input_df)
    print(f"Prediction made: {prediction[0]}")
    # Return the first prediction value
    return prediction[0]