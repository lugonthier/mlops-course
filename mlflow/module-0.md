# MLflow Tracking Server: Installation and Launch Guide

This guide provides step-by-step instructions to install MLflow and launch its tracking server.

## 1. Prerequisites

Before you begin, ensure you have Python and pip (Python package installer) installed on your system. You can verify their installation by running:

```bash
python --version
pip --version
```

If they are not installed, please install them first. Instructions can be found on the official Python website.

## 2. Installing MLflow

MLflow can be installed using pip. Open your terminal or command prompt and run:

```bash
pip install mlflow
```

This command will download and install the latest version of MLflow and its dependencies.

To install a specific version, you can use:
```bash
pip install mlflow==<version_number> # e.g., pip install mlflow==2.3.0
```

## 3. Launching the MLflow Tracking Server

The MLflow tracking server logs parameters, code versions, metrics, and output files when running your machine learning code and later visualizes the results.

The basic command to start the tracking server is:

```bash
mlflow server
```

By default, this command starts the server on `http://127.0.0.1:5000` (or `http://localhost:5000`). It will create a local `./mlruns` directory in the location where you run the command to store experiment and run data (metadata and artifacts).

### Common Configurations

You can customize the server's behavior using various options:

*   `--host <hostname>`: The network address to listen on (e.g., `0.0.0.0` to listen on all addresses). Default: `127.0.0.1`.
*   `--port <port_number>`: The port to listen on. Default: `5000`.
*   `--backend-store-uri <uri>`: Specifies the backend store for metadata. This can be a local file path or a database connection string.
*   `--default-artifact-root <uri>`: Specifies the URI where artifacts should be stored. This can be a local directory or a cloud storage location (e.g., `s3://my-mlflow-artifacts/`).

#### Example 1: File Backend with Custom Artifact Root

This launches the server, stores metadata in a local directory named `my_mlflow_server_data`, and stores artifacts in a separate local directory `my_mlflow_artifacts`.

```bash
mkdir my_mlflow_server_data
mkdir my_mlflow_artifacts

mlflow server \
    --backend-store-uri ./my_mlflow_server_data \
    --default-artifact-root ./my_mlflow_artifacts \
    --host 0.0.0.0 \
    --port 5001
```
The server will be accessible at `http://<your-machine-ip>:5001`. If run locally, it will be `http://localhost:5001`.

#### Example 2: SQLite Backend with Default Artifact Root in a Specific Location

This uses an SQLite database file (`mlflow.db` in the current directory) for metadata and a specific local folder for artifacts.

```bash
# For SQLite, you might need to install the SQLAlchemy dialect:
# pip install sqlalchemy psycopg2-binary # Example for PostgreSQL, for SQLite it's usually included or simple
# For SQLite, no extra package is typically needed beyond sqlalchemy (often a mlflow dependency)

mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlflow_artifacts_location \
    --host 0.0.0.0 \
    --port 5000
```
This will create `mlflow.db` in the directory where you ran the command and store artifacts in `./mlflow_artifacts_location/`.

**Note on Database Backends:**
For other database backends like PostgreSQL or MySQL, you would provide the appropriate SQLAlchemy-compatible database URI and ensure the necessary database drivers are installed in your Python environment (e.g., `psycopg2-binary` for PostgreSQL, `mysqlclient` for MySQL).

Example for PostgreSQL:
```bash
# pip install psycopg2-binary
mlflow server \
    --backend-store-uri postgresql://user:password@host:port/database_name \
    --default-artifact-root s3://my-mlflow-bucket/artifacts \
    --host 0.0.0.0
```

## 4. Accessing the MLflow UI

Once the server is running, open your web browser and navigate to the address shown in the terminal (e.g., `http://127.0.0.1:5000` or the custom host/port you specified).

You will see the MLflow UI, where you can track experiments, compare runs, and view artifacts.

## 5. Stopping the MLflow Server

To stop the MLflow server, go to the terminal where it is running and press `Ctrl+C`.

This concludes the basic guide to installing and launching an MLflow tracking server. For more advanced configurations and features, refer to the official MLflow documentation.
