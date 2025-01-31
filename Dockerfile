# Use a minimal Python image
FROM python:3.10-slim-bullseye  

WORKDIR /usr/src/app  

# Copy src folder and requirements.txt
COPY src/ /usr/src/app/src/  
COPY requirements.txt /usr/src/app/requirements.txt  

# Install only necessary dependencies and clean up cache
RUN apt update && apt install -y --no-install-recommends \
    wget \
    procps \
    vim \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*  

# Download and install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb  

# Install Python dependencies with no cache
RUN pip install --no-cache-dir -r requirements.txt  

# Modify DrissionPage config
RUN sed -i "/browser_path/s/$(grep 'browser_path' /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini | awk -F '=' '{print $2}')/\/usr\/bin\/google-chrome/" /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini && \
    sed -i "/arguments/s/\[/\[\'--no-sandbox\', \'--headless=new\', /" /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini  

EXPOSE 8000  

CMD ["python", "src/main.py"]  
