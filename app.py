import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask import Flask
app = Flask(__name__)

import os

def load_courses_data():
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'dataset', 'course.csv')
    return pd.read_csv(csv_path)


# Load courses data from CSV
courses_df = load_courses_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/suggest', methods=['POST'])
def suggest():
    query = request.form['query']
    # filtered_courses = courses_df[courses_df['course_title'].str.contains(query, case=False)]
    filtered_courses = courses_df[courses_df['course_title'].str.contains(query, case=False, na=False)]

    filtered_courses = filtered_courses.head(10)
    results = []
    for _, row in filtered_courses.iterrows():
        result = {
            'course_id': row['course_id'],
            'course_title': row['course_title'],
            'url': row['url'],
            'subject': row['subject']  # Add subject information
        }
        results.append(result)

    return jsonify(results)

@app.route('/addData.html')
def add_data():
    return render_template('addData.html')


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        try:

            course_id = request.form['course_id']
            course_title = request.form['course_title']
            url = request.form['url']
            subject = request.form['subject']
            # with open('dataset/course.csv', 'a') as f:
            base_dir = os.path.dirname(__file__)
            csv_path = os.path.join(base_dir, 'dataset', 'course.csv')
            with open(csv_path, 'a') as f:
                f.write(f"\n{course_id},{course_title},{url},{subject}")
            global courses_df
            courses_df = load_courses_data()
            return 'Course added successfully!'
        except Exception as e:
            return str(e), 400  # Return the exception message and set the status code to 400

    elif request.method == 'GET':
        # Handle GET request (e.g., render the form)
        return render_template('addData.html')

if __name__ == '__main__':
    app.run(debug=True)
