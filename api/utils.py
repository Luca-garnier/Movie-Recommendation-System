import pickle
import json
import pathlib

MODEL_PATH = pathlib.Path(__file__).parent / "models" / "cf_model.pkl"
DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "train_data" / "train_df.pkl"

def load_pickle(path):
    with open(path, "rb") as file:
        return pickle.load(file)


def load_json(path):
    with open(path, "r+") as f:
        return json.load(f)


def get_movie_id(string_id):
    return int(string_id.split("+")[-1])


# FIXME: This column should be added when the dataframe is created and not here
def compute_ids_int(df):
    movies = df["movie_id"].unique()
    convert = {movie_id: i for i, movie_id in enumerate(movies)}
    df["movie_id_int"] = df["movie_id"].apply(lambda x: convert[x])
    return df


def verifyUserID(userId):
    # TODO: Ideally we would also like to cross-reference with the server to verify
    # if the userid belongs to a user. Circle CI cannot easily be set up with the
    # McGill VPN so for now this is not possible
    if not userId.isnumeric():
        return None
    return int(userId)