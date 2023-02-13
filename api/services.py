from api.utils import compute_ids_int

import logging
import numpy as np
import wandb
import git

logging.basicConfig(level=logging.DEBUG)

SETTINGS = {
    "wandb": True,
    "number_recommendation": 10,
    "min_candidates": 40,
    "num_genres": 5,
    "average_user": 1,
    "code_version": git.Repo(search_parent_directories=True).head.object.hexsha,
}


def recommend_movie(userid, model, data, run=None):
    recommend_movies = get_recommendations(model, data, userid)
    if SETTINGS["wandb"]:
        logs = {
            "model_version": SETTINGS["model_version"],
            "data_version": SETTINGS["data_version"],
            "code_version": SETTINGS["code_version"],
            "userid": userid,
            "recommended_movies": recommend_movies,
        }
    return f"userid:{userid}, movies:{recommend_movies}", logs


def get_recommendations(model, data, userid):
    data = compute_ids_int(data)
    watched_movies = get_watched_movies(data, userid)
    candidates = generate_candidates(model, data, userid, watched_movies)
    recommend_movies = scoring(candidates, data)
    return (",".join( repr(e) for e in recommend_movies )).replace("'", "")


def generate_candidates(model, data, userid, watched_movies):
    userid = int(userid)
    number_candidates = len(watched_movies) + SETTINGS["min_candidates"]
    try:
        candidates = model.recommend(
            userid, data, N=number_candidates, filter_already_liked_items=False
        )
    except IndexError:
        candidates = model.recommend(
            SETTINGS["average_user"],
            data,
            N=number_candidates,
            filter_already_liked_items=False,
        )
    candidates = filter_candidates(candidates, watched_movies)
    return candidates


def get_watched_movies(data, userid):
    watched_movies = data.loc[data["user_id"].astype(int) == userid]
    return np.array(watched_movies["movie_id_int"])


def filter_candidates(candidates, watched_movies):
    candidates = [
        (candidate_id, score)
        for candidate_id, score in candidates
        if candidate_id not in watched_movies
    ]
    return candidates


def scoring(candidates, data):
    movies_genres = get_movies_genres(candidates, data)
    movies_by_genre = {}
    for i, candidate in enumerate(candidates):
        candidate_id, _ = candidate
        movie_genres = movies_genres[i]
        for genre in movie_genres:
            if genre in movies_by_genre:
                movies_by_genre[genre].append(candidate_id)
            else:
                movies_by_genre[genre] = [candidate_id]

    recommended_movies = []
    movies_per_genre = int(SETTINGS["number_recommendation"] / SETTINGS["num_genres"])
    for genre in movies_by_genre.keys():
        movies = movies_by_genre[genre]
        movies = [movie for movie in movies if (movie not in recommended_movies)]
        recommended_movies += movies[:movies_per_genre]
        if len(recommended_movies) > SETTINGS["number_recommendation"]:
            break

    recommended_movies = get_full_ids(
        recommended_movies[: SETTINGS["number_recommendation"]], data
    )
    return recommended_movies


def get_movies_genres(candidates, data):
    movies_genres = []
    for candidate_id, _ in candidates:
        genres = data.loc[data["movie_id_int"] == candidate_id]["genres"].values[0]
        movies_genres.append(genres)

    return movies_genres


def get_full_ids(recommended_movies, data):
    full_ids = []
    for recommended_movie in recommended_movies:
        full_id = data.loc[data["movie_id_int"] == recommended_movie][
            "movie_id"
        ].values[0]
        full_ids.append(full_id)

    return full_ids

