FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app

# copy src folder and requirements.txt
COPY src/ /usr/src/app/src/
COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

RUN true && \
	apt update && \
	apt install -y wget procps vim ffmpeg && \
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
	dpkg -i google-chrome-stable_current_amd64.deb || apt --fix-broken install -y && \
	rm -rf google-chrome-stable_current_amd64.deb
RUN true && \
	cd /usr/local/lib/python3.10/site-packages/DrissionPage/_configs/ && \
	sed -i "/browser_path/s/$(grep 'browser_path' 'configs.ini' | awk -F '=' '{print $2}')/\/usr\/bin\/google-chrome/" configs.ini && \
	sed -i "/arguments/s/\[/\[\'--no-sandbox\', \'--headless=new\', /" configs.ini


EXPOSE 8000

CMD ["python", "src/main.py"]
