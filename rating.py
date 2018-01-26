import csv
import re
import sqlite3
import time
from numpy import mean

# Read file 'movies.csv' and store the results in a list 
movies = dict() # movie dict
with open('movie.csv') as csvfile:
	data = csv.reader(csvfile, delimiter = ',')
	first_line = True
	for row in data:
		if first_line:
			first_line = False
			continue
		movies[int(row[0])] = row[1:]
	csvfile.close()

# Read file 'rating.csv' and store the results in a list 
f = open('rating.csv')
line_num = sum([1 for line in f])
f.close()
ratings = [0] * line_num
with open('rating.csv') as csvfile:
	data = csv.reader(csvfile, delimiter = ',')
	count = 0
	for row in data:
		ratings[count] = row[:3]
		count += 1
	csvfile.close()
ratings = ratings[1:] # rating list

# Create sqlite file
conn = sqlite3.connect('movie.sqlite')
cur = conn.cursor()
# cur.execute('SELECT Number_of_Rating from Movie')
# print(sum([row[0] for row in cur if row[0] != None]))

cur.execute('''CREATE TABLE IF NOT EXISTS Movie
	(id INTEGER UNIQUE, title TEXT, year INTEGER, Number_of_Rating INTEGER, 
	Average_Rating REAL, updated BOOLEAN)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Rating 
	(user_id INTEGER, movie_id INTEGER, rating REAL, PRIMARY KEY (user_id, movie_id) )''')
cur.execute('CREATE TABLE IF NOT EXISTS Genre (id INTEGER UNIQUE, name TEXT UNIQUE)')
cur.execute('''CREATE TABLE IF NOT EXISTS Movie_Genre 
	(movie_id INTEGER, genre_id INTEGER, PRIMARY KEY (movie_id, genre_id) )''')

genres = list() # create a genre list
for movie_id, info in movies.items():
	if info[1] == '(no genres listed)': genre = ['Not listed']
	else: genre = info[1].split('|')
	for word in genre:
		if word not in genres: genres.append(word)

genre_id = 1
# Data to insert into Genre table
for genre in genres:
	cur.execute('INSERT OR IGNORE INTO Genre (id, name) VALUES ( ?, ? )', (genre_id, genre))
	genre_id += 1

# Initialize the Movie table by setting all movies not updated
for movie_id, info in movies.items():
	cur.execute('INSERT OR IGNORE INTO Movie (id, updated) values ( ?, ? )', (movie_id, 0))

# Data to insert into Rating table
for rating in ratings:
	# If we find a (user_id, movie_id) pair that is not in the Rating table, then we need to 
	# update the corresponding movie.
	cur.execute('SELECT movie_id FROM Rating WHERE user_id = ? AND movie_id = ?', 
		(rating[0], rating[1]))
	row = cur.fetchone()
	if row is not None: continue 

	user_id = int(rating[0])
	movie_id = int(rating[1])
	rate = rating[2]
	cur.execute('UPDATE Movie SET updated = ? WHERE id  = ?', (0, movie_id))
	cur.execute('''INSERT OR IGNORE INTO Rating (user_id, movie_id, rating) VALUES ( ?, ?, ? )''', 
		(user_id, movie_id, rate))

conn.commit()

count = 0
# Data to insert into Movie table
for movie_id, info in movies.items():
	# If the movie is already updated, continue to the next movie
	cur.execute('SELECT updated, title FROM Movie WHERE id = ?', (movie_id, ))
	row = cur.fetchone()
	if row is None: continue
	updated = row[0]
	title = row[1] 
	if updated == 1: continue

	count += 1
	if count%1000 == 0: 
		conn.commit()
		time.sleep(3)

	cur.execute('SELECT rating FROM Rating WHERE movie_id = ? ', (movie_id, ))
	rows = cur.fetchall()
	number = len(rows) # Number of Rating

	# If no users rated this movie, we treat it as an updated movie
	if number == 0: 
		title = re.findall('(.*) \([0-9]{4}[-0-9]*\)', info[0]) # title
		if len(title) == 1: title = title[0] 
		if re.match('.*, The$', title): 
			title = title[:-5]

		genre = info[1] # genre
		if genre == '(no genres listed)': genre = ['Not listed']
		else: genre = genre.split('|')
		for word in genre:
			cur.execute('SELECT id FROM Genre WHERE name = ? ', (word, ))
			genre_id = cur.fetchone()[0] # genre_id
			cur.execute('''INSERT OR IGNORE INTO Movie_Genre (movie_id, genre_id)
				VALUES ( ?, ? )''', (movie_id, genre_id))

		year = re.findall('\([0-9]{4}[-0-9]*\)', info[0]) # year
		if len(year) == 1: year = int(year[0][1:5]) 

		cur.execute('''UPDATE Movie SET title = ?, year = ?, Number_of_Rating = ?, 
			updated = ? WHERE id = ?''', (title, year, number, 1, movie_id))

		continue

	average_rating = mean([row[0] for row in rows]) # Average Rating

	if title is None: # If the movie is not in the database
		title = re.findall('(.*) \([0-9]{4}[-0-9]*\)', info[0])
		if len(title) == 1: title = title[0] # title
		if re.match('.*, The$', title): 
			title = title[:-5]

		genre = info[1] # genre
		if genre == '(no genres listed)': genre = ['Not listed']
		else: genre = genre.split('|')
		for word in genre:
			cur.execute('SELECT id FROM Genre WHERE name = ? ', (word, ))
			genre_id = cur.fetchone()[0] # genre_id
			cur.execute('''INSERT OR IGNORE INTO Movie_Genre (movie_id, genre_id) 
				VALUES ( ?, ? )''', (movie_id, genre_id))

		year = re.findall('\([0-9]{4}[-0-9]*\)', info[0]) # year
		if len(year) == 1: year = int(year[0][1:5])

		cur.execute('''UPDATE Movie SET title = ?, year = ?, Number_of_Rating = ?, 
			Average_Rating = ?, updated = ? WHERE id = ?''', 
			(title, year, number, average_rating, 1, movie_id))
	else: # The movie is already in the database
		cur.execute('''UPDATE Movie SET Number_of_Rating = ?, Average_Rating = ?, 
			updated = ? WHERE id = ?''', (number, average_rating, 1, movie_id))


conn.commit()
cur.close()
conn.close()


