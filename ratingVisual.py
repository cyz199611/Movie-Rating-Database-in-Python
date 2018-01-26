import sqlite3
import string

conn = sqlite3.connect('movie.sqlite')
cur = conn.cursor()

howmany = int(input('How many movies? '))

ratings = dict()
cur.execute('''SELECT title, Average_Rating FROM Movie WHERE Number_of_Rating >= 10''')
for row in cur:
    ratings[row[0]] = row[1]
cur.close()
conn.close()

sorted_ratings = sorted(ratings, key=ratings.get, reverse = True)
highest = 0
lowest = 5
for k in sorted_ratings[:howmany]:
    if highest < ratings[k]:
        highest = ratings[k]
    if lowest > ratings[k] :
        lowest = ratings[k]
print('Range of ratings:', lowest, highest)

# Spread the font sizes across 15-50 based on the count
bigsize = 50
smallsize = 15

fhand = open('rating.js','w')
fhand.write("rating = [")
first = True
for title in sorted_ratings[:howmany]:
    if not first : fhand.write( ",\n")
    first = False
    rating = ratings[title]
    # rating Normalization
    rating = (rating - lowest) / float(highest - lowest)
    rating = int((rating * bigsize) + smallsize)
    fhand.write('{text: "' + title + '", size: ' + str(rating) + "}")
fhand.write("\n];\n")

print("Output written to rating.js")
print("Open rating.htm in a browser to see the vizualization")
