FROM quay.io/astronomer/astro-runtime:12.7.1
RUN pip install dbt-core dbt-snowflake


# install dbt into a venv to avoid package dependency conflicts
#WORKDIR "/usr/local/airflow"
#COPY dbt-requirements.txt ./
#RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
 #   pip install --no-cache-dir -r dbt-requirements.txt && deactivate


    # replace dbt-postgres with another supported adapter if you're using a different warehouse type
#RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
#pip install --no-cache-dir dbt-snowflake && deactivate