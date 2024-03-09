from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import current_user, jwt_required

from api.dao.movies import MovieDAO
from api.dao.ratings import RatingDAO

movie_routes = Blueprint("movies", __name__, url_prefix="/api/movies")

# For debugging flask stuff
from pprint import pprint, pformat
import sys
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity


@movie_routes.get('/')
@jwt_required(optional=True)
def get_movies():
    # print request details for debugging
    # current_app.logger.debug("get_movies")
    # current_app.logger.debug("Request Args %s", request.args)
    # current_app.logger.debug("Request Headers %s", request.headers)
    # current_app.logger.debug("JWT %s", get_jwt())
    # current_app.logger.debug("JWT identity %s", get_jwt_identity())
    # current_app.logger.debug("current user %s", current_user)

    # Extract pagination values from the request
    sort = request.args.get("sort", "title")
    order = request.args.get("order", "ASC")
    limit = request.args.get("limit", 6, type=int)
    skip = request.args.get("skip", 0, type=int)

    # Get User ID from JWT Auth
    user_id = current_user["sub"] if current_user != None else None

    # Create a new MovieDAO Instance
    dao = MovieDAO(current_app.driver)

    # Retrieve a paginated list of movies
    output = dao.all(sort, order, limit=limit, skip=skip, user_id=user_id)

    # Return as JSON
    return jsonify(output)


@movie_routes.get('/<movie_id>')
@jwt_required(optional=True)
def get_movie_details(movie_id):
    # Get User ID from JWT Auth
    user_id = current_user["sub"] if current_user != None else None

    # Create a new MovieDAO Instance
    dao = MovieDAO(current_app.driver)

    # Get the Movie
    movie = dao.find_by_id(movie_id, user_id)

    return jsonify(movie)


@movie_routes.get('/<movie_id>/ratings')
def get_movie_ratings(movie_id):
    # Extract pagination values from the request
    sort = request.args.get("sort", "timestamp")
    order = request.args.get("order", "ASC")
    limit = request.args.get("limit", 6, type=int)
    skip = request.args.get("skip", 0, type=int)

    # Create a new RatingDAO Instance
    dao = RatingDAO(current_app.driver)

    # Get ratings for the movie
    ratings = dao.for_movie(movie_id, sort, order, limit, skip)

    return jsonify(ratings)


@movie_routes.get('/<movie_id>/similar')
@jwt_required(optional=True)
def get_similar_movies(movie_id):
    # Get User ID from JWT Auth
    user_id = current_user["sub"] if current_user != None else None

    # Extract pagination values from the request
    limit = request.args.get("limit", 6, type=int)
    skip = request.args.get("skip", 0, type=int)

    # Create a new MovieDAO Instance
    dao = MovieDAO(current_app.driver)

    # Get Similar Movies
    output = dao.get_similar_movies(movie_id, limit, skip, user_id)

    return jsonify(output)

