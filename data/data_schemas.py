from mongoengine import *


class User(Document):
    meta = {'db_alias': 'bd'}
    user_id = IntField(required=True)
    age = IntField(min_value=0, max_value=99)
    occupation = StringField(max_length=200)
    gender = StringField(max_length=50, choices=["M", "F"])


class Rating(Document):
    meta = {'db_alias': 'bd'}
    user_id = IntField(required=True)
    movie_id = StringField(required=True)
    timestamp = DateTimeField()
    rate = IntField(min_value=0, max_value=5)


class Clip(EmbeddedDocument):
    meta = {'db_alias': 'bd'}
    timestamp = DateTimeField()
    clip = StringField(required=True, max_length=200)


class WatchHistory(Document):
    meta = {'db_alias': 'bd'}
    user_id = IntField(required=True)
    movie_id = StringField(required=True)
    clips = ListField(EmbeddedDocumentField(Clip))


class MovieCollection(EmbeddedDocument):
    meta = {'db_alias': 'bd'}
    id = IntField(max_length=200)
    name = StringField(max_length=200)
    poster_path = StringField(max_length=200)
    backdrop_path = StringField(max_length=200)


class Genre(EmbeddedDocument):
    meta = {'db_alias': 'bd'}
    id = IntField(max_length=200)
    name = StringField(max_length=200)


class ProdCompany(EmbeddedDocument):
    meta = {'db_alias': 'bd'}
    id = IntField(max_length=200)
    name = StringField(max_length=200)


class ProdCountry(EmbeddedDocument):
    meta = {'db_alias': 'bd'}
    iso_3166_1 = StringField(max_length=200)
    name = StringField(max_length=200)


class SpokenLang(EmbeddedDocument):
    meta = {'db_alias': 'bd'}
    iso_639_1 = StringField(max_length=200)
    name = StringField(max_length=200)


class Movie(Document):
    meta = {'db_alias': 'bd'}
    movie_id = StringField(db_field='movie_id', required=True)
    tmdb_id = IntField(max_length=200)
    imdb_id = StringField(max_length=200)
    title = StringField(max_length=200)
    original_title = StringField(max_length=200)
    adult = BooleanField()
    belongs_to_collection = EmbeddedDocumentField(MovieCollection)
    budget = IntField(max_length=200, default=None)
    genres = ListField(EmbeddedDocumentField(Genre))
    homepage = StringField(max_length=200)
    original_language = StringField(max_length=200)
    overview = StringField(max_length=1000)
    popularity = FloatField(min_value=0)
    poster_path = StringField(max_length=200)
    production_companies = ListField(EmbeddedDocumentField(ProdCompany))
    production_countries = ListField(EmbeddedDocumentField(ProdCountry))
    release_date = DateTimeField()
    revenue = IntField(max_length=200, default=None)
    # how many clips
    runtime = IntField(max_length=200)
    spoken_languages = ListField(EmbeddedDocumentField(SpokenLang))
    status = StringField(max_length=200)
    vote_average = FloatField(min_value=0, max_value=10)
    vote_count = IntField(min_value=0)

class RecMovie(EmbeddedDocument):
    meta = {'db_alias': 'bd'}
    movie_id = StringField(max_length=200)
    watched = BooleanField(default=False)
    rated = IntField(default=0)


class Recommendation(Document):
    meta = {'db_alias': 'bd'}
    user_id = IntField(required=True)
    movies = ListField(EmbeddedDocumentField(RecMovie))