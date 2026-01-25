# Démonstration CSRF (Cross-Site Request Forgery)

## Qu'est-ce que le CSRF?

Le CSRF est une attaque qui force un utilisateur authentifié à exécuter des actions non désirées sur une application web. L'attaquant exploite la confiance qu'un site a envers le navigateur de l'utilisateur.

> Dans une attaque de falsification de requête inter-sites (cross-site request forgery, CSRF en anglais), un attaquant trompe le navigateur pour qu'il effectue une requête HTTP vers le site cible à partir d'un site malveillant. La requête inclut les identifiants de l'utilisateur et amène le serveur à exécuter une action nuisible, pensant que l'utilisateur l'a voulue.
>
> Une attaque CSRF est possible si un site web :
>
> - utilise des requêtes HTTP pour modifier un état côté serveur ;
> - utilise uniquement des cookies pour valider que la requête provient d'un utilisateur authentifié ;
> - utilise uniquement des paramètres dans la requête qu'un attaquant peut prédire.
>
> -- <https://developer.mozilla.org/fr/docs/Glossary/CSRF>

<https://learn.snyk.io/lesson/csrf-attack/?ecosystem=javascript>

## Comment ça marche?

1. L'utilisateur se connecte à sa banque (localhost:5000)
2. Le navigateur stocke le cookie de session
3. L'utilisateur visite un site malveillant (localhost:5001)
4. Le site malveillant soumet un formulaire caché vers la banque
5. Le navigateur envoie automatiquement les cookies avec la requete.

## Lancer la démonstration

### Étape 1: Lancer le serveur vulnérable

```bash
uv run vulnerable_server.py
```

### Étape 2: Se "connecter" à la banque

Ouvrir http://localhost:5000 dans le navigateur.
→ Vous voyez un solde de 1000€

### Étape 3: Lancer le serveur attaquant (dans un autre terminal)

```bash
uv run attacker_server.py
```

### Étape 4: Visiter le "site malveillant"

Ouvrir <http://localhost:5001> dans un nouvel onglet.

### Étape 5: Constater l'attaque

Retourner sur <http://localhost:5000>

## Pourquoi ça fonctionne?

- Le serveur fait confiance à toute requête POST avec un cookie valide
- Il n'y a pas de vérification que la requête provient du site légitime
- Le navigateur envoie automatiquement les cookies pour le domaine concerné

## Comment se protéger?

1. **Token CSRF**: Inclure un token unique et secret dans chaque formulaire
2. **SameSite Cookie**: Utiliser `SameSite=Strict` ou `SameSite=Lax`
3. **Vérifier le header Origin/Referer**
4. **Demander une re-authentification** pour les actions sensibles

## Fichiers

- `vulnerable_server.py` - Serveur bancaire vulnérable (port 5000)
- `attacker_server.py` - Serveur malveillant qui exploite la vulnérabilité (port 5001)
