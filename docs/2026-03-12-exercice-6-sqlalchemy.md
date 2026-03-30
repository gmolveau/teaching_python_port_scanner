# TP 6 : Sqlalchemy

Dans ce TP nous allons mettre en place `sqlalchemy`.

## Histoire

SQLAlchemy est une bibliothèque Python open source créée par **Michael Bayer** (alias *zzzeek* : <https://github.com/zzzeek>) et publiée pour la première fois en **2006**. Elle s'est rapidement imposée comme la référence en matière d'ORM (Object-Relational Mapper) dans l'écosystème Python, grâce à sa flexibilité et à son double niveau d'abstraction : un ORM haut niveau et un Core SQL bas niveau.

La **version 2.0**, sortie en janvier **2023**, a introduit une refonte majeure de l'API : le style d'écriture des requêtes est désormais unifié autour de `select()`, les sessions sont plus explicites, et le support natif de `asyncio` a été considérablement amélioré. C'est cette version moderne que nous utiliserons dans ce TP.

## ORM

Un **ORM** (Object-Relational Mapper) est une technique de programmation qui permet de faire le lien entre le monde **orienté objet** (notre code Python) et le monde **relationnel** (notre base de données SQL).

Sans ORM, comme actuellement, on écrit du SQL brut dans le code et on map manuellement les résultats vers des structures Python.

Exemple dans notre fonction `get_user_by_username`, on ecrit le `select` en SQL pur et on va manuellement mettre les resultats dans un dictionnaire.

```python
def get_user_by_username(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            return None
        return {"id": result[0], "password": result[1]}
```

Avec un ORM, ces étapes ne seraient plus necessaires.

**Avantages :**

- **Abstraction du SQL** : vous écrivez du Python, pas du SQL. Le code est plus lisible et plus proche du métier.
- **Typage et autocomplétion** : les champs sont typés, les erreurs de type sont détectables statiquement (avec `mypy`/`ty`) plutôt qu'à l'exécution.
- **Portabilité** : changer de base de données (SQLite → PostgreSQL) ne nécessite généralement pas de réécrire vos requêtes.
- **Cohérence avec le schéma** : le modèle Python est la source de vérité. Si le schéma change, les erreurs apparaissent dès la compilation/typage.
- **Gestion des relations** : naviguer entre objets liés (`user.addresses`) est naturel, sans JOIN explicite.

L'idée globale à retenir est donc que nous cherchons à décrire le schéma de DB (les champs, mais aussi les relations) que l'on souhaite, avec des objets python.

### Exemple simple

Dans un terminal, rendez vous dans `examples/sqlalchemy_simple`.

Lancer `uv run create_db.py`.

Un fichier `simple.db` a été généré.

Regardons le code de `models.py` pour comprendre comment fonctionne SQLAlchemy.

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass
```

On retrouve au début des imports que l'on expliquera par la suite.

On définit ensuite une première classe, `Base` qui hérite de `DeclarativeBase`, importée depuis SQLAlchemy. Cette étape permet de créer une classe de `base` (littéralement) qui servira à convertir nos autres classes python en classes sqlalchemy.

```python
...
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"
...
```

Ici on retrouve la déclaration de notre premier modèle.

Il s'agit de la classe `User`, qui hérite de `Base` pour en faire un modèle que SQLAlchemy peut utiliser.

On remarque un premier attribut de notre classe `__tablename__`.

Comme son nom l'indique il s'agit du nom de la table dans notre base.

L'attribut suivant, `id` est déclaré comme un type `Mapped[int]`, pour simplifier on pourra le considérer comme `int`. Et sa valeur est `mapped_column(primary_key=True)` qui signifie : ce champ `id` correspond donc au champ `id` du même nom dans notre table `users`. ce champ en base est une clé primaire de type `INTEGER`.

Le dernier attribut `name` n'a que son type de déclaré `Mapped[str]`. Cela est suffisant pour SQLAlchemy pour comprendre que cela correspond au champ `name` de la table, qui aura pour type l'équivalent du `str` de python, à savoir `VARCHAR`. Par défaut sqlalchemy ajoute la contrainte  `not null` à ce champ.

Visuellement le mapping ressemble à :

```console
Python (classe User)               Base de données (table "users")
─────────────────────────────  |   ─────────────────────────────────
class User(Base):              |
    __tablename__ = "users"    ──►  TABLE users
                               │   ┌──────────┬─────────┬─────────────┐
    id: Mapped[int]        ────┼──►│ id       │ INTEGER │ PRIMARY KEY │
       mapped_column(          │   ├──────────┼─────────┼─────────────┤
         primary_key=True)     │   │          │         │             │
    name: Mapped[str]      ────┼──►│ name     │ VARCHAR │ NOT NULL    │
                               │   └──────────┴─────────┴─────────────┘
                               │
```

Regardons le code de `create_db.py`

```python
from models import Base
from sqlalchemy import create_engine

engine = create_engine("sqlite:///simple.db")
Base.metadata.create_all(engine)
```

2 lignes nous interessent.

`engine = create_engine("sqlite:///simple.db")`

Ici on déclare un `engine`, c'est notre connection à notre base de données. Ici on lui passe comme argument la string `"sqlite:///simple.db"` pour lui indiquer que l'on souhaite se connecter à une base sqlite nommée `simple.db` située dans le current working directory.

Ensuite : `Base.metadata.create_all(engine)`

En important notre classe de base `Base` on peut lancer une action de création de toutes les tables qui en héritent.

**Cependant** on va préférer utiliser les migrations alembic pour générer notre base de données plutot qu'utiliser cette façon de faire.

Un exemple suivra.

Enfin étudions `data.py` :

```python
from models import User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///simple.db")

with Session(engine) as session:
    # Insert
    session.add_all([User(name="Alice"), User(name="Bob")])
    session.commit()

    # Query all
    users = session.scalars(select(User)).all()
    for user in users:
        print(user.id)

    # Query one by name
    alice = session.scalar(select(User).where(User.name == "Alice"))
    print(alice)
```

Ce fichier sert à montrer comment insérer et récupérer de la donnée.

On remarque qu'il nous faut une `Session` pour cela. Session qui nécessite un `engine`.

### Alembic

Remplacons ce fichier `create_db.py` par des migrations alembic.

Dans le dossier `examples/sqlalchemy_simple_alembic` alembic a ete configuré mais aucune migration n'existe encore.

Si on regarde le fichier `migrations/env.py` ligne 16 on peut lire :

```python
# add your model's MetaData object here
# for 'autogenerate' support
from models import Base

target_metadata = Base.metadata
```

Grâce à cet import, alembic est désormais en capacité de générer des migrations automatiquement en détectant les changements de vos modèles !

Essayez de lancer `uv run alembic revision --autogenerate -m "add users"`

Alembic va créer automatiquement une nouvelle mirgations dans `migrations/versions`.

On peut maintenant lancer la création de notre DB avec alembic !

`uv run alembic upgrade head`

Maintenant, éditez le model `User` en lui rajoutant ce champ :

`password_hash: Mapped[str]`

Puis lancez : `uv run alembic revision --autogenerate -m "add password field to users"` et étudiez la nouvelle migration

```python
def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###
```

Alembic a bien détecté ce nouveau champ !

### Exemple complet

Rendez vous dans `examples/sqlalchemy_blog` pour un exemple simple mais concret, d'un mini moteur de blog.

Pour cet exemple, on imagine que l'on a un blog. Un utilisateur possède un identifiant `id` et un `username`.

Un utilisateur peut écrire 0 ou plusieurs articles. Un article ne peut être écrit que par 1 seul utilisateur. C'est une relation 1-N.

Un utilisateur peut `liker` 0 ou plusieurs articles. Un article peut être liké par 0 ou plusieurs utilisateurs différents. C'est une relation N-N (many-to-many).

Nous avons donc 3 tables :

- Une table pour les utilisateurs => `users`
- Une table pour les articles => `blogposts`
- Une table de jointure (entre les utilisateurs et les articles) pour les likes => `likes`

Lorsque l'on crée des modèles, il est très important de bien réfléchir aux termes de que l'on va utiliser.

Questions (à répondre en anglais, evidemment) :

- Quel serait un nom de variable pour décrire, du point de vue d'un utilisateur, les articles qu'il a rédigé ? => `posts` ou `blogposts`
- Quel serait un nom de variable pour décrire, du point de vue de l'article de blog, l'utilisateur qui l'a écrit ? => `author`
- Quel serait un nom de variable pour décrire, du point de vue d'un utilisateur, les articles qu'il a mis en favoris ? => `liked_blogposts`
  - et inversement, du point de vue d'un article ? => `liked_by`

Comme nous venons de voir les champs de base, voyons les attributs correspondant à des relations.

```python
...
# relationships
posts: Mapped[list["BlogPost"]] = relationship(back_populates="author")
likes: Mapped[list["Like"]] = relationship(back_populates="user")
liked_posts: Mapped[list["BlogPost"]] = relationship(
    secondary="likes", back_populates="liked_by"
)
```

D'abord `posts`, une variable de type `liste de BlogPost`. Ici on remarque que la valeur est une `relationship` avec un argument particulier : `back_populates`. Cet argument permet de faire le lien avec la classe `BlogPost`, et plus particulièrement avec le champ `author` de cette classe.

Grâce à cette ligne, nous pouvons désormais obtenir, à partir d'un utilisateur, ses articles avec l'opérateur `.` => `user1.posts` ; sans avoir à écrire de SQL: la jointure est gérée pour nous et le mapping également !

Grâce à ces explications, décrivez la prochaine ligne :

`likes: Mapped[list["Like"]] = relationship(back_populates="user")`

Enfin le dernier attribut :

```python
...
liked_posts: Mapped[list["BlogPost"]] = relationship(
    secondary="likes", back_populates="liked_by"
)
```

Ici cette ligne nous permet d'aller récupérer une liste d'objets qui se trouvent derrière une relation many-to-many.

Pour rappel, nous avons la table `users` et la table `blogposts` qui sont reliées entre elles par une table de jointure `likes`.

Il est donc théoriquement possible de récupérer, pour un utilisateur, ses `likes` (c'est à dire la liste des blogposts que l'utilisateur a liké).

Et inversement il est possible de récupérer, pour un blogpost, les utilisateurs ayant liké.

Pour faire cela, l'argument `secondary` est utilisé dans `relationship` pour pointer vers le nom de la table de jointure.

Je vous invite fortement à lire la documentation complète ici : <https://docs.sqlalchemy.org/en/21/orm/basic_relationships.html>.

-------

## Mise en place

### Infos de connexion - env vars

Pour fonctionner, SQLAlchemy va avoir besoin des informations de connexion à la base de données.

Ces informations sont généralement stockées dans les variables d'environnement, pour éviter la recopie.

Créons le fichier `.env.example` qui contiendra la liste des variables d'environnement à renseigner.

Ce fichier sera commité avec le projet.

Comme nous utilisons sqlite, pour l'instant notre fichier `.env.example` contiendra uniquement le chemin vers la base.

Ajoutons donc `DATABASE_URL=sqlite:///db.sqlite` dans ce fichier.

Et créons le fichier `.env` avec la même donnée.

On veillera à ignorer le fichier `.env` dans notre `.gitignore`.

### Alembic

Déplacons le dossier alembic dans `src`

Il faudra éditer `alembic.ini` > `script_location = %(here)s/src/alembic`

Pour que `alembic` puisse récupérer les variables d'environnement, il faudra modifier le script `src/alembic/env.py`.

```python
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from src.models import Base  # noqa: E402

target_metadata = Base.metadata
```

Ici on rajoute la librairie `dotenv` afin d'auto importer les variables d'environnement.

Nous n'avons pas encore installé cette librairie, rajoutons là à nos dépendances.

```bash
uv add python-dotenv
```

Puis on utilise la variable `DATABASE_URL` pour configurer alembic afin qu'il trouve la base de données.

Et enfin on importe notre `Base` model depuis notre fichier `models.py`

Ce fichier `models.py` n'existe pas encore nous allons le créer.

### Connexion à la BD

Il faut éditer notre fichier `src/db.py` pour remplacer notre connexion à la base SQLite pour utiliser SQLAlchemy.

```python
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


def get_session() -> Session:
    return Session(engine)

```

Maintenant que nous avons la nouvelle connexion à notre base de données via SQLAlchemy, il nous faut créer nos models SQLAlchemy ;)

