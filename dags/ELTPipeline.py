from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime, timedelta, date
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Constants
AZURE_PATH_STATS = 'nba_stats/'
AZURE_PATH_SALARIES = 'nba_salaries/'
LOCAL_PATH = '/tmp/'
AZURE_ACCOUNT_NAME = 'nbastorage'
AZURE_CONTAINER_NAME = 'nbastorage'
AZURE_CONN_ID = 'azure_blob_connection'

#Snowflake Constants
SNOWFLAKE_CONN_ID = 'snowflake_conn'
DATABASE = 'MASTER'
SCHEMA = 'STAGE'
STAGE = 'NBA_STATS_STAGE'
TABLE_STATS = 'NBA_STATS'
TABLE_SALARIES = 'SALARIES'

# Airflow DAG configuration
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 27),
    'retries': 0,
}

dag = DAG(
    'nba_data_pipeline',
    default_args=default_args,
    description='Fetch NBA data, upload to Azure',
    schedule_interval=None
)

def get_nba_stats():
    last_five_years = [date.today().year - i for i in range(5)]
    data_rows = []

    for year in last_five_years:
        URL = f'https://www.basketball-reference.com/leagues/NBA_{year}_totals.html'
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'lxml')
        results = soup.find('div', id='div_totals_stats')

        table_data = results.find_all('tr')
        for row in table_data[1:]:
            data = row.find_all('td')
            individual_data = [i.text for i in data]
            individual_data.append(year)
            data_rows.append(individual_data)

    #Get a list of all the headers
    data_headers = results.find_all('th', class_ = ['poptip center','poptip sort_default_asc center','ranker poptip sort_default_asc show_partial_when_sorting center','poptip hide_non_quals center','poptip sort_col center'])
    for row in data_headers:
        titles = [i.text for i in data_headers]
    titles.append('Year')


    df = pd.DataFrame(data_rows, columns=titles)
    df = df[df['Player'] != 'League Average']

    local_file_path = os.path.join(LOCAL_PATH, 'nba_stats.csv')
    df.to_csv(local_file_path, index=False)
    print(f'NBA stats saved to {local_file_path}')
    return local_file_path

def get_nba_salaries():
    
    URL = 'https://www.basketball-reference.com/contracts/players.html'
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'lxml')
    results = soup.find('div', id='div_player-contracts')

    table_data = results.find_all('tr')
    data_rows = []

    for row in table_data[2:]:
        #Find all table data
        data = row.find_all('td')
        individual_data = [i.text for i in data]
        #Add data to the empty list
        data_rows.append(individual_data)

    #Get headers
    data_headers = results.find_all('th', class_ = ['center','right', 'over_header center', 'sort_default_asc left'])
    for row in data_headers:
        titles = [i.text for i in data_headers]

    titles = titles[33:42]

    df = pd.DataFrame(data_rows, columns= titles)

    local_file_path = os.path.join(LOCAL_PATH, 'nba_salaries.csv')
    df.to_csv(local_file_path, index=False)
    print(f'NBA salaries saved to {local_file_path}')
    return local_file_path

def upload_to_azure(local_file_path, blob_name):
    """Upload file to Azure Blob Storage."""
    hook = WasbHook(AZURE_CONN_ID)
    hook.load_file(
        file_path=local_file_path,
        container_name=AZURE_CONTAINER_NAME,
        blob_name=blob_name,
        overwrite=True
    )
    print(f"Uploaded {local_file_path} to Azure Blob Storage as {blob_name}")

def load_data_to_snowflake(blob_name, table_name):
    """Loads data from Azure Blob Storage to Snowflake."""
    SQL_QUERY = f"""
        COPY INTO {DATABASE}.{SCHEMA}.{table_name}
        FROM @{STAGE}/{blob_name}
        FILE_FORMAT = (TYPE = 'PARQUET')
        MATCH_BY_COLUMN_NAME = case_insensitive;
    """
    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    hook.run(SQL_QUERY)
    print(f"Loaded data from {blob_name} into {table_name}.")


# Airflow Tasks
scrape_stats_task = PythonOperator(
    task_id='get_nba_stats',
    python_callable=get_nba_stats,
    dag=dag
)

scrape_salaries_task = PythonOperator(
    task_id='get_nba_salaries',
    python_callable=get_nba_salaries,
    dag=dag
)

upload_stats_task = PythonOperator(
    task_id='upload_nba_stats',
    python_callable=upload_to_azure,
    op_kwargs={
        'local_file_path': os.path.join(LOCAL_PATH, 'nba_stats.csv'),
        'blob_name': f"nba_stats/nba_stats_{date.today().year}.csv"
    },
    dag=dag
)

upload_salaries_task = PythonOperator(
    task_id='upload_nba_salaries',
    python_callable=upload_to_azure,
    op_kwargs={
        'local_file_path': os.path.join(LOCAL_PATH, 'nba_salaries.csv'),
        'blob_name': f"nba_salaries/nba_salaries_{date.today().year}.csv"
    },
    dag=dag
)

convert_csv_to_parquet_in_adf = AzureDataFactoryRunPipelineOperator(
    task_id="convert_csv_to_parquet",
    pipeline_name="nba_convert_csv_to_parquet",
    azure_data_factory_conn_id="azure_data_factory_conn",
    resource_group_name="nba-rg",
    factory_name="adf-nba-mzubac125",
    dag=dag
)

load_stats_task = PythonOperator(
    task_id='load_nba_stats_to_snowflake',
    python_callable=load_data_to_snowflake,
    op_kwargs={
        'blob_name': f"nba_stats/nba_stats.parquet",
        'table_name': TABLE_STATS
    },
    dag=dag
)

load_salaries_task = PythonOperator(
    task_id='load_nba_salaries_to_snowflake',
    python_callable=load_data_to_snowflake,
    op_kwargs={
        'blob_name': f"nba_salaries/nba_salaries.parquet",
        'table_name': TABLE_SALARIES
    },
    dag=dag
)
dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command=
        'cd /usr/local/airflow/dags/dbt/nba_stats && dbt run' 
    ,
    dag=dag,
)

# Set task dependencies
scrape_stats_task >> upload_stats_task >> convert_csv_to_parquet_in_adf >> load_stats_task
scrape_salaries_task >> upload_salaries_task >> convert_csv_to_parquet_in_adf >> load_salaries_task

[load_stats_task, load_salaries_task] >> dbt_run
