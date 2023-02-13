import confluent_kafka
from confluent_kafka import Consumer
import numpy as np
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

class OnlineEvaluation:
    # You can generate an API token from the "API Tokens Tab" in the UI
    token = "-fJqPJFLpjLUE3KAh6yBcdGHpf2QtQ_3DW7bEaUGIkIcHL2zdn_COSQFP7Ju4Sormx5DodZ1F7S93UU6oZLKCQ=="
    org = "szghab@gmail.com"
    bucket = "szghab's Bucket"
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"

    def __init__(self):
        self.client = influxdb_client.InfluxDBClient( url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        # Create kafka consumer
        self.c = Consumer({
            'bootstrap.servers': "fall2021-comp598.cs.mcgill.ca:9092",
            'group.id': 'mygroup',
            'auto.offset.reset': "latest"
        })

        def my_assign(consumer, partitions):
            for p in partitions:
                p.offset = confluent_kafka.OFFSET_END
            print('assign', partitions)
            consumer.assign(partitions)

        self.c.subscribe(["movielog3"], on_assign=my_assign)

    def store_evaluation(self, recommendations):
        precision, recall = 0, 0
        precisions = []
        recalls = []

        for user_id  in recommendations:
            recommendation = recommendations[user_id]
            print(recommendation)
            recommendations_movies = recommendation["recommendations"]

            watched_movies = {movie_id for movie_id, watch_time in recommendation["watch"].items() if watch_time >= 1}
            rated_movies = {movie_id for movie_id, rating in recommendation["rate"].items() if int(rating) >= 2}
            liked_movies = rated_movies.union(watched_movies)

            if len(liked_movies) > 0:
                precision = len(liked_movies.intersection(recommendations_movies)) / len(recommendations_movies)
                recall = len(liked_movies.intersection(recommendations_movies)) / len(liked_movies)

                precisions.append(precision)
                recalls.append(recall)

        if len(precisions) > 0:
            precision, recall = np.mean(precisions), np.mean(recalls)

        p = influxdb_client.Point("model_online_performance")\
            .tag("version", "v1.0.0")\
            .field("precision", precision)\
            .field("recall", recall)

        self.write_api.write(bucket=self.bucket, org=self.org, record=p)
        print("save to influxDB")


    def start(self):
        recommendations = dict()
        start_time = time.time()

        while True:

            msg = self.c.poll(1.0)
            if msg is None:
                continue

            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue

            line = msg.value().decode('utf-8')

            user_id = line.split(",")[1]
            
            if (line.split(",")[2].__contains__("GET")):
                if (line.split("/")[1] == "rate"):
                    movie_id = line.split("/")[2].split("=")[0]
                    rate = line.split("/")[2].split("=")[1]
                    if user_id in recommendations:
                        recommendations[user_id]["rate"][movie_id] = rate

                if (line.split("/")[1] == "data"):
                    movie_id = line.split("/")[3]
                    if user_id in recommendations:
                        if movie_id in recommendations[user_id]["watch"]:
                            recommendations[user_id]["watch"][movie_id] += 1
                        else:
                            recommendations[user_id]["watch"][movie_id] = 1



            if (line.split(",")[2].__contains__("recommendation")):

                if (line.split(",")[3] == " status 0"):
                    print("SERVICE FAILS")

                if (line.split(",")[3] == " status 400"):
                    print("ERROR")

                if (line.split(",")[3] == " status 200"):
                    # Save recommendation for user
                    movie_ids = line.split("status 200, result: ")[1].split(",")

                    recommendations[user_id] = {
                        "recommendations": movie_ids,
                        "rate": dict(),
                        "watch": dict()
                    }


            # Push metrics after a delay of 5s
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time > 120 :

                self.store_evaluation(recommendations)

                # reinit
                start_time = time.time()


        self.c.close()


if __name__ == '__main__':
    print("STARTING")
    eval_on = OnlineEvaluation()
    eval_on.start()