### Models

Pour débuter nous allons faire le choix de mettre tous les models dans un unique fichier.

Il est possible si notre application évolue, de répartir les models dans plusieurs fichiers, en faisant attention aux imports circulaires.

Créons donc le fichier `src/models.py`.

Nous allons avoir 4 classes au total :

- `Base`
- `User` : `id` (int, clé primaire), `username` (text, non-null, unique), `password_hash` (text, non-null)
- `Session` : `id` (int, clé primaire), `expires_at` (date, non-null), `external_id` (uuidv7, non-null, calculé automatiquement lors de la création)
- `Scan` : `id` (int, clé primaire), `ip_target` (str, non-null), `port_target` (int, non-null), `result` (text)

Le champ `external_id` est requis ici car l'identifiant etant un entier autoincrémenté, il nous faut un autre identifiant plus sécurisé. On pourrait très bien modifier le type de l'identifiant de cette table pour utiliser un UUID et ne pu avoir besoin de ce champ `external_id` supplémentaire.

Il y aura deux relations one-to-many :

- `[User] N - 1 [Session]`
- `[User] N - 1 [Scan]`

#### Exercice models

Avant de lire la correction (cf `src/models.py`), essayez de coder les models !

#### Services

Maintenant que nos models sont prêts, nous allons pouvoir les utiliser dans nos `services`.

