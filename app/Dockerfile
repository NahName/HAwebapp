FROM python:3.7

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install gunicorn
ENV FLASK_APP /app/main.py

CMD gunicorn --bind 0.0.0.0:5000 main:app

EXPOSE 5000
