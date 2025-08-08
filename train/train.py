import argparse
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
        parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
        args = parser.parse_args()
        
        print(f"The training data path is: {args.train}")

        input_files = [os.path.join(args.train, file) for file in os.listdir(args.train) if file.endswith('.parquet')]
        
        if not input_files:
            raise ValueError("No Parquet input files found in the training channel.")

        train_data_path = input_files[0]
        df = pd.read_parquet(train_data_path)

        # Use temperature as the feature (X) and humidity as the target (y)
        X = df[['avg_temperature']]
        y = df['avg_humidity']

        # Initialize and train a Linear Regression model
        model = LinearRegression()
        model.fit(X, y)

        # Save the trained model
        model_path = os.path.join(args.model_dir, 'model.joblib')
        joblib.dump(model, model_path)

        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        raise