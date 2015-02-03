# -*- coding: utf-8 -*-
"""
Created on Sun Jan 25 15:53:42 2015

@author: MatthewCohen
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data_url = 'http://bit.ly/cs109_imdb'
names = ['imdbID', 'title', 'year', 'score', 'votes', 'runtime', 'genres']
data = pd.read_csv(data_url, delimiter='\t', names=names).dropna()

print "Number of rows: %i" % data.shape[0]

data.head()

#The following snipptet converts a string like '142 mins.' to the number 142
dirty = '142 mins.'
number, text = dirty.split(' ')
clean = int(number)
print number

#We can package this up into a list comprehension
clean_runtime = [float(r.split(' ')[0]) for r in data.runtime]
data['runtime'] = clean_runtime
data.head()

data.runtime[data.runtime==0] = np.nan
data.runtime[data.runtime > 300] = np.nan



#interesting fact 1 - which genre do people like the most (rate the highest) *** Need help ***
genre_mean_score = data.groupby('genres').score.mean()


#interesting fact 2: My 5 favorite movies have an average rating of 8.24
favorite_movies = data[(data.title == 'The Matrix (1999)') | (data.title == 'Fight Club (1999)') | (data.title == 'Braveheart (1995)') | (data.title == 'Wedding Crashers (2005)') | (data.title == 'V for Vendetta (2006)')]
favorite_movies.score.mean()

#plot 1 - Average movie rating per year over time
data.groupby('year').score.mean().plot(kind='line')


#plot 2 - How many long (over 2 hrs) and bad (rating under 7) movies a year over time
long_bad_movies = data[(data.runtime > 120) & (data.score < 7.0)]
long_bad_movies.groupby('year').year.value_counts().plot(kind='line')
