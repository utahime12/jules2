# ONNX Model Conversion Web Application

This application provides a web interface to convert `.safetensors` models to ONNX format using a Python backend and a simple HTML/JavaScript frontend.

## Files

-   `convert_onnx.py`: The core Python script that performs the model conversion. Contains logic for ONNX export and optimization, and AIVM/AIVMX metadata generation.
-   `app.py`: A Flask-based Python backend server that provides an API endpoint (`/convert`) to trigger the `convert_onnx.py` script.
-   `index.html`: The main HTML file for the frontend user interface.
-   `script.js`: JavaScript file for frontend logic (handling user input, communication with the backend).
-   `style.css`: CSS file for basic styling of the frontend.

## Prerequisites

1.  **Python:** Ensure you have Python 3.7+ installed.
2.  **Pip:** Python's package installer, usually comes with Python.
3.  **`convert_onnx.py` script:** This script must be present in the same directory as `app.py`.

## Setup and Installation

1.  **Clone/Download Files:**
    Make sure you have all the application files (`app.py`, `convert_onnx.py`, `index.html`, `script.js`, `style.css`) in the same directory.

2.  **Install Backend Dependencies:**
    Navigate to the application directory in your terminal and install the required Python packages for the Flask backend and the conversion script:
    ```bash
    pip install Flask flask-cors torch onnx onnxsim rich style-bert-vits2 aivmlib
    ```
    *(Note: `style-bert-vits2` and `aivmlib` are based on the imports in `convert_onnx.py`. If these are part of a larger local package or have different installation names, adjust accordingly. Ensure all dependencies for `convert_onnx.py` are met.)*

## Running the Application

1.  **Start the Backend Server:**
    Open your terminal, navigate to the application directory, and run the Flask server:
    ```bash
    python app.py
    ```
    You should see output indicating the server is running, typically on `http://127.0.0.1:5000/` or `http://0.0.0.0:5000/`.

2.  **Open the Frontend in Your Browser:**
    Open your web browser (like Chrome, Firefox, etc.) and navigate to the `index.html` file. You can usually do this by:
    *   Double-clicking the `index.html` file in your file explorer.
    *   Or, if your browser requires it to be served (less common for simple setups like this without JS modules), you might need a simple HTTP server for the frontend files. However, direct opening should work for this application.

    The application will attempt to connect to the backend at `http://127.0.0.1:5000`.

## How to Use

1.  Once the backend is running and `index.html` is open in your browser:
2.  **Enter Model Path:** In the "Model Path or Directory" field, provide the absolute path to your `.safetensors` model file or a directory containing such models.
    *   *Important:* The backend server needs to have access to this path. If running the server on your local machine, this means local paths. If the server is remote or in Docker, path considerations will be different.
3.  **Select Options:**
    *   Check "Force Convert" if you want to overwrite existing ONNX models.
    *   Check "Generate AIVM" to create an `.aivm` file from the Safetensors model.
    *   Check "Generate AIVMX" to create an `.aivmx` file from the generated ONNX model.
4.  **Run Conversion:** Click the "Run Conversion" button.
5.  **View Logs:** The output, progress, and any errors from the conversion script will appear in the "Output Log" area on the page.

## Troubleshooting

-   **`ModuleNotFoundError` in `app.py` console:** Ensure all backend dependencies (Flask, etc.) are installed in the Python environment you're using to run `app.py`.
-   **`ModuleNotFoundError` in web UI log:** This indicates `convert_onnx.py` (run by the backend) is missing dependencies (torch, onnx, etc.). Install them in the same Python environment.
-   **"Error during fetch operation" / Logs not appearing:**
    *   Make sure the Flask backend server (`app.py`) is running.
    *   Check your browser's developer console (usually F12) for network errors. The frontend tries to connect to `http://127.0.0.1:5000`. If your Flask server is on a different address/port, you'll need to update `script.js`.
    *   Ensure CORS is handled (it is by default in `app.py` with `flask-cors`).
-   **File Access Issues:** The path provided for models must be accessible by the Python script running on the server.
