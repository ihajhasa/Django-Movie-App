from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

ratings_score = [
    (1, 'Awful'),
    (2, 'Boring'),
    (3, 'Nice'),
    (4, 'Good'),
    (5, 'Epic!!')
]

''' Provided '''
''' str function added '''
class Movie(models.Model):
    title    = models.CharField(max_length=150)
    year     = models.IntegerField(validators=[MinValueValidator(1900),
                                               MaxValueValidator(2200)],
                                   default=timezone.datetime.now().year)
    rating   = models.DecimalField(max_digits=4, decimal_places=3,
                                   validators=[MinValueValidator(0.000),
                                               MaxValueValidator(5.000)],
                                   default=0.000)
    nratings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title + ' (' + str(self.year) + ')' + '\t Global Rating: ' + str(self.rating) + '\t Rated by: ' + str(self.nratings)

'''
    UserRating:
        rating: Rating provided by the user (1-5).
        ratedby: Reference to user who's rating the movie
        ratedfor: Reference the movie that rating is about
'''
class UserRating(models.Model):

    rating = models.IntegerField(choices=ratings_score)
    ratedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userrating_user')
    ratedfor = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='userrating_movie')

'''
    MovieParty:
        id: Autonumber representing the party number (also the primary key)
        members: Reference to all the members who joined the party.
            users can be members in more than one party, and a party can contain multiple users as members
        createdby: Reeference to the user who created the party 
            so only the creator can delete the party (not asked for in doc. but thought the added restriction
            is a small extra challenge)
'''
class MovieParty(models.Model):
    id = models.AutoField(primary_key=True)
    members = models.ManyToManyField(User, related_name='movieparty_user', blank=True)
    createdby = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='movieparty_creator', null=True)

