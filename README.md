# Retro Arkanoid with Flask

Arkanoid web app built with Flask. The base game runs on an HTML5 canvas, and the `codex/usuarios` branch adds Google sign-in, SQLite persistence, saved runs, and per-user high scores.

## Requirements

- Windows with `pyenv-win` available as `pyenv`
- Python `3.12.7`
- A Google OAuth client configured for a web application

## Setup with pyenv-win

Install and select the local Python version:

```powershell
pyenv install 3.12.7
pyenv local 3.12.7
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Google OAuth configuration

Copy `.env.example` to `.env` and set real values for:

- `SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `DATABASE_URL` optional, defaults to local SQLite in `instance/arkanoid.db`

For Google Cloud Console, configure an OAuth web client with a redirect URI like:

```text
http://127.0.0.1:5000/auth/google/callback
```

## Run the app

```powershell
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Gameplay and persistence

- Users must authenticate with Google before they can play.
- Every finished run is saved in SQLite.
- The best score is shown as soon as the user enters the session.
- The sidebar also shows the most recent saved runs.
- Controls: Left Arrow or `A`, Right Arrow or `D`, `Space`, and `R`.
