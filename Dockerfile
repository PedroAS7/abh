FROM python:3-slim

WORKDIR /opt/abh
COPY main.py .
COPY requirements.txt .
COPY abh abh

RUN pip install -r requirements.txt
CMD [ "python", "main.py" ]