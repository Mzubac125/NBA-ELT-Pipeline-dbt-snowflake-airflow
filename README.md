# Analytics Engineering Project: ELT Pipeline for NBA Statistics

## Project Overview
The goal of this project is to collect and process NBA data from online sources, transforming it into structured insights for analysis and visualization.

<img width="914" alt="Image" src="https://github.com/user-attachments/assets/38ec643a-c984-4e72-881b-5705162b753e" />


Video Link: https://youtu.be/r7WqfFBfnL8?si=BEgQWIaixTl1HQJe


## Tech Stack
* DBT (Data Build Tool): Data transformations
* Airflow: Workflow orchestration and scheduling
* Python: Web scraping, scripting, and automation
* Azure Blob Storage: Cloud storage for raw data
* Snowflake: Data warehousing
* SQL: Database querying
* Azure Data Factory (ADF): Converting CSV files to Parquet format

## Data Source
I web scraped player statistics and salary data from [Basketball Reference](https://www.basketball-reference.com/) using Python and BeautifulSoup.

## Data Ingestion and Storage
* Apache Airflow is used to orchestrate the data pipeline. Airflow automates extracting the player statistics and salary data from Basketball Reference.
* The extracted data is then stored in an Azure Data Lake, which serves as the staging area for the raw data.

## Data Format Conversion
I used Azure Data Factory to convert raw CSV files into Parquet format, enabling more efficient storage and faster query performance for downstream processing.

## Data Warehousing
From Azure DLS, the data is loaded into Snowflake, a cloud-based data warehousing solution.

## Data Transformation
I used dbt for my data transformation because dbt enables modular, version-controlled SQL development directly within the Snowflake environment. This setup allowed me to build reliable, well-documented data models, implement automated testing, and ensure efficient, scalable transformations using Snowflake’s compute power.

## Data Visualization
Once the data is transformed and stored in Snowflake, Tableau is used for creating visualizations, dashboards, and reports. This step enables stakeholders to derive insights from the NBA data.

![Image](https://github.com/user-attachments/assets/f0005bf2-730f-4915-8fc2-0f3e54c7a547)
