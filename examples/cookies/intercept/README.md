# Exemple Interception de Cookie - Flag Secure manquant

Ce dossier contient une démonstration d'interception de cookies sur le réseau lorsque le flag `Secure` n'est pas activé.

## Fichiers

- `vulnerable_server.py` - Application Flask avec cookies sans flag Secure
- `patched_server.py` - Version sécurisée avec flag Secure
- `sniffer.py` - Script pour intercepter les cookies sur le réseau

## Le problème

Quand un cookie n'a pas le flag `Secure`, il est continue d'être envoyé par le navigateur mieme si la connexion n'est pas sécurisée (pas de HTTPS) Un attaquant sur le même réseau peut donc intercepter le trafic et voler les cookies de session.

Le flag Secure dit au navigateur :

1. "Ne stocke ce cookie que si tu l'as reçu via HTTPS" (certains navigateurs)
2. "Ne renvoie ce cookie que sur des connexions HTTPS"

### Scénarios d'attaque

1. **WiFi public** - L'attaquant est sur le même réseau WiFi (café, aéroport, hôtel)
2. **Man-in-the-Middle** - L'attaquant s'intercale entre la victime et le routeur
3. **Réseau compromis** - L'attaquant a accès au réseau interne

## Comment tester

### 1. Prérequis

- Installer `uv` > <https://docs.astral.sh/uv/getting-started/installation/>

### 2. Lancer le serveur vulnérable

Terminal 1:

```bash
uv run vulnerable_server.py
```

### 3. Lancer le sniffer (nécessite sudo)

Terminal 2:

```bash
# Sur macOS (interface loopback)
sudo uv run sniffer.py -i lo0 -p 5555

# Sur Linux
sudo uv run sniffer.py -i lo -p 5555
```

### 4. Déclencher l'envoi du cookie

1. Ouvrez <http://localhost:5555> dans votre navigateur
2. Cliquez sur "Se connecter"
3. Observez le cookie intercepté dans le terminal du sniffer!
4. Cliquez sur le bouton `Se déconnecter` pour vider les cookies, ou bien les supprimer via les `devtools` du navigateur

#### Exemple de sortie du sniffer

```text
============================================================
COOKIE INTERCEPTÉ! [14:32:15]
============================================================
Source: 127.0.0.1:54321
Destination: 127.0.0.1:5555
------------------------------------------------------------
  [REQUEST] session_id=SECRET_SESSION_abc123xyz789; username=alice

URL: GET /connected
============================================================
```

### Explication du scénario

1. L'utilisateur se rend sur <http://localhost:5555/>
2. Il n'a aucun cookie stocké pour l'instant
3. En cliquant sur le bouton `Se connecter` cela crée une requête POST vers la route `/login`.
4. Cette route `/login` va renvoyer les cookies `session_id` et `username` tout en redirigeant l'utilisateur vers la route `/connected`.
5. Le navigateur reçoit les cookies, il les stocke, puis il lance la redirection en faisant une requête `GET` vers `/connected`.
6. Lors de cette requête `GET` c'est à ce moment là que le navigateur regarde si la connexion est chiffrée ou non. Si la connexion est en non chiffrée (HTTP) il n'enverra que les cookies qui n'ont **pas** le flag `Secure`

Note : en localhost le comportement du navigateur est différent car il considère que localhost est pour du dev, donc il enverra quand même tous les cookies. C'est pour cela que le sniffer les détecte. Mais vous pouvez verifier en allant dans les `devtools / storage / cookies` que le cookie `session_id` a bien le flag `Secure` activé.

## Comment se protéger

### 1. Toujours utiliser le flag Secure

```python
resp.set_cookie(
    "session_id",
    value,
    secure=True,  # Cookie transmis uniquement sur HTTPS
)
```

### 2. Forcer HTTPS partout

- Utiliser HSTS (HTTP Strict Transport Security)
- Rediriger automatiquement HTTP vers HTTPS

### 3. Configuration complète recommandée

```python
resp.set_cookie(
    "session_id",
    value,
    secure=True,       # Uniquement sur HTTPS
    httponly=True,     # Inaccessible via JavaScript
    samesite="Strict", # Protection CSRF
)
```

## Différence avec le flag HttpOnly

| Flag       | Protège contre                 |
| ---------- | ------------------------------ |
| `Secure`   | Interception réseau (sniffing) |
| `HttpOnly` | Vol via XSS (JavaScript)       |

**Les deux sont complémentaires et doivent être utilisés ensemble.**

## Scénario sécurisé

### 1. Prérequis

- Installer `uv` > <https://docs.astral.sh/uv/getting-started/installation/>
- Télécharger `bore` pour exposer le service sur internet :

```bash
curl -L https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-x86_64-unknown-linux-musl.tar.gz | tar xz -C /tmp
```

### 2. Lancer le serveur vulnérable

Terminal 1:

```bash
uv run patched_server.py
```

### 3. Exposer le service sur internet

Terminal 2:

```bash
/tmp/bore local 5555 --to bore.pub
```

Vous devriez voir dans le terminal une sortie similaire à :

```text
2026-01-24T09:25:43.623742Z  INFO bore_cli::client: connected to server remote_port=13609
2026-01-24T09:25:43.623847Z  INFO bore_cli::client: listening at bore.pub:13609
```

### 3. Lancer le sniffer (nécessite sudo)

Terminal 2:

```bash
sudo uv run sniffer.py -i all -p 5555
```

### 4. Déclencher l'envoi du cookie

1. Ouvrez <http://localhost:5555> dans votre navigateur
2. Cliquez sur "Se connecter"
3. Observez le cookie intercepté dans le terminal du sniffer
4. Dans les requêtes de login on peut effectivement voir les cookies passés, meme le cookie `session_id`. C'est attendu puisque le navigateur va recevoir ce cookie. Le flag `Secure` ne protège pas contre ce cas de figure.
5. Par contre on remarque que pour les requêtes qui suivent, il n'y a que le cookie `username` qui est transmis. Le flag `Secure` de `session_id` fonctionne donc bien :) La navigateur a détecté que la connection etait en HTTP et n'a donc pas transmis le cookie `session_id`.

```text
============================================================
COOKIE INTERCEPTÉ! [10:29:07]
============================================================
Source: 192.168.2.5:51711
Destination: 159.223.171.199:13609
------------------------------------------------------------
  [REQUEST] username=alice

URL: GET /connected
============================================================
```