Par exemple nous remplacerons :

```python
def user_exists(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result is not None
```

par son équivalent qui utilise la session de SQLAlchemy et le model `User` :

```python
def user_exists(username: str) -> bool:
    with get_session() as db:
        stmt = select(User).where(User.username == username)
        user = db.scalar(stmt)
        return user is not None
```

Expliquons ce changement ligne par ligne :

```python
# 0. création de la session (connexion à la DB)
with get_session() as db:
    # 1. d'abord la requete (aussi appelé statement, stmt en version courte)
    # plutot explicite, on imagine facilement sa traduction en SQL
    # SELECT * FROM users as u WHERE u.username = "<username>";
    stmt = select(User).where(User.username == username)
    # 2. on execute cette requete avec db.scalar(...) qui signifie
    # je ne veux qu'un seul résultat
    # si on voulait plusieurs résultats, il faut utiliser db.scalars(...)
    # 3. et le résultat de cette requête est stocké dans une variable
    user = db.scalar(stmt)
    # 4. le but de notre fonction est d'indiquer si un utilisateur existe pour un username donné, on fait le choix que notre fonction renvoie un bool (True/False)
    # db.scalar(...) renvoie None si la requete n'a retourné aucun resultat
    # on se sert donc de ce None pour verifier si un utilisateur existe
    # (user is not None) renvoie bien un bool
    return user is not None
```

