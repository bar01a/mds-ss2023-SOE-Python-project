import pandas as pd
import os
import pickle
import math


class Recommendation:
    def __init__(self, movieId, lift):
        self.movieId = movieId
        self.lift = lift

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.movieId == other.movieId and math.isclose(self.lift, other.lift)
        else:
            return False

    def __str__(self):
        return f'({self.movieId}, {self.lift})'


def create_user_ratings_dict_set(ratings, rating_mean_per_movie_dict, rating_mean_per_user_dict,
                                 load_if_available=True, save_on_creation=True, print_progress=True):
    save_file_path = "models/user_ratings_dict_set.pkl"
    if load_if_available and os.path.exists(save_file_path):
        with (open(save_file_path, "rb")) as openfile:
            return pickle.load(openfile)

    user_ratings_dict_set = {}

    # iterate through all ratings and group users in dictionary
    for index, rating_info in enumerate(ratings.values):
        userId = int(rating_info[0])
        movieId = int(rating_info[1])
        rating = rating_info[2]
        average_movie_rating = rating_mean_per_movie_dict[movieId]["rating"]
        average_user_rating = rating_mean_per_user_dict[userId]
        if rating >= average_user_rating and rating >= average_movie_rating:
            if userId in user_ratings_dict_set:
                user_ratings_dict_set[userId].add(movieId)
            else:
                user_ratings_dict_set[userId] = {movieId}
        if index % 1000000 == 0 and index > 0 and print_progress:
            print('{:,}'.format(index).replace(',', '.'))

    if save_on_creation:
        with open(save_file_path, 'wb') as file:
            pickle.dump(user_ratings_dict_set, file)

    # remove users with only one rating
    return {key: value for key, value in user_ratings_dict_set.items() if len(value) > 1}


def contains_movie_title(list_with_strings: [str], str_text: str):
    result = []
    # replace multiple whitespaces with single space and split words
    split_search = ' '.join(str_text.split()).lower().split(' ')

    for string_in_list in list_with_strings:
        string_in_list = string_in_list.lower()
        has_all_search_parts = True
        for search_part in split_search:
            if search_part not in string_in_list:
                has_all_search_parts = False
                break
        result.append(has_all_search_parts)

    return result


def get_movie(movies_df, str_text: str, print_result=True):
    matches = movies_df[contains_movie_title(movies_df.title, str_text)]
    if len(matches) == 0:
        if print_result:
            print("no matches for", str_text)
        return None
    if len(matches) > 1 and print_result:
        print("more than 1 match -> taking first movie", matches.iloc[0].title)
    elif print_result:
        print("found title:", matches.iloc[0].title)
    return matches.iloc[0]


def get_movies(movies_df, str_texts: str) -> [pd.Series]:
    movies = [get_movie(movies_df, text) for text in str_texts.split(";")]
    return [movie for movie in movies if movie is not None]


def create_movies_recommendation_dict(association_results, load_if_available=True, save_on_creation=True):
    save_file_path = "models/recommendationDict.pkl"
    if load_if_available and os.path.exists(save_file_path):
        with (open(save_file_path, "rb")) as openfile:
            return pickle.load(openfile)

    result = {}
    shallow_copy = list(association_results)

    while len(shallow_copy) > 0:
        current_item_add = shallow_copy[0].ordered_statistics[0].items_add
        current_movie_id = next(iter(current_item_add))
        result[current_movie_id] = []
        to_remove = []
        for index, association_result in enumerate(shallow_copy):

            item_add = association_result.ordered_statistics[0].items_add
            movieId = next(iter(item_add))
            if movieId == current_movie_id:
                to_remove.append(index)
                item_base = association_result.ordered_statistics[0].items_base
                recommended_movieId = next(iter(item_base))
                result[current_movie_id].append(Recommendation(recommended_movieId,
                                                               association_result.ordered_statistics[0].lift))
        result[current_movie_id].sort(key=lambda recommendation: recommendation.lift, reverse=True)
        for index in sorted(to_remove, reverse=True):
            del shallow_copy[index]

    if save_on_creation:
        with open(save_file_path, 'wb') as file:
            pickle.dump(result, file)

    return result


def print_possible_matches(movies_df: pd.DataFrame, movies_string: str, recommendation_dict, n=5):
    movies_list = get_movies(movies_df, movies_string)
    print()
    for movie in movies_list:
        recommendations = recommendation_dict[movie.movieId] if movie.movieId in recommendation_dict else []
        print("Recommendations for %s: %d recommendations found" % (movie.title, len(recommendations)))
        for recommendation in recommendations[:n]:
            print("Lift: %.2f | Movie: %s" % (recommendation.lift,
                                              ";".join(movies_df[
                                                           movies_df.movieId == recommendation.movieId].title.to_list())))
        print("--------")


