# Use a minimal Python image
FROM python:3.10-slim-bullseye  

WORKDIR /usr/src/app  

# Install required system dependencies first
RUN apt update && apt install -y --no-install-recommends \
    wget \
    procps \
    vim \
    ffmpeg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*  

# Download and install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb  

# Copy source files
COPY src/ /usr/src/app/src/  
COPY requirements.txt /usr/src/app/requirements.txt  

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt  

# Modify DrissionPage config
RUN sed -i "/browser_path/s/$(grep 'browser_path' /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini | awk -F '=' '{print $2}')/\/usr\/bin\/google-chrome/" /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini && \
    sed -i "/arguments/s/\[/\[\'--no-sandbox\', \'--headless=new\', /" /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini  

EXPOSE 8000  

CMD ["python", "src/main.py"]  
