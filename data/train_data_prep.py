import json
import pathlib
import wandb

import pandas as pd
from pymongo import MongoClient
import configparser
from sklearn.model_selection import train_test_split


class TrainingDataPrep:
    config = configparser.ConfigParser()

    def __init__(self):
        self.config.read(pathlib.Path(__file__).parent.parent / "config" / "config.ini")
        # Open connection to mongoDB
        self.conn = MongoClient(self.config["mongoDB"]["host"])
        self.db = self.conn[self.config["mongoDB"]["db"]]

    def build_training_df(self):
        df_rating = pd.DataFrame(list(self.db["rating"].find()))
        df_watch = pd.DataFrame(list(self.db["watch_history"].find()))
        df_movie = pd.DataFrame(list(self.db["movie"].find()))
        df_user = pd.DataFrame(list(self.db["user"].find()))
        df_user = df_user[["user_id", "gender"]]

        df_movie = df_movie[
            [
                "movie_id",
                "genres",
                "popularity",
                "runtime",
                "vote_average",
                "vote_count",
            ]
        ]
        df = df_watch.merge(df_rating, how="left", on=["user_id", "movie_id"])
        df = df.merge(df_movie, how="inner", on=["movie_id"])
        df = df.merge(df_user, how="inner", on=["user_id"])

        # Extract genres
        df["genres"] = df["genres"].apply(lambda x: [ob["name"] for ob in x])

        # Extract watch time percentage
        df["clips"] = df["clips"].apply(lambda x: len(x))
        df["watch_percentage"] = df["clips"] / df["runtime"]

        # Add movie integer id
        movies = df["movie_id"].unique()
        convert = {movie_id: i for i, movie_id in enumerate(movies)}
        df["movie_id_int"] = df["movie_id"].apply(lambda x: convert[x])

        df = df.drop(["clips", "runtime", "_id_x", "_id_y", "timestamp"], axis=1)
        return df

    def clean_training_data(self, df):
        df["rate"] = df["rate"].fillna(0)
        print(f'Number of unique users {len(df["movie_id"].unique())}')
        print(f'Number of unique movies {len(df["user_id"].unique())}')
        return df

    def pickle_training_data(self, df, use_wandb=True):
        df_train, df_test = train_test_split(df, test_size=0.1, random_state=1)
        df_train, df_val = train_test_split(df, test_size=0.2, random_state=1)
        df_train.to_pickle(self.config["TrainData"]["train_df_pkl_path"])
        df_val.to_pickle(self.config["TrainData"]["val_df_pkl_path"])
        df_test.to_pickle(self.config["TrainData"]["test_df_pkl_path"])

        if use_wandb:
            run = wandb.init(
                project="movie-recs",
                entity="movie-recs-team3",
                job_type="data-preparation",
            )

            artifact = wandb.Artifact("data-df", type="data")
            artifact.add_file(self.config["TrainData"]["train_df_pkl_path"])
            artifact.add_file(self.config["TrainData"]["val_df_pkl_path"])
            artifact.add_file(self.config["TrainData"]["test_df_pkl_path"])
            run.log_artifact(artifact)
            run.finish()

    def unpickle_training_data(self, path):
        return pd.read_pickle(path)

    def run(self):
        df = self.build_training_df()
        df = self.clean_training_data(df)
        self.pickle_training_data(df)


if __name__ == "__main__":
    trainingData = TrainingDataPrep()
    df = trainingData.build_training_df()
    df = trainingData.clean_training_data(df)
