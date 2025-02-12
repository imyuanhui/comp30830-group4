# comp30830-group4
## Setting Up a Virtual Environment
1. Open a terminal.
2. Run the following command to create a virtual environment with all required packages:
   ```bash
   conda env create -f environment.yml
   ```
3. Activate the virtual environment:
   ```bash
   conda activate seg4
   ```
4. To update the `environment.yml` file with the current environment’s packages:
   ```bash
   conda env export > environment.yml
   ```

## Configuring Your Credentials
1. Copy the `example_config.json` file and rename it to `config.json`.
2. Open the `config.json` file and fill in all the required credentials.
3. If you create a new connection, add the corresponding format in the `example_config.json` file to ensure consistency.
    - ⚠ **Important:** Do not upload your `config.json` file to the GitHub repository to protect sensitive information.