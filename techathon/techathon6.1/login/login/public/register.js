const regForm = document.getElementById('registerForm');
const regUsername = document.getElementById('regUsername');
const regPassword = document.getElementById('regPassword');
const regMessage = document.getElementById('regMessage');

async function sha256(text) {
  const enc = new TextEncoder();
  const data = enc.encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

regForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  regMessage.textContent = '';
  const username = regUsername.value.trim();
  const password = regPassword.value;
  if (!username || !password) {
    regMessage.textContent = 'Username and password required';
    return;
  }
  const passwordHash = await sha256(password);
  try {
    const res = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      // Send plain password to server which also hashes; but send hash as well
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (res.ok && data.ok) {
      regMessage.textContent = 'Registered successfully — redirecting to sign in';
  // Also store locally for offline fallback (store hash, not plain pw)
  const stored = JSON.parse(localStorage.getItem('registered') || '{}');
  stored[username] = { passwordHash };
  localStorage.setItem('registered', JSON.stringify(stored));
      setTimeout(() => { window.location.href = 'index.html'; }, 900);
    } else {
      regMessage.textContent = data.message || 'Registration failed';
    }
  } catch (err) {
    // Offline: store locally
    const stored = JSON.parse(localStorage.getItem('registered') || '{}');
    if (stored[username]) {
      regMessage.textContent = 'User already exists (offline)';
      return;
    }
    stored[username] = { passwordHash };
    localStorage.setItem('registered', JSON.stringify(stored));
    regMessage.textContent = 'Registered locally (offline) — redirecting to sign in';
    setTimeout(() => { window.location.href = 'index.html'; }, 900);
  }
});
