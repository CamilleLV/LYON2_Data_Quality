# Base image: Official Apache Airflow
FROM apache/airflow:2.7.1

# Switch to root to install system dependencies (if needed)
USER root
# (Optional) Install git or other system tools here if required
# RUN apt-get update && apt-get install -y git

# Switch back to the airflow user for Python package installation
USER airflow

# Copy the requirements file into the container
COPY requirements.txt /requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt