# TX Early Voting Scraper
## Python Environment
This project uses `uv` for virtual environment management. If you don't have `uv` already, see install instructions [here](https://pypi.org/project/uv/)

To create a new virtual environment and install dependencies, run the following from your shell:
```bash
# Create a virtual environment at .venv.
uv venv

# Activate the virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate On Windows.

# Install from a requirements.txt file.
uv pip install -r requirements.txt  
```

## Usage 
To run the scraper, downloading Early Voter files, appending them together and uploading the results to BQ, run:
```bash
python scrape_ev_files.py
```

## Run in local docker (for debugging)
Build with `docker build -t tx_early_voting_scraper .` 
and run with `docker run tx_early_voting_scraper`

Hop into an interactive shell with (after building): `docker run -it tx_early_voting_scraper /bin/bash`