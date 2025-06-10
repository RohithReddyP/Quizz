from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

# Load questions from file once at startup
with open('questions.json') as f:
    quiz_data = json.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/categories')
def get_categories():
    return jsonify(list(quiz_data.keys()))

@app.route('/questions/<category>')
def get_questions(category):
    questions = quiz_data.get(category)
    if questions:
        # Do not send answers, just questions and options
        questions_no_answers = [
            {
                "question": q["question"],
                "options": q["options"]
            } for q in questions
        ]
        return jsonify(questions_no_answers)
    else:
        return jsonify({"error": "Category not found"}), 404

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    category = data.get('category')
    question_index = data.get('question_index')
    selected_option = data.get('selected_option')

    correct_answer = quiz_data[category][question_index]['answer']
    is_correct = selected_option == correct_answer

    return jsonify({"correct": is_correct})

import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))