# /// script
# dependencies = [
#   "flask",
# ]
# ///
from flask import Flask, make_response, redirect, render_template_string, request

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mon Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .warning { background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .info { background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Application de Banking (simulation)</h1>

    {% if logged_in %}
        <div class="info">
            <h2>Bienvenue, {{ username }}!</h2>
            <p>Votre solde: <strong>10,000 EUR</strong></p>
            <p>Session ID: <code>{{ session_id }}</code></p>
        </div>
        <p><a href="/logout">Se déconnecter</a></p>
    {% else %}
        <h2>Connexion</h2>
        <form method="POST" action="/login">
            <p>
                <label>Utilisateur:</label><br>
                <input type="text" name="username" value="alice">
            </p>
            <p>
                <label>Mot de passe:</label><br>
                <input type="password" name="password" value="password123">
            </p>
            <button type="submit">Se connecter</button>
        </form>
    {% endif %}

    <div class="warning">
        <strong>Vulnérabilité:</strong> Le cookie de session est envoyé sans le flag
        <code>Secure</code>, il peut donc être intercepté sur une connexion HTTP non chiffrée.
    </div>
</body>
</html>
"""


@app.get("/")
def index():
    session_id = request.cookies.get("session_id")
    username = request.cookies.get("username")

    return render_template_string(
        TEMPLATE,
        logged_in=bool(session_id),
        username=username,
        session_id=session_id,
    )


@app.post("/login")
def login():
    username = request.form.get("username", "user")

    resp = make_response(redirect("/connected"))

    # VULNÉRABILITÉ: Cookies sans le flag Secure!
    # Ces cookies seront transmis en clair sur HTTP
    resp.set_cookie(
        "session_id",
        "SECRET_SESSION_abc123xyz789",
        httponly=True,  # Protégé contre XSS, mais...
        secure=False,  # VULNÉRABLE: Pas de flag Secure!
        samesite="Lax",
    )
    resp.set_cookie(
        "username",
        username,
        secure=False,  # VULNÉRABLE: Pas de flag Secure!
    )

    return resp


@app.get("/connected")
def connected():
    session_id = request.cookies.get("session_id")
    username = request.cookies.get("username")

    if not session_id:
        return redirect("/")

    return render_template_string(
        TEMPLATE,
        logged_in=True,
        username=username,
        session_id=session_id,
    )


@app.get("/logout")
def logout():
    resp = redirect("/")
    resp.delete_cookie("session_id")
    resp.delete_cookie("username")
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
