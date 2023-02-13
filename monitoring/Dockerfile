FROM python:3.8

# set working directory
WORKDIR /monitoring

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# add and install requirements
COPY requirements.txt /monitoring/requirements.txt
RUN pip install -r requirements.txt
RUN pip install influxdb-client

COPY online_evaluation.py /monitoring/online_evaluation.py

CMD ["python", "online_evaluation.py"]