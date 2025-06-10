from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # required for session

# --- Load Quiz Questions ---
with open('questions.json') as f:
    quiz_data = json.load(f)

# --- Initialize Database for Users ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Routes ---

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/categories')
def get_categories():
    return jsonify(list(quiz_data.keys()))

@app.route('/questions/<category>')
def get_questions(category):
    questions = quiz_data.get(category)
    if questions:
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


# --- Register ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registered successfully. Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
        finally:
            conn.close()

    return render_template('register.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.')

    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))


# --- Run App ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
