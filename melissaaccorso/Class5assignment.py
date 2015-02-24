# -*- coding: utf-8 -*-
"""
Created on Thu Feb 5 19:20:35 2015

@author: melaccor
"""

#importing division from the future release of python (i.e. Python 3)
from __future__ import division

import numpy
import sqlite3
import pandas
from sklearn.neighbors import KNeighborsClassifier

CROSS_VALIDATION_AMOUNT =.2

conn=sqlite3.connect('C:\\Users\\melaccor\\Documents\\SQLite\\lahman2013.sqlite')
#Create a SQL table to pull data from all 4 Tables in the Baseball database: HallOfFame, Batting, Pitching, Fielding
sql= """select a.playerID as playerID, max(a.inducted) as inducted, sum(g.Games) as games, sum(g.Hits) as hits, 
sum(g.atbats) as atbats, sum(g.homeruns) as homeruns, sum(g.doubleplays) as doubleplays, sum(g.fielderassists) as fielderassists, sum(g.fielderrors) as fielderrors 
from HallOfFame a 
left outer join (select b.G as games, b.H as hits, b.AB as atbats, b.HR as homeruns, b.playerID, e.fielderassists, e.doubleplays, e.fielderrors  
from Batting b
left outer join (select d.playerID, d.A as fielderassists, d.E as fielderrors, d.DP as doubleplays from Fielding d) e on b.playerID = e.playerID)g
on a.playerID = g.playerID
where yearID<2000
and g.games is not null 
group by a.playerID;"""
df= pandas.read_sql(sql,conn)
conn.close()
df.dropna(inplace=True)

#KNN Model

#separate response variable from explanatory variables
response_series = df.inducted
explanatory_vars = df[['games','hits','atbats','homeruns','doubleplays','fielderassists','fielderrors']]

# designating the number of observations we need to hold out
holdout_num = round(len(df.index) * CROSS_VALIDATION_AMOUNT, 0)

#creating training and test indices
test_indices = numpy.random.choice(df.index, holdout_num, replace = False)
train_indices = df.index[~df.index.isin(test_indices)] 

#create training set
response_train = response_series.ix[train_indices,]
explanatory_train = explanatory_vars.ix[train_indices,]

#create test set 
response_test = response_series.ix[test_indices,]
explanatory_test = explanatory_vars.ix[test_indices,]

#Instantiating the KNN Classifier, with p=2 for Euclidian distance
KNN_Classifier = KNeighborsClassifier(n_neighbors=3,p=2)

#fitting the data to training set
KNN_Classifier.fit(explanatory_train,response_train)

#predicting the data on test set
predicted_response = KNN_Classifier.predict(explanatory_test)

#calculating accuracy
number_correct = len(response_test[response_test == predicted_response])
total_in_test_set = len(response_test)
accuracy = number_correct/total_in_test_set
print accuracy*100


#K-Fold CV


#let's use 10-fold cross-validation to score model
from sklearn.cross_validation import cross_val_score
#we need to re-instantiate the model 
KNN_classifier = KNeighborsClassifier(n_neighbors=3, p = 2)
scores = cross_val_score(KNN_classifier, explanatory_vars, response_series, cv=10, scoring='accuracy')
#let's print out the accuracy at each itration of cross-validation.
print scores
#now, let's get the average accuracy score
mean_accuracy = numpy.mean(scores) 
print mean_accuracy * 100
#look at how this differs from the previous accuracy we computed
print accuracy*100

#now, let's tune the model for the optimal number of K. 
k_range = range(1, 30, 2)
scores = []
for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k,  p = 2)
    scores.append(numpy.mean(cross_val_score(knn, explanatory_vars, response_series, cv=10, scoring='accuracy')))

#plot the K values (x-axis) versus the 5-fold CV score (y-axis)
import matplotlib.pyplot as plt
plt.figure()
plt.plot(k_range, scores)
#so, the optimal value of K appears to be low

#automatic grid search for an optimal value of K
from sklearn.grid_search import GridSearchCV
knn = KNeighborsClassifier( p = 2)
k_range = range(1, 30, 2)
param_grid = dict(n_neighbors=k_range)
grid = GridSearchCV(knn, param_grid, cv=10, scoring='accuracy')
grid.fit(explanatory_vars, response_series)

#check the results of the grid search and extract the optial estimator
grid.grid_scores_
grid_mean_scores = [result[1] for result in grid.grid_scores_]
plt.figure()
plt.plot(k_range, grid_mean_scores)
best_oob_score = grid.best_score_
grid.best_params_
Knn_optimal = grid.best_estimator_
