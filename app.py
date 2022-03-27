import pyrebase
import streamlit as st
from datetime import datetime
import json
from Classifier import KNearestNeighbours
from operator import itemgetter

# Configuration Key
firebaseConfig = {
  'apiKey': "AIzaSyAvGCUyX73SJ_sRAQzK-TuD106PVXY3lk0",
  'authDomain': "newtesting-caacf.firebaseapp.com",
  'projectId': "newtesting-caacf",
  'databaseURL': "https://newtesting-caacf-default-rtdb.firebaseio.com/",
  'storageBucket': "newtesting-caacf.appspot.com",
  'messagingSenderId': "439187704820",
  'appId': "1:439187704820:web:b16f42cb7811359a0e47a1",
  'measurementId': "G-ENV18VE9N1"
}


# Load data and movies list from corresponding JSON files
with open(r'data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open(r'titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)

def knn(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Distances to most distant movie
    max_dist = sorted(model.distances, key=itemgetter(0))[-1]
    # Print list of 10 recommendations < Change value of k for a different number >
    table = list()
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2]])
    return table

if __name__ == '__main__':
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']

    movies = [title[0] for title in movie_titles]
    

# Login/Signup Side bar
# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()
st.sidebar.title("Our Minor 2 app")

# Authentication
choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password',type = 'password')

# App 

# Sign up Block
if choice == 'Sign up':
    handle = st.sidebar.text_input(
        'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account is created suceesfully!')
        st.balloons()
        # Sign in
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome' + handle)
        st.info('Login via login drop down selection')

# Login Block
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email,password)

        #Movie recommendation system
        st.header('Movie Recommendation System') 
        apps = ['--Select--', 'Movie based', 'Genres based']   
        app_options = st.selectbox('Select application:', apps)
        
        if app_options == 'Movie based':
            movie_select = st.selectbox('Select movie:', ['--Select--'] + movies)
            if movie_select == '--Select--':
                st.write('Select a movie')
            else:
                n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
                genres = data[movies.index(movie_select)]
                test_point = genres
                table = knn(test_point, n)
                for movie, link in table:
                    # Displays movie title with link to imdb
                    st.markdown(f"[{movie}]({link})")
        elif app_options == apps[2]:
            options = st.multiselect('Select genres:', genres)
            if options:
                imdb_score = st.slider('IMDb score:', 1, 10, 8)
                n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
                test_point = [1 if genre in options else 0 for genre in genres]
                test_point.append(imdb_score)
                table = knn(test_point, n)
                for movie, link in table:
                    # Displays movie title with link to imdb
                    st.markdown(f"[{movie}]({link})")

            else:
                    st.write("This is a simple Movie Recommender application. "
                            "You can select the genres and change the IMDb score.")

        else:
            st.write('Select option')