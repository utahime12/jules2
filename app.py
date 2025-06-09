from flask import Flask, request, jsonify
import subprocess
import sys
import os
from flask_cors import CORS # For handling Cross-Origin Resource Sharing

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/convert', methods=['POST'])
def convert_model():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided in request."}), 400

        model_path = data.get('model_path')
        force_convert = data.get('force_convert', False)
        generate_aivm = data.get('generate_aivm', False)
        generate_aivmx = data.get('generate_aivmx', False)

        if not model_path:
            return jsonify({"status": "error", "message": "model_path is required."}), 400

        # Basic security check: Ensure model_path is not trying to access parent directories excessively
        # This is a very basic check; for production, more robust path validation/sandboxing is needed.
        if ".." in model_path:
             # A more sophisticated check might involve resolving the absolute path
             # and ensuring it's within an allowed directory.
            app.logger.warning(f"Potentially unsafe model_path detected: {model_path}")
            # For now, we'll allow it but log it. Consider stricter rules for production.
            # Depending on requirements, you might want to reject paths with ".."

        # Path to the convert_onnx.py script. Assumed to be in the same directory as app.py
        # For robustness, construct path relative to app.py's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "convert_onnx.py")

        if not os.path.exists(script_path):
            app.logger.error(f"Script not found: {script_path}")
            return jsonify({"status": "error", "message": f"Conversion script '{os.path.basename(script_path)}' not found on server."}), 500

        # Ensure the python executable used is the one for the current environment,
        # especially if running in a virtual environment.
        python_executable = sys.executable

        command = [python_executable, "-u", script_path, "--model", model_path]

        if force_convert:
            command.append("--force-convert")
        if generate_aivm:
            command.append("--aivm")
        if generate_aivmx:
            command.append("--aivmx")

        app.logger.info(f"Executing command: {' '.join(command)}")

        # Using subprocess.run to capture output
        # Set a timeout (e.g., 5 minutes = 300 seconds) to prevent runaway processes
        timeout_seconds = 300
        process = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, check=False)

        log_output = f"--- STDOUT ---\n{process.stdout}\n"
        if process.stderr:
            log_output += f"--- STDERR ---\n{process.stderr}\n"

        app.logger.info(f"Script stdout: {process.stdout}")
        if process.stderr:
            app.logger.info(f"Script stderr: {process.stderr}")


        if process.returncode == 0:
            app.logger.info("Conversion script completed successfully.")
            return jsonify({
                "status": "success",
                "message": "Conversion process completed.",
                "log": log_output
            })
        else:
            app.logger.error(f"Conversion script failed with exit code {process.returncode}.")
            return jsonify({
                "status": "error",
                "message": f"Conversion process failed with exit code {process.returncode}.",
                "log": log_output
            }), 500 # Internal Server Error status for script failure

    except subprocess.TimeoutExpired:
        app.logger.error(f"Conversion script timed out after {timeout_seconds} seconds.")
        return jsonify({
            "status": "error",
            "message": f"Conversion process timed out after {timeout_seconds} seconds. The process may be too long or stuck.",
            "log": f"Process timed out. Command: {' '.join(command)}"
        }), 500
    except FileNotFoundError as e:
        # This might catch if python_executable itself is not found, though unlikely.
        # Or if convert_onnx.py path is somehow incorrect despite earlier check (e.g. during subprocess.run)
        app.logger.error(f"File not found during subprocess execution: {e}")
        return jsonify({"status": "error", "message": f"Error during script execution: {e}. Ensure Python and the script path are correct."}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True) # exc_info=True will log traceback
        return jsonify({"status": "error", "message": f"An unexpected server error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # It's good practice to enable debugging for development, but ensure it's off for production.
    # Using a logger is better than print for server applications.
    app.run(debug=True, host='0.0.0.0', port=5000)
