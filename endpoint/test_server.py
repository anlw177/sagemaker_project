import os
from flask import Flask, request
from inference import model_fn, predict_fn

# Set up the Flask application
app = Flask(__name__)

# Load the model outside of the request handler for efficiency
# This simulates how SageMaker loads the model once when the container starts
model_dir = os.path.join(os.getcwd(), 'model.tar.gz')
model = model_fn(model_dir)

@app.route('/ping', methods=['GET'])
def ping():
    """Health check."""
    return "", 200

@app.route('/invocations', methods=['POST'])
def invocations():
    """Predicts a response to an input payload."""
    content_type = request.content_type
    data = request.get_json()  # Assuming the input is a single JSON value like 25.5

    # Pass the deserialized data directly to predict_fn
    prediction = predict_fn(data, model)
    
    return str(prediction), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)