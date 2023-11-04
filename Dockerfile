FROM python:3.12-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging (same as -u)
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app

RUN pip install -U pip
RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --only main

CMD [ "python3", "main.py" ]
