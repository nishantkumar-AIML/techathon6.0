const form = document.getElementById('loginForm');
const usernameEl = document.getElementById('username');
const passwordEl = document.getElementById('password');
const rememberEl = document.getElementById('remember');
const messageEl = document.getElementById('message');
const submitBtn = document.getElementById('submitBtn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearErrors();
  messageEl.textContent = '';
  submitBtn.disabled = true;

  const payload = {
    username: usernameEl.value.trim(),
    password: passwordEl.value,
    remember: rememberEl.checked
  };

  let hasError = false;
  if (!payload.username) {
    setError('usernameError', 'Username is required');
    hasError = true;
  }
  if (!payload.password) {
    setError('passwordError', 'Password is required');
    hasError = true;
  }
  if (hasError) { submitBtn.disabled = false; return; }

  try {
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok && data.ok) {
      messageEl.textContent = data.message || 'Logged in';
      messageEl.className = 'message success';
      // For demo: store token if remember checked
      if (payload.remember) localStorage.setItem('token', data.token);
      // Mark session as authenticated so protected pages can detect it
      sessionStorage.setItem('auth', 'true');
      // Save username so protected pages can show it
      sessionStorage.setItem('username', payload.username || '');
      setTimeout(() => { window.location.href = 'secret.html'; }, 900);
    } else {
      messageEl.textContent = data.message || 'Login failed';
      messageEl.className = 'message error';
    }
  } catch (err) {
    // Network error (server not reachable). Provide a local demo fallback so
    // the page can be tested without a running backend or when opened via
    // file:// in the browser.
    console.warn('Fetch failed, using local fallback auth:', err);
    // First, check if user was registered locally (offline registration)
    try {
      const registered = JSON.parse(localStorage.getItem('registered') || '{}');
      if (registered[payload.username] && registered[payload.username].passwordHash) {
        // compute hash of entered password
        const enc = new TextEncoder();
        const data = enc.encode(payload.password);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const enteredHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        if (enteredHash === registered[payload.username].passwordHash) {
          messageEl.textContent = 'Login successful (local registered)';
          messageEl.className = 'message success';
          if (payload.remember) localStorage.setItem('token', 'fake-jwt-token');
          sessionStorage.setItem('auth', 'true');
          sessionStorage.setItem('username', payload.username || '');
          setTimeout(() => { window.location.href = 'secret.html'; }, 900);
          submitBtn.disabled = false;
          return;
        }
      }
    } catch (e) {
      console.warn('Failed to read local registered users', e);
    }
    // When offline and not found in local registered users, show an error.
    messageEl.textContent = 'Network error — unable to authenticate offline (user not registered)';
    messageEl.className = 'message error';
  } finally {
    submitBtn.disabled = false;
  }
});

function setError(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}
function clearErrors() {
  setError('usernameError', '');
  setError('passwordError', '');
}
