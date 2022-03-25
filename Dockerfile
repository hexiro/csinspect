FROM python:3.10-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt

RUN [ "python3", "-m", "pip", "install", "-r", "requirements.txt" ]

COPY . /app

CMD [ "python3", "main.py" ]
