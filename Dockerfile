# Use an official Python image as the base image
FROM python:3.12.4

# WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY database.py .
COPY sqlalchemy_tomato.db .

RUN pip install --upgrade pip && pip install -r requirements.txt && rm -rf ~/.cache/pip

EXPOSE 80

CMD [ "python3", "main.py" ]