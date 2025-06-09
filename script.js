document.addEventListener('DOMContentLoaded', () => {
    const modelPathInput = document.getElementById('model_path');
    const forceConvertCheckbox = document.getElementById('force_convert');
    const generateAivmCheckbox = document.getElementById('generate_aivm');
    const generateAivmxCheckbox = document.getElementById('generate_aivmx');
    const runConversionButton = document.getElementById('run_conversion_button');
    const outputLogArea = document.getElementById('output_log_area');

    runConversionButton.addEventListener('click', async () => {
        const modelPath = modelPathInput.value;
        const forceConvert = forceConvertCheckbox.checked;
        const generateAivm = generateAivmCheckbox.checked;
        const generateAivmx = generateAivmxCheckbox.checked;

        if (!modelPath.trim()) {
            outputLogArea.textContent = 'Error: Model Path or Directory cannot be empty.';
            return;
        }

        // Clear previous logs and indicate processing
        outputLogArea.textContent = 'Processing... Please wait.\n';
        runConversionButton.disabled = true; // Disable button during processing

        const requestData = {
            model_path: modelPath,
            force_convert: forceConvert,
            generate_aivm: generateAivm,
            generate_aivmx: generateAivmx
        };

        try {
            // Assuming the Flask server is running on http://127.0.0.1:5000
            // Adjust if your Flask server runs on a different port/host.
            const response = await fetch('http://127.0.0.1:5000/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            });

            runConversionButton.disabled = false; // Re-enable button

            outputLogArea.classList.remove('error'); // Remove error class first
            const result = await response.json();

            let logContent = `Status: ${result.status}\nMessage: ${result.message}\n`;
            if (result.log) {
                logContent += `--- Log Output ---\n${result.log}`;
            } else if (result.data_received) { // For the initial placeholder response
                logContent += `Data sent: ${JSON.stringify(result.data_received, null, 2)}\n`;
            }
            outputLogArea.textContent = logContent;

            if (response.ok && result.status === 'success') {
                // Success: ensure no error styling
                outputLogArea.classList.remove('error');
                console.log('Conversion successful:', result);
            } else {
                // Error: add error styling
                outputLogArea.classList.add('error');
                console.error('Conversion failed or error in response:', result);
            }

        } catch (error) {
            runConversionButton.disabled = false; // Re-enable button on error
            outputLogArea.classList.add('error'); // Add error class
            console.error('Error during fetch operation:', error);
            outputLogArea.textContent = `An error occurred while communicating with the server: ${error.message}\nCheck if the backend server is running and accessible.`;
        }
    });
});
