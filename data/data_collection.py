"""
KAFKA CONSUMER
reads produced logs from server, cleans and stores the data on mongodb
"""

import logging
import configparser
import pathlib

from confluent_kafka import Consumer
from data.data_schemas import Rating, WatchHistory, Clip
from data.data_cleaning import DataCleaning

log = logging.getLogger()
log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


class MovieLogConsumer:
    config = configparser.ConfigParser()

    def __init__(self, test=False):
        self.config.read(pathlib.Path(__file__).parent.parent / "config" / 'config.ini')
        self.test = test
        self.dataCleaning = DataCleaning(True)

        if self.test:
            # For testing no need to create the consumer since will be feeding lines of text to the tested components
            pass

        else:
            # Create kafka consumer
            self.c = Consumer({
                'bootstrap.servers': self.config['kafka']['bootstrap.servers'],
                'group.id': 'mygroup',
                'auto.offset.reset': self.config['kafka']['offset']
            })
            self.c.subscribe([self.config['kafka']['topic']])

    def processRateRequest(self, line: str):

        print("===RATE==")
        timestamp = line.split(",")[0]
        user_id = line.split(",")[1]
        tmp = line.split("/")[2]
        movie_id = tmp.split("=")[0]
        rate = tmp.split("=")[1]

        rating = Rating(
            user_id=user_id,
            movie_id=movie_id,
            timestamp=timestamp,
            rate=rate
        )

        try:
            if not self.test:
                if not (self.dataCleaning.verifyMovieExistsSave(movie_id) and self.dataCleaning.verifyUserExistsSave(
                        int(user_id))):
                    print("User or movie ids do not exists")
                    pass
                # Built-in validation
                # in testing just validate but do not save record
                rating.validate()
                Rating \
                    .objects(user_id=user_id, movie_id=movie_id) \
                    .update_one(set__rate=rate, set__timestamp=timestamp, upsert=True)
            else:
                # in testing just validate but do not save record
                rating.validate()

        except Exception as e:
            print("Error: \n%s" % e)
            return {}

        return rating

    def processDataRequest(self, line: str):

        print("===DATA==")
        timestamp = line.split(",")[0]
        user_id = line.split(",")[1]
        movie_id = line.split("/")[3]
        clip = line.split("/")[4]

        try:
            if not self.test:
                if not (self.dataCleaning.verifyMovieExistsSave(movie_id) and
                        self.dataCleaning.verifyUserExistsSave(int(user_id))):
                    print("User or movie ids do not exists")
                    pass

            clip = Clip(
                timestamp=timestamp,
                clip=clip
            )

            watch = WatchHistory(
                user_id=user_id,
                movie_id=movie_id,
                clips=[clip]
            )

            watch.validate()

            # Built-in validation
            WatchHistory \
                .objects(user_id=user_id, movie_id=movie_id) \
                .update_one(push__clips=clip, upsert=True)

            print(watch)
            return watch

        except Exception as e:
            print("Error: \n%s" % e)
            return {}

    def _get_kafka_consumer(self):
        return self.c

    def startConsumer(self):
        while True:

            msg = self.c.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue

            if self.test:
                line = msg
            else:
                line = msg.value().decode('utf-8')
                print(line)

            request_type = line.split("/")[1]
            if request_type == "rate":
                self.processRateRequest(line)
            if request_type == "data":
                self.processDataRequest(line)

        self.c.close()


class DataCollection:
    def __init__(self, test=False):
        self.test = test

    def run(self):
        # Launch kafka stream consumer that only persists correct data
        movielogConsumer = MovieLogConsumer(self.test)
        movielogConsumer.startConsumer()


if __name__ == '__main__':
    movielogConsumer = MovieLogConsumer()
    movielogConsumer.startConsumer()
