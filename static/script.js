const form = document.getElementById('loginForm');
const message = document.getElementById('message');

if (form && message) {
  form.addEventListener('submit', (event) => {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !password) {
      event.preventDefault();
      message.textContent = 'Please enter both username and password.';
      message.style.color = '#cf3f3f';
    } else {
      message.textContent = 'Signing in…';
      message.style.color = '#2f7dff';
    }
  });
}
