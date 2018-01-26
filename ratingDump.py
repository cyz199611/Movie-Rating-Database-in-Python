import sqlite3

howmany = int(input('How many movies? '))

conn = sqlite3.connect('movie.sqlite')
cur = conn.cursor()

cur.execute('''SELECT id, title, year, Number_of_Rating, Average_Rating FROM Movie 
	WHERE Number_of_Rating >= 10 ORDER BY Average_Rating DESC, id''')

rows = cur.fetchall()
for row in rows[:howmany]:
	cur.execute('''SELECT Genre.name FROM Genre JOIN Movie_Genre 
		ON Genre.id = Movie_Genre.genre_id 
		WHERE Movie_Genre.movie_id = ? ''', (row[0], ))
	genre = cur.fetchall()
	genre = [ item[0] for item in genre ] 
	string = '\nTitle: ' + row[1] + '\nYear: ' + str(row[2]) + '\nGenre: ' + ', '.join(genre) + \
	         '\nNumber of Rating: ' + str(row[3]) + '\nAverage Rating: ' + str(row[4])
	print(string)

cur.close()
conn.close()
