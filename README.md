# FastAPI User Management System

## Project Setup

### Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.8 or later
- pip (Python package installer)

### Install Dependencies


1. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:
    - **On Windows:**
      ```bash
      venv\Scripts\activate
      ```
    - **On macOS/Linux:**
      ```bash
      source venv/bin/activate
      ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configure the Database

Ensure your database settings are correctly configured in the `app/database.py` file. This project uses SQLAlchemy to connect to the database.

## Running the Application

1. Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```

2. Open your web browser and go to `http://127.0.0.1:8000` to access the application.
