import pandas as pd 

from google.cloud import bigquery

def clean_datetime(df, column_name):
    """Converts a datetime column to New York time (handles DST),
    removes timezone info (tz-naive), and standardizes format.

    Args:
        df (pd.DataFrame): dataframe
        column_name (str): name of the datetime column to clean
    """
    # Convert to datetime if not already
    df[column_name] = pd.to_datetime(df[column_name], errors='coerce', utc=True)

    # Convert to America/New_York timezone (handles DST)
    df[column_name] = df[column_name].dt.tz_convert('America/New_York')

    # Remove timezone info (tz-naive)
    df[column_name] = df[column_name].dt.tz_localize(None)

    return df.head()

def upload_to_bigquery(df, table_name, project_id, dataset_id):
    """Upload the data into GCP Bigquery

    Args:
        df (pd.DataFrame): data files in the data folder
        table_name (str): name of the bigquery table
        project_id (str): project id
        dataset_id (str): BigQuery dataset name
        There is a project, inside project there is a dataset, inside dataset there are these tables
    """
    client = bigquery.Client(project=project_id)

    table_id = f"{project_id}.{dataset_id}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite if table exists
        autodetect=True,                     # Infer schema from DataFrame
    )

    job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    )

    job.result()  # Wait for the job to complete
    print(f"Uploaded {table_name} to BigQuery: {table_id}")
    
    
# channel_df = pd.read_csv('data/channels/2025-05-21_channel_data.csv')
# PROJECT_ID="youtube-analytics-459121"
# DATASET_ID="youtube_data"

# upload_to_bigquery(channel_df, 'channel_data', PROJECT_ID, DATASET_ID)