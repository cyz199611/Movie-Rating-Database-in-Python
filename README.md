Summary
========================
This project uses sqlite database to store the movie rating from [MovieLens](http://movielens.org), a movie recommendation service.
The data contains 100004 ratings and 1296 tag applications across 9125 movies. These data were created by 671 users between January 09, 1995 and October 16, 2016. This dataset was generated on October 17, 2016.

Files information
=======================
`movie.csv` and `rating.csv` is the dataset from MovieLens

`rating.py` is the program to communicate with the database and store all the necessary information to a database called `movie.sqlite`

`ratingDump.py` is the program that gives recommendation to users based on the average rating of the movies in database

`d3.layout.cloud.js` and `d3.v2.js` are two libraries used in this project to generate the word cloud visualization of the movie based on their average rating

`ratingVisual.py` is the one that generates the word_size of each movie and output to a javaScript file `rating.js`, the js file will be used to show the word cloud

`rating.htm` will be used to visualize the word cloud diagram
