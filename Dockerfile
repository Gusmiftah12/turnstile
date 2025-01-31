FROM python:3.10-alpine

WORKDIR /usr/src/app

# Install dependencies
RUN apk add --no-cache \
    ffmpeg \
    chromium \
    chromium-chromedriver \
    && rm -rf /var/cache/apk/*

# Copy source code
COPY src/ /usr/src/app/src/
COPY requirements.txt /usr/src/app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Update browser path in configs.ini
RUN sed -i "s|browser_path = .*|browser_path = /usr/bin/chromium-browser|" \
    /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini && \
    sed -i "s|\[\]|['--no-sandbox', '--headless=new']|" \
    /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/configs.ini

EXPOSE 8000

CMD ["python", "src/main.py"]
