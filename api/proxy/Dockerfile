FROM biggates/uvicorn-gunicorn-fastapi-science:python3.8
WORKDIR .
COPY . .
RUN pip install --upgrade pip
RUN pip install flask
# Running the consumer to get the data
CMD python proxy.py