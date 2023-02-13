"""
Verifying consumed data with API
"""
import configparser
import pathlib
import requests
from data.data_schemas import Movie, User


class DataCleaning:
    config = configparser.ConfigParser()

    def __init__(self, test=False):
        self.config.read(pathlib.Path(__file__).parent.parent / "config" / 'config.ini')
        self.test = test

    def verifyMovieExistsSave(self, movie_id: str):
        response = {}

        if self.test:
            # if we are testing, since CircleCI does not have access to server,
            # we are going to verify movies exist in MongoDB
            print("Movie exists")
            print(movie_id)
            print(Movie.objects(movie_id=movie_id))
            return Movie.objects(movie_id=movie_id).count() == 1
        try:
            response = requests.get(self.config['serverApi']['url'] + "/movie/" + movie_id)

        except Exception as e:
            print("API Connection error: \n%s" % e)

        response = response.json()
        if "id" in response and (not Movie.objects(movie_id=movie_id)):
            data = response
            data['movie_id'] = data['id']
            del data['id']
            try:
                Movie(**data).save()
            except Exception as e:
                print("Schema error: \n%s" % e)
        return "id" in response

    def verifyUserExistsSave(self, user_id: int):
        response = {}

        if self.test:
            # if we are testing, since CircleCI does not have access to server,
            # we are going to verify users exist in MongoDB
            return User.objects(user_id=user_id).count() == 1
        try:
            response = requests.get(self.config['serverApi']['url'] + "/user/" + str(user_id)).json()
        except Exception as e:
            print("API Connection error: \n%s" % e)

        response = response.json()
        if "user_id" in response and (not User.objects(user_id=user_id)):
            try:
                User(**response).save()
            except Exception as e:
                print("Schema error: \n%s" % e)
        return "user_id" in response
