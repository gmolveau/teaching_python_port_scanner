# Exercice 4 : Migrations de base de donnees

## Introduction

Dans les TP précédents, nous avons créé notre base de donnees SQLite avec le script `create_db.py`. Ce script crée la base et ses tables a partir de zero. Mais que se passe-t-il si on veut **modifier la structure** de notre base de donnees alors qu'elle contient deja des donnees ?

Par exemple, nous souhaitons désormais persister nos `sessions` en base. On ne peut pas simplement relancer `create_db.py` : cela écraserait toutes les données existantes.

C'est principalement le but des **migrations de base de données**.

---

## Partie 1 : Théorie

### Problématique

Quand on développe une application, le schéma de la base de données évolue au fil du temps: ajout/suppression de tables, de colonnes, on modifie des types, on ajoute des contraintes ...

Sans système de migration, on se retrouve face à plusieurs problèmes :

| Situation              | Probleme                                                                                                    |
| ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| Ajouter une colonne    | Il faut manuellement ecrire le `ALTER TABLE` et l'executer sur chaque environnement (dev, staging, prod...) |
| Travailler en equipe   | Comment savoir quelles modifications les autres developpeurs ont apportées à la base ?                      |
| Deployer en production | Comment s'assurer que la base de production est à jour, sans perdre de donnees ?                            |
| Revenir en arriere     | Comment annuler une modification si elle cause un bug ?                                                     |

### Qu'est-ce qu'une migration ?

Une migration est un **fichier qui decrit une modification du schéma de la base de donnees**. Chaque migration contient :

- Un **numéro de version** (ou un timestamp) pour les ordonner
- Une opération **"up"** : ce qu'il faut faire pour appliquer la modification
- Une opération **"down"** : ce qu'il faut faire pour annuler la modification

Voici un exemple :

```plaintext
migrations/
    001_create_users_table.sql
    002_add_email_to_users.sql
    003_create_sessions_table.sql
    004_add_created_at_to_users.sql
```

Chaque fichier représente un **pas** dans l'évolution du schéma. L'ensemble de ces fichiers constitue l'**historique complet** des modifications de la base.

Cela évite notamment les modifications sauvages en prod.

### Up et Down

Chaque migration définit donc deux opérations :

**Up (appliquer)** : le SQL à éxécuter pour appliquer la modification.

```sql
-- 002_add_email_to_users.sql (UP)
ALTER TABLE users ADD COLUMN email TEXT;
```

**Down (annuler)** : le SQL à éxécuter pour revenir à l'état précédent.

```sql
-- 002_add_email_to_users.sql (DOWN)
ALTER TABLE users DROP COLUMN email;
```

Cela permet de **monter** ou **descendre** dans les versions du schéma, comme un ascenseur :

```plaintext
Version 4  -  004_add_created_at_to_users   ▲ UP
Version 3  -  003_create_sessions_table     │
Version 2  -  002_add_email_to_users        │
Version 1  -  001_create_users_table        │
Version 0  -  (base vide)                   ▼ DOWN
```

### La table de suivi des migrations

Comment le système sait-il quelles migrations ont déjà été appliquées ?

=> Grâce à une **table dédiée** dans la base de donnees, souvent appelée `migrator_version` ou `migration_history`.

```plaintext
┌──────────────────────────────────────────────┐
│            migrator_version                 │
├──────────┬───────────────────────────────────┤
│ version  │ applied_at                        │
├──────────┼───────────────────────────────────┤
│ 001      │ 2026-01-15 10:00:00               │
│ 002      │ 2026-01-20 14:30:00               │
│ 003      │ 2026-02-05 09:15:00               │
└──────────┴───────────────────────────────────┘
```

Quand on lance les migrations :

1. Le systeme lit la table `migrator_version`
2. Il compare avec les fichiers de migration disponibles
3. Il éxécute uniquement les migrations **qui n'ont pas encore été appliquées**
4. Il enregistre chaque migration exécutée dans la table

### Le workflow en pratique

Voici le workflow classique d'une migration (avec ou sans outil) :

```plaintext
1. Je veux modifier la base de donnees
       │
       ▼
2. Création d'un nouveau fichier de migration
    (soit grâce à un outil, soit à la main)
    (ex: 004_add_comments_table.sql)
       │
       ▼
3. J'écris le SQL "up" et le SQL "down"
    ou l'outil génère lui-même cette partie
       │
       ▼
4. Je lance la commande de migration
    → Le systeme applique uniquement les nouvelles migrations
       │
       ▼
5. Je commite le fichier de migration dans Git
    → Mes collègues recupèrent la migration et l'appliquent chez eux
    → La migration peut être appliqué sur les divers environnements
```

### Pourquoi ne pas simplement modifier le script `create_db.py` ?

**Question** : Pourquoi ne pas juste mettre à jour `create_db.py` à chaque fois qu'il faut modifier le schéma ?

D'une part parce que `create_db.py` crée la base **à partir de rien**. Si la base existe déjà et contient des données (des utilisateurs s'enregistrent, des scans sont effectués...), on ne peut pas tout supprimer et reconstruire. On perdrait toutes les données.

