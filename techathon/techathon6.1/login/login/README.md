# Login Demo

A minimal login + registration demo: static frontend with an Express backend that persists users to `users.json`.

Quick start (Windows PowerShell):

```powershell
cd D:\login
npm install
npm start
# Open http://localhost:3000 in your browser
```

Register and sign in:
- Visit `/register.html` to create an account (or use the Register link on the sign-in page).
- After registering you can sign in at `/index.html`.

Demo fallback:
- If the server is not running, the app supports offline registration (stored in browser `localStorage`) and offline login.
- Demo password (always accepted when server offline): `password123`.

Notes:
- This is a demo. Do NOT use this code in production without adding proper security (HTTPS, salted password hashing, sessions/JWT signing, rate-limiting).
- Server stores users in `users.json` in the project root when running.