**Exercice** terminer de modifier tous les services.

#### flask-sqlalchemy

[`flask-sqlalchemy`](https://flask-sqlalchemy.palletsprojects.com/) est une extension Flask qui intègre SQLAlchemy dans le cycle de vie de Flask.

Dans notre projet actuel, chaque fonction de `service` ouvre et ferme sa propre session SQLAlchemy :

```python
# src/services/users.py
def user_exists(username: str) -> bool:
    with get_session() as db:
        result = db.scalar(select(User).where(User.username == username))
        return result is not None
```

Cela signifie que pour traiter une seule requête HTTP, plusieurs sessions sont ouvertes successivement — une par appel de service. Ce n'est pas idéal : une session représente une transaction, et fragmenter les opérations d'une même requête en plusieurs sessions peut causer des incohérences (une donnée insérée dans une session n'est pas encore visible dans une autre avant le `commit`).

L'idéal serait d'avoir **une seule session par requête HTTP**, ouverte en début de requête et fermée (avec commit ou rollback) à la fin.

C'est exactement ce que fait `flask-sqlalchemy` : elle lie la session SQLAlchemy au **contexte de requête Flask** (`g`), de sorte qu'une même session est réutilisée tout au long du traitement de la requête, puis automatiquement nettoyée.

Avec `flask-sqlalchemy`, on initialise une instance `db` globale :

```python
# src/db.py avec flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

On la rattache à l'application Flask au démarrage :

```python
# app.py
from flask import Flask
from src.db import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db.init_app(app)
```

Les modèles héritent de `db.Model` au lieu de notre `Base` :

```python
class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ...
```

Et dans les services, on utilise directement `db.session` sans ouvrir/fermer de contexte manuellement :

```python
def user_exists(username: str) -> bool:
    return db.session.scalar(select(User).where(User.username == username)) is not None
```

La session est automatiquement fermée par Flask à la fin de chaque requête.

On a fait le choix de ne pas utiliser `flask-sqlalchemy` pour deux raisons :

1. **Découplage** : nos services (`src/services/`) ne dépendent pas de Flask. Ils pourraient être réutilisés dans un script CLI ou un worker sans modifier leur code. Avec `flask-sqlalchemy`, `db.session` est lié au contexte Flask, donc inutilisable en dehors d'une requête.

2. **Clarté pédagogique** : utiliser `get_session()` explicitement rend visible la gestion du cycle de vie de la session, ce qui est plus formateur.

L'approche `flask-sqlalchemy` est très courante dans les projets Flask de taille modeste — elle simplifie le code au prix d'un couplage plus fort avec Flask.
