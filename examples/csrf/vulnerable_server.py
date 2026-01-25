# /// script
# dependencies = [
#   "flask",
# ]
# ///

from flask import Flask, make_response, render_template_string, request

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# Simulated user balance
user_data = {"balance": 1000, "transfers": []}

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ma Banque - Espace Client</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c5282; }
        .balance { font-size: 2em; color: #2f855a; margin: 20px 0; }
        form { background: #edf2f7; padding: 20px; border-radius: 5px; margin: 20px 0; }
        input { padding: 10px; margin: 5px 0; width: 200px; }
        button { padding: 10px 20px; background: #3182ce; color: white; border: none; cursor: pointer; border-radius: 5px; }
        button:hover { background: #2c5282; }
        .transfers { margin-top: 20px; }
        .transfer { background: #fed7d7; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .warning { background: #fef3c7; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 Ma Banque</h1>
        <p>Bienvenue, <strong>{{ username }}</strong>!</p>

        <div class="balance">Solde: {{ balance }} €</div>

        <h3>Effectuer un virement</h3>
        <form method="POST" action="/transfer">
            <div>
                <label>Destinataire:</label><br>
                <input type="text" name="to" placeholder="Nom du destinataire">
            </div>
            <div>
                <label>Montant (€):</label><br>
                <input type="number" name="amount" placeholder="100">
            </div>
            <br>
            <button type="submit">Envoyer</button>
        </form>

        {% if transfers %}
        <div class="transfers">
            <h3>Historique des virements:</h3>
            {% for t in transfers %}
            <div class="transfer">➡️ {{ t.amount }} € envoyé à {{ t.to }}</div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="warning">
            ⚠️ <strong>Application vulnérable au CSRF</strong> - À des fins éducatives uniquement.<br>
            Aucun token CSRF n'est utilisé pour valider les requêtes.
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    resp = make_response(
        render_template_string(
            TEMPLATE,
            username="Alice",
            balance=user_data["balance"],
            transfers=user_data["transfers"],
        )
    )
    # Set session cookie (simulating logged-in user)
    resp.set_cookie("session_id", "alice_session_123")
    return resp


@app.route("/transfer", methods=["POST"])
def transfer():
    # VULNÉRABILITÉ: Pas de vérification de token CSRF!
    # N'importe quel site peut soumettre ce formulaire si l'utilisateur est connecté

    to = request.form.get("to", "Inconnu")
    amount = int(request.form.get("amount", 0))

    if amount > 0 and amount <= user_data["balance"]:
        user_data["balance"] -= amount
        user_data["transfers"].append({"to": to, "amount": amount})
        print(f"[!] VIREMENT EFFECTUÉ: {amount}€ vers {to}")

    return render_template_string(
        TEMPLATE,
        username="Alice",
        balance=user_data["balance"],
        transfers=user_data["transfers"],
    )


if __name__ == "__main__":
    print("=" * 60)
    print("APPLICATION VULNÉRABLE AU CSRF - ÉDUCATION UNIQUEMENT!")
    print("=" * 60)
    print("\n1. Ouvrez http://localhost:5000 dans votre navigateur")
    print("   (Cela simule un utilisateur connecté à sa banque)")
    print("\n2. Dans un autre onglet, ouvrez attacker_page.html")
    print("   (Cela simule une visite sur un site malveillant)")
    print("\n3. Observez qu'un virement a été effectué sans votre consentement!")
    print("=" * 60)
    print("\n")
    app.run(port=5000)
