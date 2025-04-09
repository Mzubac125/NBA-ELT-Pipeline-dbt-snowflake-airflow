# NBA-ELT-Pipeline-dbt-snowflake-airflow
This project demonstrates an end-to-end ELT data pipeline for processing NBA data. I began by web scraping player statistics and salary data from [Basketball Reference](https://www.basketball-reference.com/) using Python and BeautifulSoup. The raw data was saved as CSV files and uploaded to Azure Data Lake for cloud storage. Using Azure Data Factory (ADF), I built a pipeline to convert the CSV files into Parquet format, optimizing the data for analytics and storage efficiency. The Parquet files were then loaded into Snowflake, a cloud-based data warehouse, using an Airflow-managed ELT process. From there, I used dbt (Data Build Tool) to transform the raw data in Snowflake into clean, analysis-ready models. Finally, I connected the curated data to Tableau and built an interactive dashboard to visualize player performance and salary trends.

## Project Overview
The goal of this project is to collect and process NBA data from online sources, transforming it into structured insights for analysis and visualization.

<img width="914" alt="Image" src="https://github.com/user-attachments/assets/38ec643a-c984-4e72-881b-5705162b753e" />

## Tech Stack
* DBT (Data Build Tool): Data transformations
* Airflow: Workflow orchestration and scheduling
* Python: Web scraping, scripting, and automation
* Azure Blob Storage: Cloud storage for raw data
* Snowflake: Data warehousing
* SQL: Database querying
* Azure Data Factory (ADF): Converting CSV files to Parquet format
