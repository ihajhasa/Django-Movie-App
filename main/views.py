from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from main.models import Movie, UserRating, MovieParty
from django.contrib.auth.models import User

import functools, operator

'''
Explanation to certain coding practices:

two sorts called in a row:
    sorted() is a stable sorting function -> order is maintained across elements with equal value to sorting key
    so I would sort alphabetically before sorting by score to make sure equal scores are sorted alphabetically
    
initial condition check (if not request.user.is_authenticated)
    the pages can only be visited by a logged in user. If user is not authenticated (i.e. logged in)
    then redirect them to the login page
'''

'''
    Helper Classes for HTML
        certain groupings of data to easily reference in HTML files
        none of the objects are new, they reference objects from the database and are not modified in any way
'''

'''
    RatedMovie:
        movie: Moviee object
        userscore: used as a single user's score to know the user's rating for a movie
                   OR used to calculate clan rating
'''
class RatedMovie:
    def __init__(self, movie, userscore):
        self.movie = movie
        self.userscore = userscore

'''
    MovieParty_Stats:
        movieparty: MovieParty object
        nummembers: The number of members in the movieparty
        founder: Reference to User ( = movieparty.createdby)
'''
class MovieParty_Stats:
    def __init__(self, movieparty):
        self.movieparty=movieparty
        self.nummembers = movieparty.members.count
        self.founder = movieparty.createdby

'''
    MovieParty_Profile:
        movieparty: MovieParty object
        stats: MovieParty_Stats Object
'''
class MovieParty_Profile:
    def __init__(self, movieparty, user):
        self.movieparty = movieparty
        self.stats = MovieParty_Stats(movieparty=movieparty)

        if(user in movieparty.members.all()):
            self.showjoin = False
            self.showleave = True
        else:
            if (len(movieparty.members.all()) < 10):
                self.showjoin = True
            else:
                self.showjoin = False
            self.showleave = False


        if(user == movieparty.createdby):
            self.showdelete = True
            self.showleave = False
        else:
            self.showdelete = False
'''
    Report:
        num_movies: Number of Movies
        num_users: Number of Users
        rflix_num_ratings: Number of User Ratings made through the system 
        total_num_ratings: Number of Ratings (imported + UserRatings)
        rflix_avg_num_ratings_per_movie: Average number of ratings per movie (UserRating) (Across all movies)
        total_avg_num_ratings_per_movie: Average number of ratings per movie (imported + UserRating)
        avg_num_ratings_per_user: Average number of ratings per User
        top_10_users_ratings_number: Top 10 Users with highest number of ratings
        num_movieparties: Number of MovieParties
        avg_num_users_per_party: Avg Number of Members in MovieParties
        top_10_users_movieparty_membership: Top 10 Users with highest MovieParties memberships
'''
class Report:
    def __init__(self, num_movies, num_users, rflix_num_ratings, total_num_ratings,
                 rflix_avg_num_ratings_per_movie, total_avg_num_ratings_per_movie,
                 avg_num_ratings_per_user, top_10_users_ratings_number, num_movieparties,
                 avg_num_users_per_party, top_10_users_movieparty_membership):
        self.num_movies = num_movies
        self.num_users = num_users
        self.rflix_num_ratings = rflix_num_ratings
        self.total_num_ratings = total_num_ratings
        self.rflix_avg_num_ratings_per_movie = rflix_avg_num_ratings_per_movie
        self.total_avg_num_ratings_per_movie = total_avg_num_ratings_per_movie
        self.avg_num_ratings_per_user = avg_num_ratings_per_user
        self.top_10_users_ratings_number = top_10_users_ratings_number
        self.num_movieparties = num_movieparties
        self.avg_num_users_per_party = avg_num_users_per_party
        self.top_10_users_movieparty_membership = top_10_users_movieparty_membership

# Helper functions
# https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
# to flatten a list
def functools_reduce_iconcat(a):
    return functools.reduce(operator.iconcat, a, [])

