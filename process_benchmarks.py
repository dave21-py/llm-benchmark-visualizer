import pandas as pd
import requests
import io
import json
from datetime import datetime

# Example output row:
# model_name,benchmark_name,score,param_B,country,updated_at
# gpt-4,MMLU,0.864,1750,USA,2023-11-15T12:30:00Z

def fetch_and_process_benchmarks(input_csv_path: str, output_csv_path: str):
    """
    Reads a CSV of models, fetches benchmark data from URLs, and outputs a normalized CSV.

    Args:
        input_csv_path (str): Path to the input CSV file with model information.
        output_csv_path (str): Path to write the final normalized scores CSV.
    """
    try:
        models_df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}")
        return

    all_scores = []
    # Get the current timestamp for the 'updated_at' column
    current_timestamp = datetime.utcnow().isoformat() + "Z"

    # Iterate through each model in the input CSV
    for _, row in models_df.iterrows():
        model_name = row['model_name']
        url = row['primary_benchmark_url']
        param_B = row.get('param_B') # Use .get() for optional columns
        country = row.get('country')

        if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            print(f"Skipping invalid URL for {model_name}: {url}")
            continue

        print(f"Processing {model_name} from {url}...")

        try:
            # Fetch the benchmark file from the URL
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # --- Data Extraction Logic ---
            if 'json' in response.headers.get('Content-Type', '') or url.endswith('.json'):
                try:
                    data = response.json()
                    # Handle the specific structure of OpenVLM.json
                    if 'results' in data:
                        for model_key, benchmarks in data['results'].items():
                            # Check if the model from the JSON matches the one from the CSV
                            if model_name.lower() in model_key.lower():
                                for benchmark_name, scores in benchmarks.items():
                                    if isinstance(scores, dict) and 'Overall' in scores:
                                        score_data = {
                                            'model_name': model_name,
                                            'benchmark_name': benchmark_name,
                                            'score': scores['Overall'],
                                            'param_B': param_B,
                                            'country': country,
                                            'updated_at': current_timestamp
                                        }
                                        all_scores.append(score_data)
                                        print(f"  - Found score for {model_name}: {benchmark_name} -> {scores['Overall']}")
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON from {url} for {model_name}. Skipping.")

            # Placeholder for other file types (CSV, Parquet)
            # This section can be expanded to handle other data formats
            elif 'csv' in response.headers.get('Content-Type', '') or url.endswith('.csv'):
                print(f"Skipping CSV file for {model_name} at {url} (implementation pending).")

            elif url.endswith('.parquet'):
                print(f"Skipping Parquet file for {model_name} at {url} (implementation pending).")

            else:
                print(f"Skipping unsupported file type for {model_name} at {url}")
                continue

        except requests.exceptions.RequestException as e:
            print(f"Could not fetch URL {url} for {model_name}. Error: {e}. Skipping.")
        except Exception as e:
            # Catch other potential errors during file processing
            print(f"An error occurred while processing the file for {model_name}. Error: {e}. Skipping.")

    # After processing all models, create a final DataFrame and save to CSV
    if all_scores:
        output_df = pd.DataFrame(all_scores)
        # Ensure columns are in the desired order
        output_df = output_df[['model_name', 'benchmark_name', 'score', 'param_B', 'country', 'updated_at']]
        output_df.to_csv(output_csv_path, index=False)
        print(f"\nSuccessfully wrote {len(output_df)} scores to {output_csv_path}")
    else:
        print("\nNo scores were extracted. Output file not created.")

if __name__ == '__main__':
    # Assuming 'models.csv' is in the same directory as the script
    fetch_and_process_benchmarks('models.csv', 'scores.csv')