# Exercice : Ajout d'une base de données

## Introduction

Dans cet exercice, nous allons ajouter une base de données en mémoire à notre application Flask pour permettre aux utilisateurs de créer un compte et de se connecter. Nous utiliserons un simple dictionnaire Python comme base de données en mémoire. Puis nous passerons à une vraie base de données.

## Étape 1 : Création de la db inmemory

La première étape consiste à créer un fichier qui contiendra notre base de données en mémoire. Nous allons créer un fichier `db.py` dans le répertoire `src`.

```python
# src/db.py
USERS = {}
```

Ce fichier contient un simple dictionnaire nommé `USERS` qui stockera les utilisateurs de notre application. La clé sera le nom d'utilisateur et la valeur sera le mot de passe haché.

---

## Exercice

Modifiez votre programme pour que l'authentification se fasse avec ce dictionnaire.

Cela signifie que dans l'endpoint de register, il faudra d'abord verifier que l'utilisateur n'existe pas déjà en base, puis il faudra hacher le mot de passe et le stocker dans la base.

Pour le login, il faudra verifier que le username existe, et si oui, comparer le mot de passe haché stocké en base avec celui fourni par l'utilisateur.

Ci-dessous la correction.

---

## Étape 2 : Modification du fichier `auth.py` pour gérer l'enregistrement

Maintenant, nous devons modifier le fichier `src/auth.py` pour gérer l'enregistrement des utilisateurs. Nous allons importer le dictionnaire `USERS` et l'utiliser pour stocker les nouveaux utilisateurs.

```python
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from src.db import USERS

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.get("/register")
def register_page():
    return render_template("register.html")


@auth_blueprint.post("/register")
def post_register():
    form = request.form.to_dict()
    username = form.get("username")
    password = form.get("password")

    if username in USERS:
        # L'utilisateur existe déjà
        return redirect(url_for("auth.register_page"))
        # on aurait pu utiliser aussi
        # return redirect("/register")
        # utiliser url_for permet de suivre les mises a jour eventuel du code et donc de la route

    secure_password = generate_password_hash(password)
    # on ajoute l'utilisateur en base
    USERS[username] = secure_password
    return redirect(url_for("auth.login_page"))
```

Dans cette étape, nous avons :

- Importé le dictionnaire `USERS` depuis `src/store.py`.
- Modifié la fonction `post_register` pour :
  - Récupérer le nom d'utilisateur et le mot de passe du formulaire.
  - Vérifier si l'utilisateur existe déjà dans le dictionnaire `USERS`.
  - Hacher le mot de passe en utilisant `generate_password_hash`.
  - Stocker le nom d'utilisateur et le mot de passe haché dans le dictionnaire `USERS`.
  - Rediriger l'utilisateur vers la page de connexion.

## Étape 3 : Modification du fichier `auth.py` pour gérer la connexion

Maintenant, nous devons modifier le fichier `src/auth.py` pour gérer la connexion des utilisateurs.

```python
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from src.db import USERS

auth_blueprint = Blueprint("auth", __name__)
# ... (code de l'enregistrement)

@auth_blueprint.get("/login")
def login_page():
    return render_template("login.html")


@auth_blueprint.post("/login")
def post_login():
    form = request.form.to_dict()
    username = form.get("username")
    password = form.get("password")

    if username not in USERS:
        # L'utilisateur n'existe pas
        return redirect(url_for("auth.login_page"))

    secure_password = USERS[username]
    if check_password_hash(secure_password, password):
        # Le mot de passe est correct
        return redirect(url_for("forms.home"))
    else:
        # Le mot de passe est incorrect
        return redirect(url_for("auth.login_page"))

```

Dans cette étape, nous avons :

- Modifié la fonction `post_login` pour :
  - Vérifier si l'utilisateur existe dans le dictionnaire `USERS`.
  - Récupérer le mot de passe haché depuis le dictionnaire `USERS`.
  - Vérifier si le mot de passe fourni correspond au mot de passe haché en utilisant `check_password_hash`.
  - Rediriger l'utilisateur vers la page d'accueil en cas de succès, sinon vers la page de connexion.

## Étape 4 : Lancement de l'application et test de la fonctionnalité

Maintenant que nous avons apporté toutes les modifications nécessaires, nous pouvons lancer l'application et tester la fonctionnalité.

1. Lancez l'application Flask (activer le venv, puis `flask --app src run --debug`)
2. Se rendre sur `http://127.0.0.1:5000/register`.
3. Créez un nouveau compte avec un nom d'utilisateur et un mot de passe.
4. Vous serez redirigé vers la page de connexion.
5. Connectez-vous avec le compte que vous venez de créer.
6. Vous devriez être redirigé vers la page d'accueil.

Congrats ! Vous avez ajouté une base de données in-memory.