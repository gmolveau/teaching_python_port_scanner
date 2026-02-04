# Exercice 3 : Sessions et protection des routes

## Introduction

Dans les TP précédents, nous avons implémenté un système de register/login. Cependant, une fois connecté, l'application ne "se souvient" pas de l'utilisateur. Si vous rafraîchissez la page home `/`, vous n'êtes plus connecté.

Dans ce TP, nous allons :

1. Comprendre ce qu'est une session et un cookie
2. Implémenter un système de session "à la main"
3. Protéger certaines routes pour les utilisateurs connectés uniquement

---

## Partie 1 : Théorie - Sessions et Cookies

Le protocole HTTP ne garde aucune mémoire entre les requêtes. Chaque requête est indépendante. Le serveur ne sait pas si deux requêtes viennent du même utilisateur.

### Comment les sites web modernes gèrent-ils la connexion alors ?

**Question** : Comment un site comme Gmail sait-il que vous êtes connecté quand vous naviguez entre les pages ?

La réponse : les **cookies** et les **sessions**. Ces mécanismes ont été ajoutés "par-dessus" HTTP pour simuler un état et permettre au serveur de reconnaître un utilisateur d'une requête à l'autre.

### Une solution possible : Les cookies

Un **cookie** est un fichier texte stocké par le navigateur. Le serveur peut demander au navigateur de stocker un cookie, et le navigateur renverra automatiquement ce cookie à chaque requête vers ce serveur.

```plaintext
1. Client → Serveur : POST /login (username=alice, password=secret)
2. Serveur → Client : "OK, voici un cookie à garder" (Set-Cookie: user=alice)
3. Client → Serveur : GET /scan (Cookie: user=alice)
4. Le serveur sait maintenant que c'est Alice !
```

### Anatomie d'un cookie

Un cookie possède plusieurs attributs :

| Attribut              | Description                                   |
| --------------------- | --------------------------------------------- |
| `name=value`          | Le nom et la valeur du cookie                 |
| `Expires` / `Max-Age` | Durée de vie du cookie                        |
| `HttpOnly`            | Le cookie n'est pas accessible via JavaScript |
| `Secure`              | Le cookie n'est envoyé que sur HTTPS          |
| `SameSite`            | Protection contre les attaques CSRF           |

### ⚠️ Pourquoi ne pas stocker directement le nom d'utilisateur dans le cookie ?

Si on stocke simplement `user=alice` dans un cookie, n'importe qui peut modifier son cookie pour mettre `user=admin` et usurper l'identité d'un autre utilisateur !

Les cookies sont stockés côté client et peuvent être modifiés (via les DevTools du navigateur par exemple).

### Méthode 1 : Les sessions côté serveur

Au lieu de stocker les données utilisateur dans le cookie, on stocke uniquement un **identifiant de session** (session ID). Les vraies données sont elles stockées côté serveur.

```plaintext
┌─────────────────┐                    ┌───────────────────────────┐
│    NAVIGATEUR   │                    │     SERVEUR               │
│                 │                    │                           │
│  Cookie:        │                    │  Sessions:                │
│  session_id=    │    ─────────►      │  abc123 → {               │
│  abc123         │                    │    user: alice,           │
│                 │                    │    logged: true           │
│                 │                    │    last_login: 01/01/2001 │
│                 │                    │  }                        │
└─────────────────┘                    └───────────────────────────┘
```

**Avantages** :

- Le client ne peut pas modifier les données de session
- Les données sensibles restent sur le serveur
- On peut invalider une session côté serveur (déconnexion forcée) en la supprimant du serveur

### ⚠️ Attaques sur les sessions

#### 1. Session Hijacking (vol de session)

Si un attaquant obtient votre session ID, il peut usurper votre identité. C'est pourquoi :

