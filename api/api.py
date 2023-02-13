import os
import flask
from flask.helpers import make_response

import wandb

from api.utils import verifyUserID, load_pickle, MODEL_PATH, DATA_PATH
from api.services import SETTINGS, recommend_movie

from api.utils import verifyUserID, load_pickle
from api.services import recommend_movie
from prometheus_flask_exporter import PrometheusMetrics
import logging

recRoute = "/recommend/"
logRoute = "/log/"

# For load balanceing, one in every Nth user will recieve the new model.
everyNthUser = 3

flsk = flask.Flask(__name__)

metrics = PrometheusMetrics(flsk)

metrics.info("app_info", "App Info, this can be anything you want", version="1.0.0")

MODEL = None
DATA = None

RUN = None

LOG_TABLE = wandb.Table(
    columns=[
        "model_version",
        "data_version",
        "code_version",
        "userid",
        "recommended_movies",
    ],
)

MODEL = load_pickle(MODEL_PATH)
DATA = load_pickle(DATA_PATH)
logging.basicConfig(level=logging.INFO)
logging.info("Setting LOGLEVEL to INFO")


@flsk.route("/", methods=["GET"])
def test():
    return "Hello World!"


@flsk.route(recRoute + "<userid>", methods=["GET"])
def recommend(userid):
    global LOG_TABLE
    vUID = verifyUserID(userid)
    if vUID == None:
        return make_response("Invalid userid", 400)
    recommentations, logs = recommend_movie(vUID, MODEL, DATA, RUN)
    LOG_TABLE.add_data(*list(logs.values()))
    return recommentations

@flsk.route(logRoute, methods=["GET"])
def logWandB():
    global RUN
    RUN.log({"metadata": LOG_TABLE}, commit=True)
    return "Success"


def deployAPI(port):
    global SETTINGS
    global RUN
    global MODEL
    global DATA
    global LOG_TABLE

    if SETTINGS["wandb"]:
        # TODO: Remove API key from codebase. Bad practice.
        wandb.login(key="8000db4d0a17a105928eb36809982acbf89af37c")
        RUN = wandb.init(
            project="movie-recs",
            entity="movie-recs-team3",
            job_type="recommendation",
            config=SETTINGS,
        )
        with RUN:
            model_artifact = RUN.use_artifact("trained_model" + ":latest")
            model_dir = model_artifact.download()
            MODEL = load_pickle(os.path.join(model_dir, "cf_model.pkl"))
            print(
                f"Using model version {model_artifact.version}, commit {model_artifact.commit_hash}"
            )
            data_artifact = RUN.use_artifact("data-df" + ":latest")
            data_dir = data_artifact.download()
            DATA = load_pickle(os.path.join(data_dir, "train_df.pkl"))
            print(
                f"Using data version {data_artifact.version}, commit {data_artifact.commit_hash}"
            )
            SETTINGS.update(
                {
                    "model_version": model_artifact.version,
                    "data_version": data_artifact.version,
                    "code_version": SETTINGS["code_version"],
                }
            )
            flsk.run(host="0.0.0.0", port=port)
    else:
        flsk.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    deployAPI(5000)

