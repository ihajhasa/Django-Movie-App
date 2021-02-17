"""rflix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from main import views
from registration import views as rviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', rviews.index, name='index'),
    path('movies/', views.movies, name='movies'),
    path('movies/<int:movie_id>/deleterating', views.delete_rating, name='deleterating'),
    path('login/', rviews.login_view, name='login'),
    path('registration/', rviews.register_user, name='register'),
    path('logout/', rviews.logout_view, name='logout'),
    path('rate/', views.rate_movie, name='rate'),
    path('personalrecommendation/',  views.personalized_movie_recommendation, name='personalrecommendation'),
    path('movieparties/', views.movie_parties, name='movieparties'),
    path('movieparties/<int:movieparty_id>/profile', views.movie_party_profile, name='moviepartyprofile'),
    path('movieparties/<int:movieparty_id>/join', views.movie_party_join, name='joinmovieparty'),
    path('movieparties/<int:movieparty_id>/leave', views.movie_party_leave, name='leavemovieparty'),
    path('movieparties/create', views.movie_party_create, name='createmovieparty'),
    path('movieparties/<int:movieparty_id>/delete', views.movie_party_delete, name='deletemovieparty'),
    path('report/', views.generate_report, name='report')
]

