Django-RFlix-Movie-Rating-And-Recommendation-Project

Submission By: Ishaq Haj Hasan
Submission Date: 06 - April - 2020

( Started Code provided by Rimads )

Rflix Django Annotated is provided because it includes my annotations + notes about certain tasks and might provide you
with some insight on my thought process.
	Green annotations are tasks completed
	Blue annotations are tasks completed but somewhat not to my liking
	Certain annotations contain notes

Gneral Usage:
	to run the program, make sure (PREREQS):
			Django is installed
			Python is installed
			Crispy_forms is installed (Styling for Django forms in HTML)
			PostgreSQL is installed with a database that has the proper permissions according to settings.py

		$ cd .../rflix
		$ python manage.py makemigrations
	
		(if migrations occur):
			$ python manage.py migrate

		$python manage.py runserver

		take the url:port that is provided by django in the terminal after the server starts running. Plug that into the browser

	to use the webpage:
		usage should be straight forward.

		A link is provided to register and login

		
		the navigation top bar will direct you to the main pages of the program

		To rate a movie:
			Click on 'Movies' in the Navigation Top Bar to go to the Movies Page
			Find a movie in the unrated movies section that you would like to rate
			Drag the slider for said movie to the desired score

		to modify:
			Click on 'Movies' in the Navigation Top Bar to go to the Movies Page
			Find a movie in the rateed movies section that you would like to modify the rating for
			Drag the slider for said movie to the new desired score

		to delete:
			Click on 'Movies' in the Navigation Top Bar to go to the Movies Page
			Find a movie in the rated movies section that you would like to delete the rating for
			Click the delete rating button

		to join/leave/delete a movie party:
			Click on 'Movie Parties' in the Navigation Top Bar to go to the Movie Parties page
			Find the desired movie party, and click Join/Leave/Delete Party button underneath it

			OR

			Click on 'Movie Parties' in the Navigation Top Bar to go to the Movie Parties page
			Find the desired movie party, and click Party Profile button
			Click the Join/Leave/Delete Party button in the left column

		to create a party:
			Click on 'Movie Parties' in the Navigation Top Bar to go to the Movie Parties page
			Click the Create Party button in the left column

Main Issue with the program:
	The thing I dislike the most about my program is that the Movies page displays all the movies, and since there were around 8000+ movies provided
	It takes a while for the browser to load the page so I wouldv'e loved to develop a paging grid to display a portion and can flip between the pages
	as I believe it would reduce the stress on the browser.

One bonus feature I would've implemented:
	Provided a search functionality for the movies page where you could search movies by their title.

Hope you enjoy using the program,
Ishaq Haj Hasan

			


		