- Les session IDs doivent être **aléatoires et impossibles à deviner**
- Il faut activer le paramètre `HttpOnly` pour empêcher le vol via [XSS](https://www.kaspersky.fr/resource-center/definitions/what-is-a-cross-site-scripting-attack)
- On utilise `Secure` pour empêcher l'interception sur le réseau

Le flag Secure dit au navigateur :

1. "Ne stocke ce cookie que si tu l'as reçu via HTTPS" (certains navigateurs)
2. "Ne renvoie ce cookie que sur des connexions HTTPS"

Rendez-vous dans `examples/cookies/xss` pour un exemple concret de XSS puis dans `examples/cookies/intercept` pour un exemple d'interception de cookie.

#### 2. Session Fixation

L'attaquant force la victime à utiliser un session ID qu'il connaît. Solution : **régénérer le session ID après le login**.

#### 3. CSRF (Cross-Site Request Forgery)

Un site malveillant fait exécuter des actions à votre insu en utilisant votre session. Solution : utiliser la propriété `SameSite` et des tokens CSRF.

<https://laconsole.dev/formations/attaques-web/csrf#comprendre-par-lexemple>

Rendez-vous dans `examples/csfr` pour un exemple concret de CSRF.

---

## Partie 2 : Implémentation manuelle des sessions

Nous allons implémenter un système de session simple sans plugin, sans extension flask pour le moment.

### Étape 1 : Créer le stockage des sessions

Rappel : Lorsqu'un utilisateur va se connecter, notre application doit générer un identifiant de session unique, qu'elle va transmettre ensuite au navigateur sous forme d'un cookie. Le navigateur renverra ensuite ce cookie pour **chaque** requête. Notre application devra donc lire le cookie à chaque requête et vérifier si l'ID de session est valide afin de retrouver l'utilisateur correspondant.

Pour débuter, nous allons stocker ces ID de sessions dans un dictionnaire.
La clé sera l'ID, et la valeur sera un dictionnaire de 3 champs :

- `user_id` : l'ID de l'utilisateur
- `created_at` : la date de création de cette session
- `expires_at` : la date d'expiration de cette session

Dans un nouveau fichier `src/services/sessions.py`, nous allons créer le dictionnaire qui va stocker les sessions, ainsi que des fonctions utiles :

- `generate_session_id`
- `create_session`
- `get_session`
- `delete_session`

```python
# src/services/sessions.py
import secrets
from datetime import datetime, timedelta

# Stockage des sessions en mémoire (dictionnaire)
# En production, on utiliserait Redis ou une base de données
SESSIONS = {}

# Durée de vie d'une session
SESSION_LIFETIME = timedelta(minutes=1440)


def generate_session_id():
    """
    Génère un identifiant de session sécurisé.
    secrets.token_hex génère une chaîne aléatoire cryptographiquement sûre.
    """
    return secrets.token_hex(32)  # 64 caractères hexadécimaux


def create_session(user_id: str) -> str:
    """
    Crée une nouvelle session pour un utilisateur.
    Retourne le session_id à stocker dans le cookie.
    """
    session_id = generate_session_id()
    SESSIONS[session_id] = {
        "user_id": user_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + SESSION_LIFETIME,
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    """
    Récupère les données d'une session.
    Retourne None si la session n'existe pas ou a expiré.
    """
    if session_id not in SESSIONS:
        return None

    session = SESSIONS[session_id]

    # Vérifier si la session a expiré
    if datetime.now() > session["expires_at"]:
        # Supprimer la session expirée
        del SESSIONS[session_id]
        return None

    return session


def delete_session(session_id: str) -> bool:
    """
    Supprime une session (déconnexion).
    Retourne True si la session existait.
    """
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        return True
    return False
```

### Étape 2 : Modifier le login pour créer une session

Maintenant que le mécanisme de création/récupération/suppression de sessions est fait, il faut modifier la logique de login pour créer une session.

Modifiez `src/auth.py` pour créer une session après un login réussi :

```python
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from src.db import get_db_connection
from src.services.users import get_user_by_username, create_user, user_exists
from src.services.sessions import create_session, delete_session, get_session

auth_blueprint = Blueprint("auth", __name__)

# ... (code du register inchangé)


@auth_blueprint.post("/login")
def post_login():
    form = request.form.to_dict()
    username = form.get("username")
    password = form.get("password")

    user = get_user_by_username(username)
    if user is None:
        return redirect(url_for("auth.login_page"))

    if not check_password_hash(user["password"], password):
        return redirect(url_for("auth.login_page"))

    # Créer une session pour l'utilisateur
    session_id = create_session(username)

    # Créer la réponse avec le cookie de session
    response = redirect(url_for("forms.home"))
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,      # Non accessible via JavaScript
        samesite="Lax",     # Protection CSRF basique
        max_age=86400,      # 24 heures en secondes
        secure=True,
    )

    return response
```

### Étape 3 : Implémenter la déconnexion

Ajoutez une route `/logout` dans `src/auth.py` qui se chargera de supprimer la session de l'utilisateur et de demander au navigateur de supprimer le cookie.

```python
@auth_blueprint.get("/logout")
def logout():
    # Récupérer le session_id depuis le cookie
    session_id = request.cookies.get("session_id")

    if session_id:
        # Supprimer la session côté serveur
        delete_session(session_id)

    # Créer une réponse qui supprime le cookie
    response = redirect(url_for("auth.login_page"))
    response.delete_cookie("session_id")

    return response
```

### Étape 4 : Créer une fonction pour récupérer l'utilisateur courant

Le mécanisme de session est presque complet. Il nous manque une fonction essentielle, celle qui nous permet de récupérer `l'utilisateur` ; dans notre cas il s'agit de récupérer l'ID de l'utilisateur.

Ajoutez cette fonction dans `src/services/sessions.py` :

```python
def get_current_user(request) -> str | None:
    """
    Récupère l'utilisateur actuellement connecté à partir de la requête.
    Retourne None si l'utilisateur n'est pas connecté.
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    session = get_session(session_id)
    if not session:
        return None

    return session["user_id"]
```

### Étape 5 : Protection d'une route - version simple v1

Maintenant que tout le mécanisme de session et de vérification est en place, nous pouvons `protéger` certaines routes pour faire en sorte que seul un utilisateur connecté puisse y avoir accès.

Dans cette version simple `v1`, pour **chaque** route que l'on souhaite protéger, nous devrons rajouter ce snippet de code au début de la fonction de la route.

```python
current_user = get_current_user(request)
if not current_user:
    return redirect(url_for("auth.login_page"))
```

*QUESTION 1* : quel est le principal inconvénient de cette façon de faire ?

Implémentons cette v1 en modifiant la route `/scan` pour vérifier que l'utilisateur est connecté :

```python
# Dans src/forms.py (ou là où se trouve votre route /scan)
from src.services.sessions import get_current_user


@forms_blueprint.get("/")
def home():
    # Récupérer l'utilisateur connecté (peut être None)
    current_user = get_current_user(request)
    return render_template("index.html", user=current_user)


@forms_blueprint.post("/scan")
def scan_form():
    # Vérifier que l'utilisateur est connecté
    current_user = get_current_user(request)
    if not current_user:
        return redirect(url_for("auth.login_page"))

    # ... reste du code du scan
```

### Étape 6 : Créer un décorateur `@login_required`

*REPONSE 1* : cela crée une recopie de code pour **chaque** route à protéger.

Pour éviter de répéter le code de vérification, nous allons **factoriser** cette logique dans un décorateur.

Rappel sur les décorateurs : <https://python.doctor/page-decorateurs-decorator-python-cours-debutants> (site ancien mais l'explication est OK)

Ajoutons le décorateur dans `src/services/sessions.py` :

```python
from functools import wraps
from flask import request, redirect, url_for


def login_required(f):
    """
    Décorateur qui protège une route.
    Redirige vers /login si l'utilisateur n'est pas connecté.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user(request)
        if not current_user:
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated_function
```

Exemple d'utilisation du nouveau décorateur `@login_required` :

```python
@blueprint.get("/")
@login_required
def unefonction():
    # Plus besoin de vérifier manuellement !
    # Le code ici ne s'exécute que si l'utilisateur est connecté
    # ...
```

---

## Partie 3 : Exercice pratique

### À faire

0. **Implémenter le système de sessions** en suivant les étapes ci-dessus

1. **Créer un blueprint pour une page d'accueil non authentifiée** :
    - Créer un nouveau fichier `src/home.py` avec un blueprint `home_blueprint` pour la page d'accueil qui sera accessible sur `/`.
    - Ajoutez ce blueprint à la liste des blueprint dans `src/__init__.py`
    - Dupliquer le fichier `src/templates/index.html` en `src/templates/dashboard.html`
    - Modifier le template `src/templates/index.html` pour n'avoir qu'un titre, un lien pour login et un lien pour register.

2. **Créer un blueprint dashboard authentifié**
    - Actuellement la page d'accueil existe déjà dans `src/forms.py`. Pour éviter les conflits, renommer `src/forms.py` en `src/dashboard.py`, renommez `forms_blueprint` en `dashboard_blueprint` (penser à mettre à jour l'import dans `src/__init__.py`)
    - Changer la route `GET /` de ce blueprint par `GET /dashboard`
    - Protéger l'endpoint `GET /dashboard` avec `@login_required`
    - Protéger l'endpoint `POST /scan` avec `@login_required`
    - Modifier la route de login pour rediriger vers le dashboard
    - Rajouter un lien vers `/logout` dans le template `dashboard.html`

