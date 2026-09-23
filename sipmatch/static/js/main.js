const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.main-nav');

if (navToggle && nav) {
  navToggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(open));
  });
}

document.querySelectorAll('.prompt-chips button').forEach((button) => {
  button.addEventListener('click', () => {
    const input = document.querySelector('#question');
    if (input) {
      input.value = button.dataset.prompt || '';
      input.focus();
    }
  });
});

const quizRoot = document.querySelector('[data-quiz]');
if (quizRoot) {
  const questions = [
    {
      question: 'A wine described as “tannic” will feel…',
      options: ['Sweet and syrupy', 'Dry and grippy', 'Fizzy and sharp'],
      answer: 1,
      note: 'Tannins create a drying, grippy sensation—similar to strong black tea.'
    },
    {
      question: 'What does “body” describe in a drink?',
      options: ['Its alcohol percentage only', 'Its color', 'Its weight and texture'],
      answer: 2,
      note: 'Body is how light or substantial a drink feels in your mouth, like skim milk versus cream.'
    },
    {
      question: 'High acidity usually makes a drink feel…',
      options: ['Fresh and mouth-watering', 'Heavy and smoky', 'Extra sweet'],
      answer: 0,
      note: 'Acidity brings freshness and makes your mouth water—think of biting into a crisp apple.'
    },
    {
      question: 'The “finish” is…',
      options: ['The last bottle produced', 'The flavor that lingers after a sip', 'The bottle label texture'],
      answer: 1,
      note: 'A finish can be short, long, warming, fruity, spicy, or many other things.'
    },
    {
      question: 'Which drink is usually friendliest with spicy food?',
      options: ['A high-alcohol tannic red', 'A lightly sweet, lower-alcohol white', 'A very bitter spirit'],
      answer: 1,
      note: 'A little sweetness calms heat, while lower alcohol avoids turning it up.'
    }
  ];

  let current = 0;
  let score = 0;
  const questionEl = quizRoot.querySelector('[data-question]');
  const optionsEl = quizRoot.querySelector('[data-options]');
  const feedbackEl = quizRoot.querySelector('[data-feedback]');
  const nextButton = quizRoot.querySelector('[data-next]');
  const progressBar = quizRoot.querySelector('[data-progress-bar]');
  const progressText = quizRoot.querySelector('[data-progress-text]');

  function renderQuestion() {
    const item = questions[current];
    questionEl.textContent = item.question;
    optionsEl.innerHTML = '';
    feedbackEl.innerHTML = '';
    nextButton.classList.add('hidden');
    progressText.textContent = String(current + 1);
    progressBar.style.width = `${((current + 1) / questions.length) * 100}%`;
    item.options.forEach((option, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'quiz-option';
      button.textContent = option;
      button.addEventListener('click', () => selectAnswer(index));
      optionsEl.appendChild(button);
    });
  }

  function selectAnswer(index) {
    const item = questions[current];
    const buttons = [...optionsEl.querySelectorAll('button')];
    buttons.forEach((button) => { button.disabled = true; });
    buttons[item.answer].classList.add('correct');
    if (index === item.answer) {
      score += 1;
      feedbackEl.innerHTML = `<strong>That’s it.</strong>${item.note}`;
    } else {
      buttons[index].classList.add('incorrect');
      feedbackEl.innerHTML = `<strong>Good guess—here’s the trick.</strong>${item.note}`;
    }
    nextButton.textContent = current === questions.length - 1 ? 'See my score →' : 'Next question →';
    nextButton.classList.remove('hidden');
  }

  nextButton.addEventListener('click', () => {
    current += 1;
    if (current < questions.length) {
      renderQuestion();
      return;
    }
    questionEl.textContent = `You got ${score} out of ${questions.length}.`;
    optionsEl.innerHTML = '<p>You now know enough to ask better questions—and that is the whole point.</p>';
    feedbackEl.innerHTML = '';
    nextButton.textContent = 'Try again';
    nextButton.classList.remove('hidden');
    nextButton.onclick = () => window.location.reload();
    progressBar.style.width = '100%';
  });

  renderQuestion();
}

window.setTimeout(() => {
  document.querySelectorAll('.flash').forEach((flash) => {
    flash.style.opacity = '0';
    window.setTimeout(() => flash.remove(), 300);
  });
}, 5000);
