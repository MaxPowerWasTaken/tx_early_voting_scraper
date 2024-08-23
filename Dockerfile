FROM selenium/standalone-chrome:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy your application files
COPY . .

# Install Python and pip
USER root
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Create a virtual environment
RUN python3 -m venv /usr/src/app/venv

# Activate the virtual environment and install dependencies
RUN . /usr/src/app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Switch back to the selenium user
USER seluser

# Set the entrypoint to activate the venv and run your script
CMD ["/bin/bash", "-c", "source /usr/src/app/venv/bin/activate && python -m scrape_ev_files"]