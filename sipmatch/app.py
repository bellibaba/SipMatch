"""SipMatch Flask application.

This prototype favors a reliable classroom demo: recommendations are deterministic,
OCR is local, and every image result can fall back to a manual catalogue search.
"""

from __future__ import annotations

import os
import re
from functools import wraps
from typing import Any, Callable

import mysql.connector
import pytesseract
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from PIL import Image, UnidentifiedImageError
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


def get_db() -> mysql.connector.MySQLConnection:
    """Create a short-lived connection suitable for a small prototype."""
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "sipmatch"),
        password=os.environ.get("DB_PASSWORD", "sipmatch"),
        database=os.environ.get("DB_NAME", "sipmatch"),
    )


def query_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def query_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(sql, params)
    connection.commit()
    row_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return row_id


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if "user_id" not in session:
            flash("Please log in to continue.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def current_user() -> dict[str, Any] | None:
    if "user_id" not in session:
        return None
    return query_one(
        "SELECT id, name, email FROM users WHERE id = %s", (session["user_id"],)
    )


@app.context_processor
def inject_user() -> dict[str, Any]:
    return {"current_user": current_user()}


@app.get("/")
def home() -> str:
    featured = query_all(
        "SELECT * FROM drinks ORDER BY aggregate_rating DESC, rating_count DESC LIMIT 3"
    )
    return render_template("index.html", featured=featured)


@app.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter a name, email, and password of at least 6 characters.", "error")
        elif query_one("SELECT id FROM users WHERE email = %s", (email,)):
            flash("An account with that email already exists.", "error")
        else:
            user_id = execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, generate_password_hash(password)),
            )
            session.clear()
            session["user_id"] = user_id
            flash("Welcome to SipMatch. Let’s learn your taste.", "success")
            return redirect(url_for("onboarding"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = query_one("SELECT * FROM users WHERE email = %s", (email,))
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name']}.", "success")
            return redirect(url_for("drinks"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html")


@app.get("/logout")
def logout() -> Any:
    session.clear()
    flash("You’re logged out.", "info")
    return redirect(url_for("home"))


@app.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding() -> str:
    preference = query_one(
        "SELECT * FROM user_preferences WHERE user_id = %s", (session["user_id"],)
    )
    if request.method == "POST":
        values = (
            request.form.get("sweetness", "medium"),
            request.form.get("acidity", "medium"),
            request.form.get("strength", "medium"),
            request.form.get("preferred_type", "Any"),
            request.form.get("past_purchases", "").strip(),
            session["user_id"],
        )
        execute(
            """
            INSERT INTO user_preferences
                (sweetness, acidity, strength, preferred_type, past_purchases, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE sweetness=VALUES(sweetness), acidity=VALUES(acidity),
                strength=VALUES(strength), preferred_type=VALUES(preferred_type),
                past_purchases=VALUES(past_purchases)
            """,
            values,
        )
        flash("Your taste profile is ready.", "success")
        return redirect(url_for("drinks"))
    return render_template("onboarding.html", preference=preference or {})


def recommendation_score(drink: dict[str, Any], pref: dict[str, Any]) -> float:
    """Rank catalogue items using transparent, presentation-friendly weights."""
    levels = {"low": 1, "medium": 2, "high": 3}
    score = float(drink["aggregate_rating"] or 0)
    for attribute in ("sweetness", "acidity", "strength"):
        wanted = levels.get(str(pref.get(attribute, "medium")).lower(), 2)
        actual = levels.get(str(drink[attribute]).lower(), 2)
        score += max(0, 2 - abs(wanted - actual)) * 1.2
    preferred_type = str(pref.get("preferred_type", "Any"))
    if preferred_type.lower() == str(drink["type"]).lower():
        score += 2.5
    return score


def attach_pairings(drinks_found: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for drink in drinks_found:
        drink["pairings"] = query_all(
            """
            SELECT s.name, s.description, p.reason
            FROM pairings p JOIN snacks s ON s.id = p.snack_id
            WHERE p.drink_id = %s LIMIT 3
            """,
            (drink["id"],),
        )
    return drinks_found


def search_catalogue(search: str) -> list[dict[str, Any]]:
    wildcard = f"%{search}%"
    return query_all(
        """
        SELECT * FROM drinks
        WHERE name LIKE %s OR type LIKE %s OR flavor_profile LIKE %s
        ORDER BY aggregate_rating DESC LIMIT 10
        """,
        (wildcard, wildcard, wildcard),
    )


@app.route("/drinks", methods=["GET", "POST"])
@login_required
def drinks() -> str:
    search = request.values.get("q", "").strip()
    ocr_text = ""
    message = ""
    results: list[dict[str, Any]] = []

    if request.method == "POST" and request.files.get("shelf_photo"):
        photo = request.files["shelf_photo"]
        try:
            image = Image.open(photo.stream)
            ocr_text = pytesseract.image_to_string(image).strip()
            tokens = [t for t in re.findall(r"[A-Za-z]{3,}", ocr_text) if len(t) > 3]
            # Search the most distinctive OCR tokens; loose matching keeps the demo forgiving.
            matches: dict[int, dict[str, Any]] = {}
            for token in tokens[:12]:
                for item in search_catalogue(token):
                    matches[item["id"]] = item
            results = list(matches.values())
            message = (
                f"Matched {len(results)} catalogue item(s) from the visible label text."
                if results
                else "No confident match—try the manual search below."
            )
        except (UnidentifiedImageError, OSError):
            message = "That image could not be read. Try JPG/PNG or use manual search."
    elif search:
        results = search_catalogue(search)
        message = f"Showing matches for “{search}”."
    else:
        pref = query_one(
            "SELECT * FROM user_preferences WHERE user_id = %s", (session["user_id"],)
        ) or {}
        catalogue = query_all("SELECT * FROM drinks")
        results = sorted(catalogue, key=lambda item: recommendation_score(item, pref), reverse=True)[:6]
        message = "Top matches for your taste profile."

    return render_template(
        "drinks.html",
        drinks=attach_pairings(results),
        message=message,
        ocr_text=ocr_text,
        search=search,
    )


@app.post("/rate/<int:drink_id>")
@login_required
def rate_drink(drink_id: int) -> Any:
    try:
        rating = float(request.form.get("rating", "0"))
    except ValueError:
        rating = 0
    if rating < 1 or rating > 5 or (rating * 2) % 1:
        flash("Choose a rating from 1 to 5 in half-star steps.", "error")
        return redirect(request.referrer or url_for("drinks"))
    execute(
        """
        INSERT INTO ratings (user_id, drink_id, rating) VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE rating=VALUES(rating), rated_at=CURRENT_TIMESTAMP
        """,
        (session["user_id"], drink_id, rating),
    )
    execute(
        """
        UPDATE drinks d SET
            d.aggregate_rating=(SELECT ROUND(AVG(r.rating), 2) FROM ratings r WHERE r.drink_id=d.id),
            d.rating_count=(SELECT COUNT(*) FROM ratings r WHERE r.drink_id=d.id)
        WHERE d.id=%s
        """,
        (drink_id,),
    )
    flash("Rating saved—your future recommendations will use it.", "success")
    return redirect(request.referrer or url_for("drinks"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile() -> str:
    user = current_user()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        existing = query_one(
            "SELECT id FROM users WHERE email=%s AND id<>%s", (email, session["user_id"])
        )
        if not name or not email or existing:
            flash("Enter a unique email and a name.", "error")
        else:
            execute(
                "UPDATE users SET name=%s, email=%s WHERE id=%s",
                (name, email, session["user_id"]),
            )
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))
    preference = query_one(
        "SELECT * FROM user_preferences WHERE user_id=%s", (session["user_id"],)
    )
    history = query_all(
        """
        SELECT d.name, d.type, r.rating, r.rated_at FROM ratings r
        JOIN drinks d ON d.id=r.drink_id WHERE r.user_id=%s ORDER BY r.rated_at DESC
        """,
        (session["user_id"],),
    )
    return render_template("profile.html", user=user, preference=preference, history=history)


@app.get("/glossary")
def glossary() -> str:
    return render_template("glossary.html")


def chatbot_answer(question: str) -> str:
    text = question.lower()
    if any(word in text for word in ("sweet", "fruity", "easy")):
        return "Try Moscato or Riesling: both are fruit-forward and approachable. Pair with fruit, soft cheese, or something lightly spicy."
    if "tannin" in text or "tannic" in text:
        return "Tannins create the drying sensation you get from strong tea. They help bold red wines stand up to fatty foods and aged cheese."
    if "acidity" in text or "acidic" in text:
        return "Acidity is mouth-watering freshness. High-acid drinks work well with rich or salty foods because they reset the palate."
    if "beer" in text:
        return "For crisp and light, try a pilsner; for citrus and bitterness, try an IPA; for roasted flavors, try a stout."
    if "pair" in text or "food" in text or "snack" in text:
        return "A handy rule: match intensity, then use contrast. Rich foods like freshness, spicy foods like lower alcohol and a little sweetness."
    if "strong" in text or "spirit" in text or "whiskey" in text:
        return "If you like bold, warming flavors, explore bourbon with vanilla and caramel notes. Sip slowly and pair with dark chocolate or smoked nuts."
    return "Tell me whether you prefer sweet or dry, light or bold, and what you’re eating—I’ll narrow it down. You can also ask me about tannins, acidity, beer, or pairing rules."


@app.route("/chat", methods=["GET", "POST"])
def chat() -> str:
    question = ""
    answer = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()[:500]
        if question:
            answer = chatbot_answer(question)
    return render_template("chat.html", question=question, answer=answer)


@app.errorhandler(413)
def too_large(_: Any) -> tuple[str, int]:
    return render_template("error.html", message="Image too large. Please upload one under 8 MB."), 413


@app.errorhandler(404)
def not_found(_: Any) -> tuple[str, int]:
    return render_template("error.html", message="That page isn’t on our menu."), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")