Il serait possible de modifier le schéma pour prendre en compte tous les cas possibles, par exemple verifier que la table X n'existe pas avant de la créer, mais cela devient vite complexe de gérer tous les cas possibles, et on perd la possibilité de revenir en arrière dans tous les cas.

### Les outils de migration

Dans l'écosystème Python, il existe plusieurs outils de migration :

- `alembic`
- `django-migrations`
- `yoyo-migrations` (dernier commit en 2024)

Dans ce TP, nous allons implémenter **notre propre système de migration**, simple et minimal, pour bien comprendre les mécanismes sous-jacents.

En règle général, à part dans le cas où Django est utilisé, Alembic est l'outil le plus utilisé.

---

## Partie 2 : outil de migration custom

L'objectif est de coder votre propre outil de migration : `migrator.py`, à la racine de votre projet.

### Disclaimer

L'outil custom est volontairement simpliste. Un vrai outil de migration complet comme Alembic est bien plus complexe :

- Il doit gérer un grand nombre de **dialectes SQL**

Chaque moteur de base de données (SQLite, PostgreSQL, MySQL...) a ses propres spécificités SQL. Par exemple, `ALTER TABLE ... DROP COLUMN` n'est supporté par SQLite que depuis la version 3.35 (2021). Un outil comme Alembic gère ces différences via des abstractions, pour que le même code de migration fonctionne sur plusieurs moteurs.

Notre outil ne sait se connecter qu'à une base SQLite.

- La limite de la **numérotation séquentielle**

Notre système maison utilise des numéros (`001`, `002`...). Cela suffit quand on travaille seul, mais en équipe si deux développeurs créent chacun une migration qui fait suite à la `002`, les deux migrations auront le numéro `003`. Généralement les outils de migration utilisent des **timestamps** (ex: `20260212_143022_create_sessions.sql`) ou des **identifiants aléatoires** avec un graphe de dépendances, ce qui réduit fortement les risques de collision.

**Autres limites de notre outil** :

- Pas de gestion des **transactions** : si une migration échoue à moitié, la base peut se retrouver dans un état incohérent
- Pas de **verrouillage** : si deux personnes lancent les migrations en même temps sur la même base, le résultat est imprévisible
- Pas de **génération automatique** : des outils comme Alembic peuvent comparer l'état du code (les modèles SQLAlchemy par exemple) avec l'état de la base et générer automatiquement le SQL nécessaire

Malgré ces limites, notre outil devrait couvrir l'essentiel : appliquer des migrations dans l'ordre, suivre lesquelles ont été appliquées, et pouvoir revenir en arrière.

### Mode expert

Pour les lecteurs les plus aventuriers, ne lisez pas le reste de l'exercice et developpez vous-même votre propre outil de migration (cli) et le format des migrations qui vont avec.

Pour rappel, les migrations se trouvent dans un dossier `migrations`.
Une migration est en 2 parties, une partie pour appliquer la migration, et une pour revenir en arriere. A vous de choisir quel design vous preferez.

N'hésitez pas à créer un projet github public pour publier votre outil ;-) #recrutement

Good luck ! :)

### Mode guidé - structure attendue

Nous choisirons de stocker les migrations au format `sql` dans un dossier `migrations`.

Nous allons pour cet exercice, hard-coder le nom de la DB dans le migrator, mais idéalement il faudrait que notre migrator puisse être configuré.

```plaintext
migrator.py              # Outil de migration
migrations/              # Dossier contenant les migrations .sql
    001_create_users_table.sql
    002_create_sessions_table.sql
src/
```

### Format des fichiers de migration

Pour représenter une migration, nous choisissons le design suivant : chaque migration est un fichier `.sql` dont le nom commence par un numéro de version sur 3 chiffres, suivi d'un `_` et d'un nom descriptif. Exemple : `001_create_users_table.sql`.

Pour avoir les 2 parties requises d'une migration, le fichier aura deux marqueurs `-- UP` et `-- DOWN` pour séparer les deux opérations.

_Idée_ : auriez-vous imaginer un autre design ?

> On aurait pu par exemple séparer une migration en 2 fichiers : `001_create_users_table.up.sql` et `001_create_users_table.down.sql` :shrug:

Exemple de notre choix de design de migration :

```sql
-- UP
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- DOWN
DROP TABLE users;
```

L'outil devra parser ce format pour extraire le SQL de chaque section.

### Table de suivi

Le `migrator` doit créer et maintenir une table `migrator_version` dans la base de données pour suivre l'état des migrations :

```sql
CREATE TABLE migrator_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);
```

- `version` : le numéro de version extrait du nom de fichier (ex: `001`)
- `applied_at` : la date/heure d'application de la migration (format ISO)

Cette table doit être créée automatiquement par le migrator si elle n'existe pas.

Elle contiendra toujours uniquement 1 seule entrée, c'est à dire la dernière migration appliquée. Cela permet à l'outil de savoir où en est la base de données.

### Commandes attendues

Le migrator doit exposer **4 commandes**.

Un exemple est disponible dans `examples/argparse/commands.py`.

#### `python migrator.py status`

