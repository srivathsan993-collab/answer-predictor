import requests
import json

def test_endpoint(file_path, mode):
    print(f"\n--- Testing {mode} ---")
    url = "http://localhost:8000/predict"
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'text/csv')}
        response = requests.post(url, files=files)
        
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Questions: {data.get('total_questions')}")
        print("First prediction sample:")
        print(json.dumps(data['predictions'][0], indent=2))
        
        if 'metrics' in data:
            print("\nMetrics:")
            metrics = data['metrics']
            print(f"Accuracy: {metrics.get('accuracy')}")
            print(f"MAP@3: {metrics.get('map_at_3')}")
            print(f"RMSE (Encoded): {metrics.get('rmse_encoded')}")
    else:
        print("Error:")
        print(response.text)

if __name__ == "__main__":
    # Wait for the server to be up
    import time
    time.sleep(2)
    
    # Test Prediction Mode
    test_endpoint("../sample_test.csv", "Prediction Mode (No Answers)")
    
    # Test Evaluation Mode
    test_endpoint("../sample_test_with_answers.csv", "Evaluation Mode (With Answers)")
