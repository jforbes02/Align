# auth

This folder handles everything related to who you are and whether you're allowed to do something.

---

## account_auth.py

Uses **HTTP Basic Auth** — the simplest form of authentication. Every request that needs a logged-in user sends a username and password in the request header. There are no sessions or tokens; the server just checks the credentials each time.

---

### Key functions

**`hash_pass(password)`**
Never store a plain-text password. This runs the password through SHA-512, turning it into a scrambled string. That's what gets saved to the database.

**`get_current_user(db, cred)`**
The gatekeeper. Looks up the username in the database, hashes the provided password, and compares it to what's stored. If it doesn't match, it throws a 401 (Unauthorized) error. Used as a dependency so any route can require a logged-in user just by adding `user: CurrentUser` to its parameters.

**`create_user(username, password, db)`**
Registers a new account. Checks if the username is taken first, then hashes the password and saves the new user.

**`login_user(db, cred)`**
Same logic as `get_current_user` but called explicitly from the `/login` route. Returns the user object if credentials are correct.

**`change_pass(db, cred, new_pass)`**
Verifies the current password first, then replaces the stored hash with a new one.

**`change_username(db, cred, new_name)`**
Verifies the current password, checks the new username isn't already taken, then updates it.

---

### Shortcuts

- `CurrentUser` — drop this into any route parameter and FastAPI automatically authenticates the request and gives you the user object
- `HTTPcred` — same idea but just gives you the raw username/password credentials

---

### Note on logout
Logout happens on the Android side — the app just deletes the saved username/password from storage. The server doesn't need to do anything because there's no session to end.
