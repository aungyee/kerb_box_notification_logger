FROM python:3.9.7

WORKDIR /kerb_box_notification_logger

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY /App .

CMD ["python","./app.py"]