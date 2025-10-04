const fs = require('fs');
const crypto = require('crypto');
const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 3000;
const USERS_FILE = path.join(__dirname, 'users.json');

function loadUsers() {
  try {
    if (!fs.existsSync(USERS_FILE)) return {};
    const raw = fs.readFileSync(USERS_FILE, 'utf8');
    return JSON.parse(raw || '{}');
  } catch (err) {
    console.error('Failed to load users:', err);
    return {};
  }
}

function saveUsers(users) {
  try {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2), 'utf8');
  } catch (err) {
    console.error('Failed to save users:', err);
  }
}

function hashPassword(pw) {
  return crypto.createHash('sha256').update(pw).digest('hex');
}

// Register endpoint: saves username + hashed password
app.post('/register', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) return res.status(400).json({ ok: false, message: 'Missing username or password' });
  const users = loadUsers();
  if (users[username]) return res.status(409).json({ ok: false, message: 'User already exists' });
  users[username] = { passwordHash: hashPassword(password), createdAt: new Date().toISOString() };
  saveUsers(users);
  return res.json({ ok: true, message: 'Registered' });
});

// Login endpoint: checks stored users first, then demo password fallback
app.post('/login', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ ok: false, message: 'Missing username or password' });
  }
  const users = loadUsers();
    if (users[username] && users[username].passwordHash === hashPassword(password)) {
      return res.json({ ok: true, message: 'Login successful', token: 'fake-jwt-token' });
    }
    // No demo fallback here — require registered users only
    return res.status(401).json({ ok: false, message: 'Invalid credentials' });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
