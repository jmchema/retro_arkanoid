# Retro Arkanoid with Flask

Small Arkanoid MVP built with Flask and an HTML5 canvas frontend. Flask serves the page and static assets; the gameplay loop runs in the browser for smooth controls and collision handling.

## Requirements

- Windows with `pyenv-win` available as `pyenv`
- A Python `3.12.x` runtime installed in `pyenv`

## Setup with pyenv-win

If you do not have Python 3.12.7 installed yet:

```powershell
pyenv install 3.12.7
```

Set the project-local version:

```powershell
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

Run the app:

```powershell
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Controls

- Left Arrow / `A`: move left
- Right Arrow / `D`: move right
- Space: launch or resume
- `R`: reset the match

## MVP behavior

- Fixed brick grid
- 3 lives
- Score increases during the current session only
- Win screen when all bricks are destroyed
- Game over screen when all lives are lost
- No backend persistence and no leaderboard in this version
