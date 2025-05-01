import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from implicit.als import AlternatingLeastSquares
from scipy.sparse import coo_matrix

# Content-Based Recommendation System
def content_based_recommendation(user_input, courses_df):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(courses_df['description'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    idx = courses_df[courses_df['title'] == user_input].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    course_indices = [i[0] for i in sim_scores]
    return courses_df['title'].iloc[course_indices]

# Collaborative Filtering Recommendation System with ALS
def collaborative_filtering_recommendation(user_id, ratings_data, courses_df):
    # Create sparse user-item matrix
    sparse_matrix = ratings_data.pivot(index='user_id', columns='course_id', values='rating').fillna(0)
    # Convert to scipy.sparse matrix
    sparse_matrix = coo_matrix(sparse_matrix.values)
    # Initialize ALS model
    model = AlternatingLeastSquares(factors=50)
    # Fit the model
    model.fit(sparse_matrix)
    # Get recommended courses for the user
    rec_course_ids = model.recommend(user_id, sparse_matrix, N=5)
    # Get course titles based on recommended course IDs
    rec_course_titles = courses_df[courses_df['course_id'].isin([rec[0] for rec in rec_course_ids])]['title']
    return rec_course_titles

# Hybrid Recommendation System
def hybrid_recommendation(user_id, user_input, courses_df, ratings_data):
    content_based_rec = content_based_recommendation(user_input, courses_df)
    collaborative_filtering_rec = collaborative_filtering_recommendation(user_id, ratings_data, courses_df)
    # Combine recommendations from different systems
    hybrid_rec = content_based_rec.append(collaborative_filtering_rec).unique()[:5]
    return hybrid_rec
