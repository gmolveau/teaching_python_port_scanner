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
    <title>Mon Application (Sécurisée)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .success { background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .info { background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Application de Banking (simulation sécurisée)</h1>

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

    <div class="success">
        <strong>Sécurisé:</strong> Le cookie de session est configuré avec:
        <ul>
            <li><code>Secure=True</code> - Transmission uniquement sur HTTPS</li>
            <li><code>HttpOnly=True</code> - Inaccessible via JavaScript</li>
            <li><code>SameSite=Strict</code> - Protection CSRF</li>
        </ul>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    session_id = request.cookies.get("session_id")
    username = request.cookies.get("username")

    return render_template_string(
        TEMPLATE,
        logged_in=bool(session_id),
        username=username,
        session_id=session_id,
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "user")

    resp = make_response(redirect("/connected"))

    # SÉCURISÉ: Cookie avec tous les flags de sécurité
    resp.set_cookie(
        "session_id",
        "SECRET_SESSION_abc123xyz789",
        httponly=True,  # Inaccessible via JavaScript (protection XSS)
        secure=True,  # SÉCURISÉ: Transmission uniquement sur HTTPS
        samesite="Strict",  # Protection CSRF
    )
    # Cookie sans les flags de sécurité
    resp.set_cookie(
        "username",
        username,
        httponly=True,
    )

    return resp


@app.route("/connected")
def connected():
    session_id = request.cookies.get("session_id", "i dont know")
    username = request.cookies.get("username", "i dont know")

    return render_template_string(
        TEMPLATE,
        logged_in=True,
        username=username,
        session_id=session_id,
    )


@app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie("session_id")
    resp.delete_cookie("username")
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