#   Return the top X movies with the highest ratings
def get_top_x_alltime(x):
    movies = sorted(Movie.objects.all(), key=lambda movie: movie.rating, reverse=True)[:x]
    return movies

# views functions


def movies(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    # User must be logged in to view page

    # list of movies that the user rated
    rated_movies = []
    # a dictionary: (KEY: movie) (VALUE: the user's rating of the movie)
    movies_rating = {}

    # For all the ratings by the user
    for rating in request.user.userrating_user.all():
        # add movie rated by the user
        rated_movies += [rating.ratedfor]
        # store the user's rating of said movie
        movies_rating[rating.ratedfor] = rating.rating

    # sort list of movies alphabetically
    rated_movies = sorted(rated_movies, key=lambda movie: movie.title)

    # unrated movies are the list of all the movies - the movies the user rated
    # then sort alphabetically
    unrated_movies = sorted(list(set(Movie.objects.all()) - set(rated_movies)), key=lambda movie: movie.title)

    # make list of rated movies as RatedMovies object to store the movie and user's score for HTML page
    rated_movies = map(lambda movie: RatedMovie(movie, movies_rating[movie]), rated_movies)

    context = {'rated_movies': rated_movies,
               'unrated_movies': unrated_movies}
    return render(request, 'movies.html', context)


def delete_rating(request, movie_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    # try to retrieve the UserRating by the user for the Movie with id=movie_id
    try:
        movie = Movie.objects.get(pk=movie_id)
        userrating = UserRating.objects.get(ratedby=request.user, ratedfor=movie)
    except:
        # if Movie not found -> the movie doesn't exist
        # if UserRating not found -> the user didn't rate this movie
        return HttpResponseRedirect(reverse('movies'))

    # modify movie stats
    if ((movie.nratings - 1) == 0):
        movie.rating = 0
        movie.nratings = 0
    else:
        new_global_score = ((movie.rating * movie.nratings) - userrating.rating) / (movie.nratings - 1)
        movie.rating = new_global_score
        movie.nratings -= 1

    # delete userrating and save changes
    movie.save()
    userrating.delete()

    return HttpResponseRedirect(reverse('movies'))

def rate_movie(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if(request.method == 'POST'):
        movie_id = request.POST['id']
        score = int(request.POST['rating'])

        if(movie_id == ''):
            return HttpResponseRedirect(reverse('movies'))

        if(score < 0 or 5 < score):
            # score out of bounds and so form is invalidated
            return HttpResponseRedirect(reverse('movies'))

        try:
            movie = Movie.objects.get(pk=movie_id)
        except  Movie.DoesNotExist:
            # user cannot rate a movie that doesn't exist
            return HttpResponseRedirect(reverse('movies'))

        try:
            userrating = UserRating.objects.get(ratedby=request.user, ratedfor=movie)
        except UserRating.DoesNotExist:
            # user rating the movie for the first time
            # create new rating and updated movie numbers
            if(score == 0):
                #user cannot rate movie 0
                return HttpResponseRedirect(reverse('movies'))

            # create new rating
            userrating = UserRating(rating=score, ratedby=request.user, ratedfor=movie)
            
            # update movie stats
            new_global_score = ((movie.rating*movie.nratings) + score)/(movie.nratings + 1)
            movie.rating = new_global_score
            movie.nratings += 1
            
            # save changes
            movie.save()
            userrating.save()

            # return to movie pages
            return HttpResponseRedirect(reverse('movies'))

        # rating already exists and needs to be either modified or deleted

        if (score == 0):
            # user wants to delete rating

            # modify movie stats
            if((movie.nratings - 1) == 0):
                movie.rating = 0
                movie.nratings = 0
            else:
                new_global_score = ((movie.rating * movie.nratings) - userrating.rating)/(movie.nratings-1)
                movie.rating = new_global_score
                movie.nratings -= 1

            # delete userrating and save changes
            movie.save()
            userrating.delete()
            
            return HttpResponseRedirect(reverse('movies'))

        # user wants to modify rating

        # modify movie stats
        new_global_score = ((movie.rating * movie.nratings) + (score - userrating.rating))/movie.nratings
        movie.rating = new_global_score

        #modify user rating
        userrating.rating = score
        
        # save changes
        userrating.save()
        movie.save()

        return HttpResponseRedirect(reverse('movies'))

    else:
        # non-POST request, just return to movies pages
        return HttpResponseRedirect(reverse('movies'))


def personalized_movie_recommendation(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    # list of tuple (User Rating, Movie) where
    #   each UserRating made by the user has an entry
    #   each UserRating is paired with the movie the rating is about
    userratings_movie_pair = list(map(lambda rating: (rating, rating.ratedfor),UserRating.objects.filter(ratedby=request.user)))

    # list of movies s.t. movies are rated by the user with a rating >= 3
    liked_movies = list(filter(lambda userrating_movie: userrating_movie[0].rating >= 3, userratings_movie_pair))
    liked_movies = list(map(lambda userrating_movie: userrating_movie[1], liked_movies))

    # given a movie return a list of users who rated the movie
    def get_users_who_liked_movie(movie):
        # get all the ratings about the movie
        userratings_for_movie = UserRating.objects.filter(ratedfor=movie)
        # keep the userratings with a rating at least 3
        userratings_for_movie = list(filter(lambda userrating: userrating.rating >= 3, userratings_for_movie))
        return list(map(lambda rating: rating.ratedby, userratings_for_movie))

    # for every liked movie by the user, get the list of users by the movie -> list of list of users
    # flatten the list and remove duplicates by converting it to a set then back to a list (then remove the user)
    # RESULTANT: other users who liked the same movies as user (get rid of duplicates and user)
    clan = list(set(functools_reduce_iconcat(list(map(get_users_who_liked_movie, liked_movies)))) - set([request.user]))

    movies_liked_by_other_users = set([])

    # for each user (that liked a movie liked by the user making the request) (i.e. otheruser)
    for otheruser in clan:
        # list of (ratings, movie rating is about)
        ou_userratings_movie_pair = list(map(lambda rating: (rating, rating.ratedfor), UserRating.objects.filter(ratedby=otheruser)))
        # keep liked movies
        ou_liked_movies = list(filter(lambda userrating_movie: userrating_movie[0].rating >= 3, ou_userratings_movie_pair))
        # change list to list of movies
        ou_liked_movies = set(map(lambda userrating_movie: userrating_movie[1], ou_liked_movies))
        # add elements to the aggregate list
        movies_liked_by_other_users = movies_liked_by_other_users.union(ou_liked_movies)
        
    # now we have a set of all the movies liked by the other users excluding the movies liked by the user
    recommendation_movies = list(map(lambda movie: RatedMovie(movie=movie, userscore=0.00),list(movies_liked_by_other_users - set(liked_movies))))

    # generate clan score for a given movie
    def generate_clan_score(ratedmovie):
        # number of clan members that rated the movie
        num_ratings = 0
        for clanmember in clan:
            try:
                userrating = (UserRating.objects.get(ratedby=clanmember, ratedfor=ratedmovie.movie)).rating
                num_ratings += 1
            except:
                userrating = 0
            ratedmovie.userscore += userrating
        ratedmovie.userscore = (ratedmovie.userscore * 1.0)/num_ratings
        ratedmovie.userscore = float("{:.2f}".format(ratedmovie.userscore)) #round to 2 decimal places
        return ratedmovie

    # for each potential recommended movie calculate the clan score
    recommendation_movies = list(map(generate_clan_score, recommendation_movies))

    # two cases:
    #   1. no other user liked a movie liked by the requesting user
    #   2. atleast one other user liked a movie liked by the requesting user BUT
    #      he hasn't liked another movie not liked by the requesting user
    if(len(recommendation_movies) == 0):
        # user could've liked all the top movies and so shouldn't recommend them to him
        recommendation_movies = get_top_x_alltime(len(liked_movies) + 5)
        recommendation_movies = sorted(list(set(recommendation_movies) - set(liked_movies)), key=lambda movie: movie.title)
        recommendation_movies = sorted(list(map(lambda movie: RatedMovie(movie=movie, userscore=0.00), recommendation_movies)), key=lambda ratedmovie: ratedmovie.movie.rating, reverse=True)
    else:
        # sort alphabetically then by clan score
        recommendation_movies = sorted(recommendation_movies, key=lambda ratedmovie: ratedmovie.movie.title)
        # sorted is stable so ties are broken by alphabetical order since list is already alphabetically sorted
        recommendation_movies = sorted(recommendation_movies, key=lambda ratedmovie: (ratedmovie.userscore, ratedmovie.movie.title), reverse=True)

    context = {'recommendations': recommendation_movies[:5]}
    return render(request, 'main/personalized-recommendation.html', context)


def movie_parties(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    # sort movie parties by their party number
    movieparties = MovieParty.objects.all()
    movieparties = sorted(list(map(lambda mp: MovieParty_Profile(movieparty=mp, user=request.user), movieparties)),
                          key=lambda mps: mps.movieparty.id)
    # keep MovieParties that the user is a member in
    joined_movie_parties = list(filter(lambda mp: request.user in mp.movieparty.members.all(), movieparties))
    # keep MovieParties that the user is NOT a member in
    unjoined_movie_parties = list(filter(lambda mp: request.user not in mp.movieparty.members.all(), movieparties))
    
    context = {'joined_movie_parties': joined_movie_parties,
               'unjoined_movie_parties': unjoined_movie_parties}
    return render(request, 'main/movie-parties.html', context=context)


def movie_party_profile(request, movieparty_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    try:
        mp = MovieParty.objects.get(id=movieparty_id)
    except:
        # MovieParty does not exist (or other errors)
        HttpResponseRedirect(reverse('movieparties'))

    mp = MovieParty_Profile(mp, request.user)

    # generate recommendations
    # dictionary of movie with (total cumulative score, num clan members who rated)
    movie_clanscore = {}

    # for each member
    for member in mp.movieparty.members.all():
        member_ratings = UserRating.objects.filter(ratedby=member)
        for rating in member_ratings:
            if rating.ratedfor in movie_clanscore:
                # a previous member rated this movie
                stats = movie_clanscore[rating.ratedfor]
                movie_clanscore[rating.ratedfor] = (stats[0] + rating.rating, stats[1] + 1)
            else:
                # member is the first one in the clan to rate it
                # add movie with base
                movie_clanscore[rating.ratedfor] = (rating.rating, 1)

    # list of RatedMovie -> movie and it's clan rating
    recommendations = []

    for key, value in movie_clanscore.items():
        recommendations += [RatedMovie(movie=key, userscore=((value[0]*1.0)/value[1]))]

    # sory by title then by clan score
    recommendations = sorted(recommendations, key=lambda ratedmovie: ratedmovie.movie.title)
    recommendations = sorted(recommendations, key=lambda ratedmovie: ratedmovie.userscore, reverse=True)

    context = {'movieparty_profile': mp,
               'memberlist': sorted(mp.movieparty.members.all(), key=lambda member: member.username),
               'recommendations': recommendations[:5]}
    return render(request, 'main/movieparty-profile.html', context)


def movie_party_join(request, movieparty_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    try:
        mp = MovieParty.objects.get(id=movieparty_id)
    except:
        # movie doesn't exist (or other errors)
        return HttpResponseRedirect(reverse('movieparties'))

    members = mp.members.all()

    if len(members) >= 10:
        # party is full
        return HttpResponseRedirect(reverse('moviepartyprofile', kwargs={'movieparty_id': movieparty_id}))

    if request.user not in members:
        # user cannot join party he is already a member in
        mp.members.add(request.user)
        mp.save()

    return HttpResponseRedirect(reverse('moviepartyprofile', kwargs={'movieparty_id': movieparty_id}))

def movie_party_leave(request, movieparty_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    try:
        mp = MovieParty.objects.get(id=movieparty_id)
    except:
        return HttpResponseRedirect(reverse('movieparties'))

    members = mp.members.all()

    if (request.user == mp.createdby):
        # party creator cannot leave
        return HttpResponseRedirect(reverse('moviepartyprofile', kwargs={'movieparty_id': movieparty_id}))

    if request.user in members:
        # user cannot leave movieparty he is NOT a member in
        mp.members.remove(request.user)
        mp.save()

    return HttpResponseRedirect(reverse('movieparties'))

def movie_party_create(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    # set user as creator of MovieParty
    mp = MovieParty(createdby=request.user)
    mp.save()
    # add user as a member to the party he just created
    mp.members.add(request.user)
    mp.save()

    return HttpResponseRedirect(reverse('moviepartyprofile', kwargs={'movieparty_id': mp.id}))

# ONLY PARTY CREATOR CAN DELETE A MOVIEPARTY
def movie_party_delete(request, movieparty_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    try:
        mp = MovieParty.objects.get(id=movieparty_id)
    except:
        return HttpResponseRedirect(reverse('movieparties'))

    if (request.user == mp.createdby):
        # party creator deleting party
        mp.delete()
        return HttpResponseRedirect(reverse('movieparties'))

    # not owner trying to delete party
    return HttpResponseRedirect(reverse('moviepartyprofile', kwargs={'movieparty_id': movieparty_id}))

def generate_report(request):
    # helpful lists
    list_movies = Movie.objects.all()
    list_users = sorted(User.objects.all(), key=lambda user: user.username)
    list_movieparties = MovieParty.objects.all()


    # total number of movies
    num_movies = len(list_movies)

    # total number of registered users
    num_users = len(list_users)

    # number of ratings done via rflix
    rflix_num_ratings = len(UserRating.objects.all())

    # total number of ratings (initial imported + user ratings via. rflix)
    total_num_ratings = 0
    for movie in list_movies:
        total_num_ratings += movie.nratings

    # average number of ratings per movie (initial imported + rflix)
    total_avg_num_ratings_per_movie = (total_num_ratings * 1.0)/num_movies

    # average number of rflix ratings per movie
    rflix_avg_num_ratings_per_movie = (rflix_num_ratings * 1.0)/num_movies

    # average number of ratings per user
    avg_num_ratings_per_user = (rflix_num_ratings * 1.0)/num_users

    # top 10 users with the most number of ratings
    users_numratings = list(map(lambda user: (user, len(user.userrating_user.all())), list_users))
    users_numratings = sorted(users_numratings, key=lambda user_numratings: user_numratings[1], reverse=True)
    users_numratings = list(map(lambda user_numratings: user_numratings[0],users_numratings))[:10]

    # number of movie parties
    num_movieparties = len(list_movieparties)

    # average number of users per party
    avg_num_users_per_party = 0
    for movieparty in list_movieparties:
        avg_num_users_per_party += len(movieparty.members.all())
    avg_num_users_per_party = (avg_num_users_per_party*1.0)/num_movieparties

    # top 10 users with the most number of memberships
    user_numparties = list(map(lambda user: (user, len(user.movieparty_user.all())), list_users))
    users_numparties = sorted(user_numparties, key=lambda user_numparties: user_numparties[1], reverse=True)[:10]
    users_numparties = list(map(lambda user_numparties: user_numparties[0],users_numparties))

    context = {'report' : Report(num_movies=num_movies,
                              num_users=num_users,
                              rflix_num_ratings = rflix_num_ratings,
                              total_num_ratings = total_num_ratings,
                              rflix_avg_num_ratings_per_movie=float("{:.4f}".format(rflix_avg_num_ratings_per_movie)),
                              total_avg_num_ratings_per_movie=float("{:.4f}".format(total_avg_num_ratings_per_movie)),
                              avg_num_ratings_per_user=float("{:.4f}".format(avg_num_ratings_per_user)),
                              top_10_users_ratings_number=users_numratings,
                              num_movieparties=num_movieparties,
                              avg_num_users_per_party=float("{:.4f}".format(avg_num_users_per_party)),
                              top_10_users_movieparty_membership=users_numparties)}
    return render(request, 'main/report.html', context)