Affiche l'état de chaque migration (appliquée ou en attente) :

```plaintext
$ python migrator.py status
Version    Fichier                                        Statut
----------------------------------------------------------------------
001        001_create_users_table.sql                     appliquée
002        002_create_sessions_table.sql                  en attente
```

Comportement :

- Récupérer la dernière migration appliquée en base grâce à la table `migrator_version`
- Lire les fichiers `.sql` du dossier `migrations/` (triés par ordre lexicographique)
- En partant de la migration la plus récente, comparer avec l'état de la DB (exemple, migration actuelle = 002, migration la plus récente == 004, donc en attente)
- Afficher le statut de chaque migration

#### `python migrator.py up`

Applique toutes les migrations en attente, dans l'ordre.

```plaintext
$ python migrator.py up
Applying 001_create_users_table.sql...
  -> OK
Applying 002_create_sessions_table.sql...
  -> OK

2 migration(s) appliquée(s).
```

Comportement :

- Déterminer les migrations à appliquer à partir de la version stockée en base
- Si la table `migrator_version` n'existe pas, il faut la créer
- Pour chaque migration en attente (dans l'ordre) : exécuter le SQL de la section `-- UP`, puis enregistrer la version dans `migrator_version`
- Si aucune migration en attente : afficher un message

#### `python migrator.py down`

Annule la **dernière** migration appliquée.

```plaintext
$ python migrator.py down
Rollback 002_create_sessions_table.sql...
  -> OK
```

Comportement :

- Récupérer la version dans `migrator_version`
- Trouver le fichier `.sql` correspondant
- Exécuter le SQL de la section `-- DOWN`
- Changer la version dans `migrator_version`, si cetait la toute première migration, alors vider la table
- Si aucune migration appliquée : afficher un message approprié

#### `python migrator.py create <nom>`

Crée un nouveau fichier de migration vide avec le bon numéro de version.

```plaintext
$ python migrator.py create "add email to users"

Migration créée: migrations/003_add_email_to_users.sql
```

Comportement :

- Trouver le chemin du dossier `migrations` à partir de l'endroit où la commande a été lancée (eg. si la commande est lancée depuis `/home/user/dev/projetpython`, l'outil va donc chercher un dossier `/home/user/dev/projetpython/migrations`)
- Déterminer le prochain numéro de version (dernier + 1, ou 001 si aucun fichier)
- Créer le fichier avec le template `-- UP` / `-- DOWN`

### Aides

- pour le cli, utiliser `argparse` avec `add_subparsers` pour les sous-commandes
- `os.listdir()` pour lister les fichiers du dossier `migrations/`
- `conn.executescript()` pour exécuter du SQL multi-lignes
- `str.split()` pour découper le contenu du fichier selon les marqueurs

---

## Partie 3 : Mise en place du migrator

### Étape 1 : Coder le migrator

Codez `migrator.py` à la racine de votre projet en suivant les specs ci-dessus.

Testez chaque commande au fur et à mesure.

### Étape 2 : Première migration - la table users

Créez votre première migration pour la table `users` :

```bash
python migrator.py create "create users table"
```

Éditez le fichier `migrations/001_create_users_table.sql` et écrivez le SQL correspondant (inspirez-vous du `CREATE TABLE` dans votre `create_db.py` actuel).

### Étape 3 : Deuxième migration - la table sessions

Actuellement, les sessions sont stockées en mémoire (dans un dictionnaire Python). À chaque redémarrage du serveur, toutes les sessions sont perdues.

Créez une migration pour persister les sessions en base :

```bash
python migrator.py create create_sessions_table
```

Réfléchissez au schéma de la table `sessions`. Quelles colonnes sont nécessaires ? Regardez le code de `src/services/sessions.py` pour comprendre quelles données sont stockées pour chaque session.

### Étape 4 : Tester les migrations

1. **Supprimez** votre fichier `db.sqlite` existant
2. Lancez `python migrator.py status` pour voir les migrations en attente
3. Lancez `python migrator.py up` pour appliquer les migrations
4. Vérifiez avec `DB Browser for SQLite` que les tables `users`, `sessions` et `migrator_version` existent
5. Testez `python migrator.py down` puis `status` pour vérifier le rollback

### Étape 5 : Adapter le code de l'application

Modifiez `src/services/sessions.py` pour que les sessions soient stockées en base de données SQLite au lieu du dictionnaire en mémoire.

Les fonctions à adapter :

- `create_session()` : INSERT dans la table sessions
- `get_session()` : SELECT dans la table sessions (en vérifiant l'expiration)
- `delete_session()` : DELETE dans la table sessions
- `get_current_user()` : devrait fonctionner sans modification si `get_session` est correct

### Étape 6 : Valider

1. Lancez votre application
2. Enregistrez un utilisateur, connectez-vous
3. **Redémarrez le serveur** : vous devriez toujours être connecté (les sessions sont maintenant persistées)
4. Testez le logout

### Bonus

- Ajoutez une migration `003_add_created_at_to_users.sql` qui ajoute un champ `created_at` à la table `users`
- Supprimez le fichier `create_db.py` devenu inutile

---

## Correction

cf. le code :)