def calculate_prediction_error(requested_movie_id, user_ratings, recommendation_dict,
                               max_recommendations=5, forgiving_error=True):
    if requested_movie_id not in recommendation_dict:
        return None

    user_enjoyed_movie_ids = user_ratings[user_ratings["movieId"] != requested_movie_id]["movieId"].to_list()
    recommendations_movie_ids = [recommendation.movieId for recommendation in
                                 recommendation_dict[requested_movie_id][0:max_recommendations]]

    relevant_recommendations = 0

    for index, recommendation_movie_id in enumerate(recommendations_movie_ids):
        # maximum number of recommendations = number of movies that the user enjoyed watching
        if index > len(user_enjoyed_movie_ids):
            break
        if recommendation_movie_id in user_enjoyed_movie_ids:
            relevant_recommendations += 1

    # maximum error 1 if no recommendations match
    # minimum error 0 if all recommendations match
    # everything in-between is calculated proportional to the number of checked recommendations
    error = 1 - relevant_recommendations / min(len(user_enjoyed_movie_ids), len(recommendations_movie_ids))

    if forgiving_error:
        # more forgiving -> if at least 1 recommendation is inside the user's favourite list: Error = 0
        #                -> otherwise: Error = 1
        return 0 if error < 1.0 else 1

    return error


def extend_recommendation_dict_both_ways(recommendation_dict, n=5, max_lift_relative_distance=0.05):
    from statistics import mean

    new_recommendations = {}
    recommendation_dict_copy = recommendation_dict.copy()

    for key, value_list in recommendation_dict_copy.items():
        top_recommendations = value_list[:n]

        for index, value in enumerate(top_recommendations):
            recommendations_except_this = list(top_recommendations[:index] + top_recommendations[index + 1:])

            if value.movieId in new_recommendations:
                for other_recommendation in recommendations_except_this:
                    if other_recommendation not in new_recommendations[value.movieId] and \
                            abs((other_recommendation.lift / value.lift) - 1) <= max_lift_relative_distance:
                        # this might add several identical movies with different lifts
                        new_recommendations[value.movieId].append(
                            Recommendation(other_recommendation.movieId, other_recommendation.lift))
            else:
                new_recommendations[value.movieId] = [
                    Recommendation(other_recommendation.movieId, other_recommendation.lift)
                    for other_recommendation in recommendations_except_this
                    if abs((other_recommendation.lift / value.lift) - 1) <= max_lift_relative_distance]

            new_recommendations[value.movieId].append(Recommendation(key, value.lift))

    # remove duplicate recommendations
    for key, value in new_recommendations.items():
        movie_ids_group = {}
        for recommendation in value:
            if recommendation.movieId not in movie_ids_group:
                movie_ids_group[recommendation.movieId] = []

            movie_ids_group[recommendation.movieId].append(recommendation.lift)

        unique_recommendations = [Recommendation(movie_id, mean(movie_ids_group[movie_id])) for movie_id in
                                  movie_ids_group.keys()]
        unique_recommendations.sort(key=lambda rec: rec.lift, reverse=True)

        new_recommendations[key] = unique_recommendations

    new_recommendations.update(recommendation_dict)
    return new_recommendations


def get_movie_titles(movies_df, movie_ids):
    if type(movie_ids) is list:
        return [movies_df[movies_df["movieId"] == movie_id]["title"].iloc[0] for movie_id in movie_ids]
    return movies_df[movies_df["movieId"] == movie_ids]["title"].iloc[0]


class Movie:
    def __init__(self, movieId, title, genres, like, image):
        self.movieId = movieId
        self.title = title
        self.genres = genres
        self.like = like
        self.image = image


class RecommendationGroup:
    def __init__(self, for_movie: Movie, movies: [Movie]):
        self.for_movie = for_movie
        self.movies = movies


def get_recommendations(rated_movies, movies_df: pd.DataFrame,
                        recommendation_dict, recommendation_per_liked_movie=5,
                        extend_disliked_list_by=5):
    result = []
    disliked_movies_ids = []

    for rated_movie in rated_movies:
        # only take disliked movies
        if rated_movie["like"] is not False:
            continue
        if rated_movie["movieId"] in recommendation_dict:
            connected_disliked_movies: [Recommendation] = recommendation_dict[rated_movie["movieId"]][:extend_disliked_list_by]
            print(rated_movie["movieId"])
            # add similar movies that were disliked to "disliked list"
            disliked_movies_ids.extend([disliked_movie.movieId for disliked_movie in connected_disliked_movies])
        disliked_movies_ids.append(rated_movie["movieId"])

    for rated_movie in rated_movies:
        # only take liked movies into account and those which have recommendations
        if rated_movie["like"] is not True or rated_movie["movieId"] not in recommendation_dict:
            continue

        recommendations = []

        for recommendation in recommendation_dict[rated_movie["movieId"]]:
            if len(recommendations) >= recommendation_per_liked_movie:
                break
            if recommendation.movieId not in disliked_movies_ids:
                movie = movies_df[movies_df["movieId"] == recommendation.movieId].iloc[0]
                # movie.movieId is numpyType? Cannot be serialized with json.dumps
                recommendations.append(Movie(int(movie.movieId), movie.title, movie.genres, True, "").__dict__)

        result.append({"movie": rated_movie, "recommendations": recommendations})

    return result
