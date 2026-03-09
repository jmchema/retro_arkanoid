import os
from datetime import datetime, timezone
from pathlib import Path

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


load_dotenv()


db = SQLAlchemy()
oauth = OAuth()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_sub = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    game_sessions = db.relationship("GameSession", back_populates="user", cascade="all, delete-orphan")


class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    won = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user = db.relationship("User", back_populates="game_sessions")


def create_app() -> Flask:
    app = Flask(__name__)

    instance_dir = Path(app.instance_path)
    instance_dir.mkdir(parents=True, exist_ok=True)

    default_db_path = instance_dir / "arkanoid.db"
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path.as_posix()}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    oauth.init_app(app)

    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if google_client_id and google_client_secret:
        oauth.register(
            name="google",
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    with app.app_context():
        db.create_all()

    @app.before_request
    def load_current_user() -> None:
        user_id = session.get("user_id")
        g.current_user = db.session.get(User, user_id) if user_id else None

    def google_enabled() -> bool:
        return "google" in oauth._registry

    def build_home_context():
        user = g.current_user
        if not user:
            return {
                "authenticated": False,
                "google_enabled": google_enabled(),
            }

        recent_games = (
            GameSession.query.filter_by(user_id=user.id)
            .order_by(GameSession.created_at.desc())
            .limit(5)
            .all()
        )
        total_games_count = GameSession.query.filter_by(user_id=user.id).count()
        max_score = (
            db.session.query(func.max(GameSession.score))
            .filter(GameSession.user_id == user.id)
            .scalar()
        ) or 0
        return {
            "authenticated": True,
            "google_enabled": google_enabled(),
            "user": user,
            "max_score": max_score,
            "total_games_count": total_games_count,
            "recent_games": recent_games,
            "recent_games_data": [
                {
                    "score": game.score,
                    "won": game.won,
                    "created_at": game.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for game in recent_games
            ],
        }

    @app.get("/")
    def index():
        return render_template("index.html", **build_home_context())

    @app.get("/login/google")
    def login_google():
        if g.current_user:
            return redirect(url_for("index"))
        if not google_enabled():
            flash("Google OAuth is not configured yet.", "error")
            return redirect(url_for("index"))

        redirect_uri = url_for("auth_google_callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    @app.get("/auth/google/callback")
    def auth_google_callback():
        if request.args.get("error"):
            flash("Google sign-in was cancelled or failed.", "error")
            return redirect(url_for("index"))

        if not google_enabled():
            flash("Google OAuth is not configured yet.", "error")
            return redirect(url_for("index"))

        try:
            token = oauth.google.authorize_access_token()
            userinfo = token.get("userinfo")
            if not userinfo:
                userinfo = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo").json()
        except Exception:
            flash("Unable to complete Google sign-in.", "error")
            return redirect(url_for("index"))

        google_sub = userinfo.get("sub")
        email = userinfo.get("email")
        display_name = userinfo.get("name") or email
        if not google_sub or not email:
            flash("Google did not return the required account details.", "error")
            return redirect(url_for("index"))

        user = User.query.filter_by(google_sub=google_sub).first()
        if user is None:
            user = User(
                google_sub=google_sub,
                email=email,
                display_name=display_name,
                avatar_url=userinfo.get("picture"),
            )
            db.session.add(user)
        else:
            user.email = email
            user.display_name = display_name
            user.avatar_url = userinfo.get("picture")

        db.session.commit()
        session.clear()
        session["user_id"] = user.id
        return redirect(url_for("index"))

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.post("/api/games")
    def save_game():
        if not g.current_user:
            return jsonify({"error": "authentication_required"}), 401

        payload = request.get_json(silent=True) or {}
        score = payload.get("score")
        won = payload.get("won")
        if not isinstance(score, int) or score < 0 or not isinstance(won, bool):
            return jsonify({"error": "invalid_payload"}), 400

        game = GameSession(user_id=g.current_user.id, score=score, won=won)
        db.session.add(game)
        db.session.commit()

        max_score = (
            db.session.query(func.max(GameSession.score))
            .filter(GameSession.user_id == g.current_user.id)
            .scalar()
        ) or 0
        total_games_count = GameSession.query.filter_by(user_id=g.current_user.id).count()

        return jsonify(
            {
                "score": game.score,
                "max_score": max_score,
                "won": game.won,
                "created_at": game.created_at.strftime("%Y-%m-%d %H:%M"),
                "total_games_count": total_games_count,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
