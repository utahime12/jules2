import gradio as gr
import subprocess
import sys # Required for path manipulation if running convert_onnx.py with a specific python interpreter
import os # Required for path manipulation

# USAGE:
# 1. Ensure 'convert_onnx.py' is in the same directory as this script.
# 2. Ensure all dependencies for 'convert_onnx.py' (e.g., PyTorch, ONNX, aivmlib, style_bert_vits2)
#    and this script (`gradio`) are installed in your Python environment.
# 3. Run this script from your terminal: python webui_convert_onnx.py
# 4. Open the URL displayed in your terminal (usually http://127.0.0.1:7860) in a web browser.
# 5. Use the interface to specify the model path, conversion options, and view logs.

# This Web UI script requires Gradio to be installed (`pip install gradio`).
# The underlying 'convert_onnx.py' script has its own set of dependencies
# (such as PyTorch, ONNX, onnxsim, rich, style_bert_vits2, aivmlib).
# Please ensure these are installed in your Python environment if you encounter
# errors reported in the log during conversion.

import gradio as gr # This import was missing in the search pattern, but needs to be here.
import subprocess
import sys # Required for path manipulation if running convert_onnx.py with a specific python interpreter

def run_conversion_script(model_path, force_convert, generate_aivm, generate_aivmx):
    log_output = ""
    try:
        if not model_path:
            yield "Error: Model Path or Directory cannot be empty."
            return

        script_path = "convert_onnx.py"
        if not os.path.exists(script_path):
            yield f"Error: The script '{script_path}' was not found in the current directory ({os.getcwd()}). Make sure it's present."
            return

        command = [sys.executable, "-u", script_path, "--model", model_path]

        if force_convert:
            command.append("--force-convert")
        if generate_aivm:
            command.append("--aivm")
        if generate_aivmx:
            command.append("--aivmx")

        log_output += f"Running command: {' '.join(command)}\n\n"
        yield log_output

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                log_output += line
                yield log_output

        process.wait() # Wait for the process to complete

        if process.returncode == 0:
            log_output += "\n\nConversion process completed successfully."
        else:
            log_output += f"\n\nConversion process failed with exit code {process.returncode}."

        yield log_output

    except FileNotFoundError: # Should be caught by os.path.exists now, but as a fallback
        log_output += f"Error: The script 'convert_onnx.py' was not found. Make sure it's in the same directory as the web UI script.\n"
        yield log_output
    except Exception as e:
        log_output += f"\nAn unexpected error occurred: {str(e)}\n"
        yield log_output

    # Final update
    yield log_output

# Placeholder for the Gradio interface
if __name__ == "__main__":
    with gr.Blocks() as iface:
        gr.Markdown("""
# ONNX Model Conversion Web UI
Ensure `convert_onnx.py` is in the same directory as this web UI script.
If the conversion fails, check the log for errors. These might indicate missing dependencies for `convert_onnx.py` (e.g., PyTorch, ONNX, aivmlib).
This Web UI itself requires Gradio (`pip install gradio`).
""")
        with gr.Row():
            model_path_input = gr.Textbox(label="Model Path or Directory", placeholder="Enter path to .safetensors file or directory containing models")
        with gr.Row():
            force_convert_checkbox = gr.Checkbox(label="Force Convert (overwrite existing ONNX)", value=False)
        with gr.Row():
            aivm_checkbox = gr.Checkbox(label="Generate AIVM (from Safetensors)", value=False)
        with gr.Row():
            aivmx_checkbox = gr.Checkbox(label="Generate AIVMX (from ONNX)", value=False)
        with gr.Row():
            run_button = gr.Button("Run Conversion")
        with gr.Row():
            output_log = gr.Textbox(label="Output Log", lines=20, interactive=False, autoscroll=True)

        run_button.click(
            fn=run_conversion_script,
            inputs=[model_path_input, force_convert_checkbox, aivm_checkbox, aivmx_checkbox],
            outputs=output_log
        )

        iface.launch() # Add this line to launch the app
        print("Gradio UI launched.") # Optional: for console confirmation
