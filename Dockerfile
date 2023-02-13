FROM biggates/uvicorn-gunicorn-fastapi-science:python3.8
WORKDIR .
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install influxdb-client

ENV port 8082

# Running the consumer to get the data
CMD python app.py $port