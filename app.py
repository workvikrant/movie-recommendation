import flask
import csv
from flask import Flask, render_template, request
import difflib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import random

app = flask.Flask(__name__, template_folder='template')

movies = pd.read_csv('C:\Users\adminn\Desktop\mrs\dataset\movies.dat')
tfidf_vector = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vector.fit_transform(movies['Genres'])
sim_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)

movies = movies.reset_index()
indices = pd.Series(movies.index, index=movies['Title'])
all_titles = [movies['Title'][i] for i in range(len(movies['Title']))]


def get_recommendations(title):
    sim_matrix2 = linear_kernel(tfidf_matrix, tfidf_matrix)
    idx = indices[title]
    sim_scores = list(enumerate(sim_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    tit = movies['Title'].iloc[movie_indices]
    dat = movies['Year'].iloc[movie_indices]

    return_df = pd.DataFrame(columns=['Title', 'Year'])
    return_df['Title'] = tit
    return_df['Year'] = dat
    return return_df


def get_suggestions():
    data = pd.read_csv('tmdb.csv')
    return list(data['Title'].str.capitalize())


app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    NewMovies = []
    with open('movie.dat', 'r') as csvfile:
        readCSV = csv.reader(csvfile)
        NewMovies.append(random.choice(list(readCSV)))
    m_name = NewMovies[0][0]
    m_name = m_name.title()

    with open('movieR.csv', 'a', newline='') as csv_file:
        fieldnames = ['Movie']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({'Movie': m_name})
        result_final = get_recommendations(m_name)
        names = []
        year = []
        for i in range(len(result_final)):
            names.append(result_final.iloc[i][0])
            year.append(result_final.iloc[i][1])
            suggestions = get_suggestions()

    return render_template('index.template', suggestions=suggestions, names=names, movie_year=year)


# Set up the main route
@app.route('/positive', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return flask.render_template('index.template')

    if flask.request.method == 'POST':
        m_name = flask.request.form['movie_name']
        m_name = m_name.title()
        if m_name not in all_titles:
            return flask.render_template('negative.template', name=m_name)
        else:
            with open('movieR.csv', 'a', newline='') as csv_file:
                fieldnames = ['Movie']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'Movie': m_name})
            result_final = get_recommendations(m_name)
            title = []
            year = []

            for i in range(len(result_final)):
                title.append(result_final.iloc[i][0])
                year.append(result_final.iloc[i][1])

            return flask.render_template('positive.template', movie_title=title, movie_year=year, search_name=m_name)


if __name__ == '__main__':
    app.run()
