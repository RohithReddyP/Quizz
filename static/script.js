let categoriesDiv = document.getElementById('categories');
let categorySelectDiv = document.getElementById('category-select');
let quizContainer = document.getElementById('quiz-container');
let questionEl = document.getElementById('question');
let optionsEl = document.getElementById('options');
let nextBtn = document.getElementById('next-btn');
let scoreEl = document.getElementById('score');
let resultDiv = document.getElementById('result');
let finalScoreEl = document.getElementById('final-score');
let restartBtn = document.getElementById('restart-btn');

let selectedCategory = null;
let questions = [];
let currentQuestionIndex = 0;
let score = 0;

async function fetchCategories() {
  const res = await fetch('/categories');
  const categories = await res.json();
  categories.forEach(cat => {
    let btn = document.createElement('button');
    btn.textContent = cat;
    btn.onclick = () => startQuiz(cat);
    categoriesDiv.appendChild(btn);
  });
}

async function startQuiz(category) {
  selectedCategory = category;
  currentQuestionIndex = 0;
  score = 0;
  categorySelectDiv.style.display = 'none';
  quizContainer.style.display = 'block';
  resultDiv.style.display = 'none';
  scoreEl.textContent = '';
  nextBtn.disabled = true;

  // Fetch questions for category from backend
  const res = await fetch(`/questions/${category}`);
  questions = await res.json();

  showQuestion();
}

function showQuestion() {
  nextBtn.disabled = true;
  let currentQuestion = questions[currentQuestionIndex];
  questionEl.textContent = `Q${currentQuestionIndex + 1}: ${currentQuestion.question}`;
  optionsEl.innerHTML = '';

  currentQuestion.options.forEach(option => {
    let btn = document.createElement('button');
    btn.className = 'option';
    btn.textContent = option;
    btn.onclick = () => selectAnswer(option, btn);
    optionsEl.appendChild(btn);
  });
}

async function selectAnswer(selected, btn) {
  const optionButtons = optionsEl.querySelectorAll('button');
  optionButtons.forEach(b => b.disabled = true);

  // Check answer from backend
  const res = await fetch('/check_answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      category: selectedCategory,
      question_index: currentQuestionIndex,
      selected_option: selected
    })
  });
  const data = await res.json();

  if (data.correct) {
    score++;
    btn.style.backgroundColor = '#90ee90';
  } else {
    btn.style.backgroundColor = '#f08080';
    optionButtons.forEach(b => {
      if (b.textContent === questions[currentQuestionIndex].answer) {
        b.style.backgroundColor = '#90ee90';
      }
    });
  }
  scoreEl.textContent = `Score: ${score} / ${currentQuestionIndex + 1}`;
  nextBtn.disabled = false;
}

nextBtn.addEventListener('click', () => {
  currentQuestionIndex++;
  if (currentQuestionIndex < questions.length) {
    showQuestion();
  } else {
    showResult();
  }
});

restartBtn.addEventListener('click', () => {
  categorySelectDiv.style.display = 'block';
  quizContainer.style.display = 'none';
  resultDiv.style.display = 'none';
  score = 0;
  currentQuestionIndex = 0;
  scoreEl.textContent = '';
});


function showResult() {
  quizContainer.style.display = 'none';
  resultDiv.style.display = 'block';
  finalScoreEl.textContent = `Your final score is ${score} out of ${questions.length}`;
}

fetchCategories();
