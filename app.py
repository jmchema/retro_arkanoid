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

SUPPORTED_LANGUAGES = ("es", "en")
TRANSLATIONS = {
    "es": {
        "app_title": "Retro Arkanoid",
        "app_badge": "Arkanoid Online",
        "auth_title": "Elige como quieres jugar",
        "auth_copy": "Puedes entrar con Google para guardar tu historial y tu puntuacion maxima, o jugar como invitado sin guardar tus partidas.",
        "continue_google": "Continuar con Google",
        "play_guest": "Jugar como invitado",
        "guest_mode_tag": "Modo libre",
        "google_not_configured": "La autenticacion con Google todavia no esta configurada.",
        "google_not_configured_help": "La autenticacion con Google todavia no esta configurada. Anade las variables de entorno de .env.example para activar el acceso.",
        "logged_in_as": "Sesion iniciada como",
        "guest_access_mode": "Modo de acceso",
        "guest_user": "Invitado",
        "guest_description": "Tus partidas no se guardan en este modo.",
        "best_score": "Puntuacion maxima",
        "saved_runs": "Partidas guardadas",
        "recent_runs": "Ultimas partidas",
        "guest_mode_title": "Modo invitado",
        "guest_mode_history": "Puedes jugar libremente, pero el historial y los records solo se guardan si entras con Google.",
        "no_saved_runs": "Todavia no hay partidas guardadas. Termina una para crear tu historial.",
        "score": "Puntuacion",
        "lives": "Vidas",
        "authenticated_subtitle": "Rompe todos los bloques. Cada partida completada se guarda en tu cuenta.",
        "guest_subtitle": "Estas jugando como invitado. Tus partidas no se guardaran.",
        "game_area_label": "Zona de juego de Arkanoid",
        "ready": "Listo",
        "start_prompt": "Pulsa Espacio para empezar",
        "move_prompt": "Usa las flechas izquierda y derecha para mover la barra.",
        "start_game": "Empezar partida",
        "controls_label": "Controles:",
        "controls_move": "Flechas izquierda y derecha",
        "controls_restart": "Reinicia cuando quieras con",
        "logout": "Cerrar sesion",
        "exit": "Salir",
        "victory": "Victoria",
        "defeat": "Derrota",
        "pause": "Pausa",
        "retry": "Reintento",
        "space_to_launch": "PULSA ESPACIO PARA LANZAR",
        "play_again": "Jugar otra vez",
        "you_win": "Has ganado",
        "win_message": "Puntuacion final: {score}. Pulsa R o usa el boton para volver a jugar.",
        "win_message_guest": "Puntuacion final: {score}. Estas jugando como invitado, asi que esta partida no se guardara.",
        "game_over": "Fin de la partida",
        "game_over_message": "Has conseguido {score} puntos. Pulsa R para intentarlo de nuevo.",
        "game_over_message_guest": "Has conseguido {score} puntos. Pulsa R para volver a jugar como invitado.",
        "ball_lost": "Has perdido la bola",
        "ball_lost_message": "Todavia te quedan {lives} vidas. Pulsa Espacio para continuar.",
        "save_game_error": "No se ha podido guardar la partida",
        "google_cancelled": "El inicio de sesion con Google se ha cancelado o ha fallado.",
        "google_failed": "No se ha podido completar el inicio de sesion con Google.",
        "google_missing_data": "Google no ha devuelto los datos de cuenta necesarios.",
        "lang_es": "ES",
        "lang_en": "EN",
        "language_label": "Idioma",
    },
    "en": {
        "app_title": "Retro Arkanoid",
        "app_badge": "Arkanoid Online",
        "auth_title": "Choose how you want to play",
        "auth_copy": "You can sign in with Google to save your history and high score, or play as a guest without saving your games.",
        "continue_google": "Continue with Google",
        "play_guest": "Play as guest",
        "guest_mode_tag": "Free mode",
        "google_not_configured": "Google authentication is not configured yet.",
        "google_not_configured_help": "Google authentication is not configured yet. Add the environment variables from .env.example to enable access.",
        "logged_in_as": "Signed in as",
        "guest_access_mode": "Access mode",
        "guest_user": "Guest",
        "guest_description": "Your games are not saved in this mode.",
        "best_score": "Best score",
        "saved_runs": "Saved runs",
        "recent_runs": "Recent runs",
        "guest_mode_title": "Guest mode",
        "guest_mode_history": "You can play freely, but history and records are only saved if you sign in with Google.",
        "no_saved_runs": "There are no saved runs yet. Finish one to create your history.",
        "score": "Score",
        "lives": "Lives",
        "authenticated_subtitle": "Break every brick. Every completed run is saved to your account.",
        "guest_subtitle": "You are playing as a guest. Your games will not be saved.",
        "game_area_label": "Arkanoid play area",
        "ready": "Ready",
        "start_prompt": "Press Space to start",
        "move_prompt": "Use the left and right arrows to move the paddle.",
        "start_game": "Start game",
        "controls_label": "Controls:",
        "controls_move": "Left and right arrows",
        "controls_restart": "Restart anytime with",
        "logout": "Log out",
        "exit": "Exit",
        "victory": "Victory",
        "defeat": "Defeat",
        "pause": "Pause",
        "retry": "Retry",
        "space_to_launch": "PRESS SPACE TO LAUNCH",
        "play_again": "Play again",
        "you_win": "You win",
        "win_message": "Final score: {score}. Press R or use the button to play again.",
        "win_message_guest": "Final score: {score}. You are playing as a guest, so this run will not be saved.",
        "game_over": "Game over",
        "game_over_message": "You scored {score} points. Press R to try again.",
        "game_over_message_guest": "You scored {score} points. Press R to play again as a guest.",
        "ball_lost": "Ball lost",
        "ball_lost_message": "You still have {lives} lives. Press Space to continue.",
        "save_game_error": "The game could not be saved",
        "google_cancelled": "Google sign-in was cancelled or failed.",
        "google_failed": "Google sign-in could not be completed.",
        "google_missing_data": "Google did not return the required account data.",
        "lang_es": "ES",
        "lang_en": "EN",
        "language_label": "Language",
    },
}


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
    app.config["BASE_URL"] = os.getenv("BASE_URL", "").rstrip("/")
    app.config["HOST"] = os.getenv("HOST", "0.0.0.0")
    app.config["PORT"] = int(os.getenv("PORT", "5000"))
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "1") == "1"

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

    def detect_language() -> str:
        cookie_language = request.cookies.get("language")
        if cookie_language in SUPPORTED_LANGUAGES:
            return cookie_language
        matched = request.accept_languages.best_match(SUPPORTED_LANGUAGES)
        return matched or "es"

    def translate(key: str, **kwargs) -> str:
        language = getattr(g, "language", "es")
        text = TRANSLATIONS.get(language, TRANSLATIONS["es"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    @app.context_processor
    def inject_i18n():
        return {
            "t": translate,
            "current_lang": getattr(g, "language", "es"),
            "languages": SUPPORTED_LANGUAGES,
        }

    @app.before_request
    def load_request_context() -> None:
        user_id = session.get("user_id")
        g.current_user = db.session.get(User, user_id) if user_id else None
        g.is_anonymous_guest = session.get("is_anonymous_guest", False)
        g.language = detect_language()

    def google_enabled() -> bool:
        return "google" in oauth._registry

    def build_google_redirect_uri() -> str:
        if app.config["BASE_URL"]:
            return f"{app.config['BASE_URL']}{url_for('auth_google_callback')}"
        return url_for("auth_google_callback", _external=True)

    def game_translations() -> dict[str, str]:
        return {
            key: translate(key)
            for key in (
                "pause",
                "play_again",
                "start_game",
                "space_to_launch",
                "you_win",
                "victory",
                "defeat",
                "retry",
                "game_over",
                "ball_lost",
                "ready",
                "start_prompt",
                "move_prompt",
                "save_game_error",
            )
        }

    def build_home_context():
        base_context = {
            "google_enabled": google_enabled(),
            "game_translations": game_translations(),
        }

        if g.current_user:
            recent_games = (
                GameSession.query.filter_by(user_id=g.current_user.id)
                .order_by(GameSession.created_at.desc())
                .limit(5)
                .all()
            )
            total_games_count = GameSession.query.filter_by(user_id=g.current_user.id).count()
            max_score = (
                db.session.query(func.max(GameSession.score))
                .filter(GameSession.user_id == g.current_user.id)
                .scalar()
            ) or 0
            return {
                **base_context,
                "authenticated": True,
                "is_anonymous_guest": False,
                "can_save_scores": True,
                "user": g.current_user,
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

        if g.is_anonymous_guest:
            return {
                **base_context,
                "authenticated": True,
                "is_anonymous_guest": True,
                "can_save_scores": False,
                "user": None,
                "max_score": 0,
                "total_games_count": 0,
                "recent_games": [],
                "recent_games_data": [],
            }

        return {
            **base_context,
            "authenticated": False,
            "is_anonymous_guest": False,
            "can_save_scores": False,
        }

    @app.get("/")
    def index():
        return render_template("index.html", **build_home_context())

    @app.get("/language/<code>")
    def set_language(code: str):
        if code not in SUPPORTED_LANGUAGES:
            code = "es"
        next_url = request.args.get("next") or url_for("index")
        if not next_url.startswith("/"):
            next_url = url_for("index")
        response = redirect(next_url)
        response.set_cookie("language", code, max_age=60 * 60 * 24 * 365, samesite="Lax")
        return response

    @app.get("/login/anonymous")
    def login_anonymous():
        session.clear()
        session["is_anonymous_guest"] = True
        return redirect(url_for("index"))

    @app.get("/login/google")
    def login_google():
        if g.current_user:
            return redirect(url_for("index"))
        if not google_enabled():
            flash(translate("google_not_configured"), "error")
            return redirect(url_for("index"))

        return oauth.google.authorize_redirect(build_google_redirect_uri())

    @app.get("/auth/google/callback")
    def auth_google_callback():
        if request.args.get("error"):
            flash(translate("google_cancelled"), "error")
            return redirect(url_for("index"))

        if not google_enabled():
            flash(translate("google_not_configured"), "error")
            return redirect(url_for("index"))

        try:
            token = oauth.google.authorize_access_token()
            userinfo = token.get("userinfo")
            if not userinfo:
                userinfo = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo").json()
        except Exception:
            flash(translate("google_failed"), "error")
            return redirect(url_for("index"))

        google_sub = userinfo.get("sub")
        email = userinfo.get("email")
        display_name = userinfo.get("name") or email
        if not google_sub or not email:
            flash(translate("google_missing_data"), "error")
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
        if g.is_anonymous_guest:
            return jsonify({"error": "guest_mode_no_persistence"}), 200

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
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
