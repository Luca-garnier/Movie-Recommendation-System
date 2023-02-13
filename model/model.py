import datetime
import sys
import time

import pathlib
import pickle
import wandb

import numpy as np
from scipy.sparse import csr_matrix
from implicit.als import AlternatingLeastSquares

from api.utils import load_pickle, compute_ids_int

HYPERPARAMS = {
    "wandb": True,
    "seed": 0,
    "embedding_size": 20,
    "show_loss": False,
    "validation_recommendations": 100,
    "validation_k_intervals": 10,
    "regularization": 1,
}

TRAIN_DATA_PATH = (
    pathlib.Path(__file__).parent.parent / "data" / "train_data" / "train_df.pkl"
)
VALID_DATA_PATH = (
    pathlib.Path(__file__).parent.parent / "data" / "train_data" / "val_df.pkl"
)
TEST_DATA_PATH = (
    pathlib.Path(__file__).parent.parent / "data" / "train_data" / "test_df.pkl"
)
MODEL_PATH = pathlib.Path(__file__).parent.parent / "api" / "models" / "cf_model.pkl"


def load_data(data_path):
    data = load_pickle(data_path)
    data = compute_ids_int(data)
    data["confidence"] = data.apply(compute_confidence, axis=1)
    feature_matrix = csr_matrix(
        (data["confidence"], (data["movie_id_int"], data["user_id"].astype(int)),)
    )
    return feature_matrix


def compute_confidence(row):
    if not row["rate"]:
        return row["watch_percentage"]
    else:
        if row["rate"] < 3:
            return (3 - row["rate"]) / 2
        else:
            return (row["rate"] - 2) / 3


def collaborative_filtering(feature_matrix):
    model = AlternatingLeastSquares(
        factors=HYPERPARAMS["embedding_size"],
        random_state=HYPERPARAMS["seed"],
        calculate_training_loss=HYPERPARAMS["show_loss"],
        regularization=HYPERPARAMS["regularization"],
    )
    model.fit(feature_matrix)

    return model


def train_model():
    feature_matrix = load_data(TRAIN_DATA_PATH)
    model = collaborative_filtering(feature_matrix)

    with open(MODEL_PATH, "wb") as file:
        pickle.dump(
            model, file,
        )


def evaluate_model():
    print("======== Evaluating model =========")
    print("------- Computing at k recall --------")
    model = load_pickle(MODEL_PATH)
    valid_data_df = load_pickle(VALID_DATA_PATH)
    valid_data_df = compute_ids_int(valid_data_df)
    valid_users = valid_data_df["user_id"].unique()
    data_male = valid_data_df.loc[valid_data_df["gender"] == "M"]
    data_female = valid_data_df.loc[valid_data_df["gender"] == "F"]

    male_users = data_male["user_id"].unique()
    female_users = data_female["user_id"].unique()
    start = time.time()
    at_k_recalls = compute_at_k_recalls(valid_data_df, valid_users, model)
    end = time.time()
    avgEvalTime = ((end - start) / len(valid_users)) * 1000
    at_k_recalls_male = compute_at_k_recalls(data_male, male_users, model)
    at_k_recalls_female = compute_at_k_recalls(data_female, female_users, model)
    original_stdout = sys.stdout  # Save a reference to the original standard output
    with open("offline_evaluation.txt", "w") as f:
        sys.stdout = f  # Change the standard output to the file we created.
        print("--------------------------------------------------------------------")
        print(datetime.datetime.utcnow())
        print("--------------------------------------------------------------------")
        for i, at_k_recall in enumerate(at_k_recalls):
            k = (i + 1) * HYPERPARAMS["validation_k_intervals"]
            print(
                f"At {k}-recall is {at_k_recall}, Average evaluation time is {round(avgEvalTime,4)}ms"
            )
        for i, at_k_recall in enumerate(at_k_recalls_male):
            k = (i + 1) * HYPERPARAMS["validation_k_intervals"]
            print(f"At {k}-recall for the male population is {at_k_recall}")
        for i, at_k_recall in enumerate(at_k_recalls_female):
            k = (i + 1) * HYPERPARAMS["validation_k_intervals"]
            print(f"At {k}-recall for the female population is {at_k_recall}")
        sys.stdout = original_stdout  # Reset the standard output to its original value


def compute_at_k_recalls(valid_data_df, valid_users, model):
    num_k = int(
        HYPERPARAMS["validation_recommendations"]
        / HYPERPARAMS["validation_k_intervals"]
    )
    at_k_recalls = [[] for k in range(num_k)]
    for user in valid_users:
        user_df = valid_data_df.loc[valid_data_df["user_id"] == user]
        user_movies = set(user_df["movie_id_int"].unique())

        recommendations = model.recommend(
            user,
            None,
            N=HYPERPARAMS["validation_recommendations"],
            filter_already_liked_items=False,
        )
        recommendations = [movie_id for movie_id, _ in recommendations]

        for i in range(1, num_k + 1):
            recommendations_subset = set(
                recommendations[: i * HYPERPARAMS["validation_k_intervals"]]
            )
            recall = len(recommendations_subset.intersection(user_movies)) / len(
                user_movies
            )
            at_k_recalls[i - 1].append(recall)

    at_k_recalls = [np.mean(np.array(at_k_recall)) for at_k_recall in at_k_recalls]
    return at_k_recalls


class Model:
    def run(self):
        if not HYPERPARAMS["wandb"]:
            train_model()
            evaluate_model()
        else:
            train_run = wandb.init(
                project="movie-recs",
                entity="movie-recs-team3",
                job_type="training",
                config=HYPERPARAMS,
            )
            train_model()
            artifact = wandb.Artifact(
                "trained_model", type="model", metadata=HYPERPARAMS
            )
            artifact.add_file(MODEL_PATH)
            train_run.log_artifact(artifact)

            evaluate_model()
            artifact = wandb.Artifact(
                "at-k-recalls", type="evaluation", metadata=HYPERPARAMS
            )
            artifact.add_file(MODEL_PATH)
            train_run.log_artifact(artifact)
            train_run.finish()


if __name__ == "__main__":
    # train_model()
    evaluate_model()
