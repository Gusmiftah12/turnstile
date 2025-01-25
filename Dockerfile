FROM sanicframework/sanic:3.8-latest

WORKDIR /sanic

# copy src folder and requirements.txt
COPY src/ /sanic/src/
COPY requirements.txt /sanic/requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "src/main.py"]
