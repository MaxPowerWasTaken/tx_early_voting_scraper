FROM selenium/standalone-chrome:latest

# tip from https://stackoverflow.com/a/78936680/1870832 regarding this particular base image
ENV SE_OFFLINE=false

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
#USER seluser  - got permission denied error when running os.path.remove()

# Set the entrypoint to activate the venv and run your script
CMD ["/bin/bash", "-c", "source /usr/src/app/venv/bin/activate && python -m scrape_ev_files"]