3. **Modifier la route d'accueil** pour rediriger automatiquement vers `/dashboard` si l'utilisateur est déjà authentifié.

4. **Protéger la route `/scan`** avec le décorateur `@login_required`

5. **Tester le workflow complet** :
    - Vérifier que la DB sqlite existe, ou la créer avec `python3 create_db`
    - Lancer l'app avec `flask --app src run --debug`
    - Se rendre sur <http://localhost:5000/>
    - Se rendre sur la page de register et créer un compte
    - Se connecter
    - Verifier que la redirection vers le dashboard fonctionne bien
    - Ouvrir les devtools et voir qu'un cookie de session existe bien
    - Cliquer sur le bouton `Logout` et etre redirigé vers la page d'accueil
    - Se rendre sur `/dashboard` sans être connecté → redirection vers `/login`
    - Avec l'outil de votre choix pour parler avec une API, essayer d'envoyer une requete `POST /scan` pour verifier que la verification de session est bien active.

6. **Regrouper les routes ensemble** dans un dossier `src/routes` :
    - déplacer les fichiers contenant des routes (`auth`, `dashboard`, `home`) dans un nouveau dossier `src/routes` (penser à créer un fichier `__init__.py` vide dans ce dossier)

### Questions de réflexion

1. Que se passe-t-il si le serveur redémarre ? Un utilisateur qui était connecté pourra-t-il accéder encore à `/dashboard` ?

2. Comment un attaquant pourrait-il voler votre session ? Quelles protections avons-nous mises en place ?

3. Pourquoi utilise-t-on `secrets.token_hex()` plutôt qu'un simple compteur (`session_1`, `session_2`, ...) ?

---

## Partie 4 : Pour aller plus loin (optionnel)

### 4.1 Afficher un message d'erreur au login

Actuellement, si le login échoue, on redirige simplement vers `/login` sans explication. Modifiez le code pour afficher "Identifiants incorrects".

**Indice** : Vous pouvez utiliser les flash messages de Flask.

### 4.2 Stocker les sessions en base de données

Le problème avec notre implémentation : si le serveur redémarre, toutes les sessions sont perdues puisqu'elles sont stockées en RAM, in memory!

Il nous faut **persister** nos sessions. Pour cela, imaginez une table `sessions`, modifiez le schéma de `create_db.py`  et modifiez `src/services/sessions.py` pour persister les sessions dans la BDD.

### 4.3 Ajouter un "Remember me"

Ajoutez une checkbox "Se souvenir de moi" au formulaire de login. Si cochée, la session dure 14 jours au lieu de 1 jour.
