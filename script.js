const form = document.getElementById('loginForm');
const message = document.getElementById('message');

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();

  if (username && password) {
    message.textContent = `Welcome, ${username}! Your secure care dashboard is ready.`;
    message.style.color = '#1f8b4c';
  } else {
    message.textContent = 'Please enter both username and password.';
    message.style.color = '#cf3f3f';
  }
});
