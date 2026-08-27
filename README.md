# TaxiGo API

TaxiGo est une API REST de gestion de courses de taxi développée avec Django et Django REST Framework.

Le projet permet de gérer des passagers, des chauffeurs, leurs véhicules, les demandes de course, le calcul de distance et de prix ainsi que la recherche des chauffeurs disponibles les plus proches.

---

## Technologies

- Python
- Django
- Django REST Framework
- SimpleJWT
- JWT stockés dans des cookies HTTPOnly
- SQLite pour le développement
- API REST

---

## Fonctionnalités

### Authentification

- Inscription
- Vérification de l'adresse e-mail
- Connexion
- JWT Access Token
- JWT Refresh Token
- Stockage des tokens dans des cookies HTTPOnly
- Protection CSRF
- Rafraîchissement du token
- Déconnexion
- Consultation du profil utilisateur avec `/me/`

### Utilisateurs

Trois rôles sont utilisés :

- `CLIENT` : passager
- `DRIVER` : chauffeur
- `ADMIN` : administrateur

---

## Chauffeurs

Un utilisateur ayant le rôle `DRIVER` peut :

- créer son profil chauffeur ;
- renseigner son numéro de permis ;
- mettre à jour sa position GPS ;
- gérer sa disponibilité ;
- consulter les courses disponibles ;
- accepter une course ;
- démarrer une course ;
- terminer une course.

Statuts d'un chauffeur :

- `AVAILABLE`
- `ON_A_RIDE`
- `UNAVAILABLE`

`ON_A_RIDE` est géré automatiquement par le backend.

---

## Véhicules

Un chauffeur peut gérer ses propres véhicules.

Informations principales :

- marque ;
- modèle ;
- immatriculation ;
- nombre de places ;
- type de véhicule.

Les permissions empêchent un chauffeur de gérer les véhicules appartenant à un autre chauffeur.

---

## Courses

Cycle principal d'une course :

```text
WAITING
   ↓
ACCEPTED
   ↓
IN_PROGRESS
   ↓
COMPLETED

Une course peut également devenir :

CANCELLED

Règles métier principales :

un passager ne peut avoir qu'une seule course active ;
un chauffeur ne peut avoir qu'une seule course active ;
seul un chauffeur disponible peut accepter une course ;
une course déjà acceptée ne peut pas être acceptée par un autre chauffeur ;
ACCEPTED → COMPLETED directement est interdit ;
une course en cours ne peut plus être annulée par le passager ;
lorsqu'une course se termine ou est annulée après acceptation, le chauffeur redevient disponible.

Ces règles sont protégées à la fois au niveau de l'API et, pour l'unicité des courses actives, par des contraintes en base de données.

Calcul de distance

TaxiGo utilise la formule de Haversine pour calculer la distance entre deux coordonnées GPS.

Le calcul est effectué côté serveur dans :

apps/taxis/utils.py

La distance est exprimée en kilomètres.

Calcul du prix

Le prix estimé d'une course est calculé côté serveur selon la formule :

prix = prix_de_prise_en_charge + distance_km × prix_par_km

Une grille tarifaire active est utilisée pour effectuer le calcul.

Le client ne peut pas imposer lui-même la distance ou le prix de la course.

Chauffeurs proches

Un passager peut rechercher les chauffeurs disponibles autour de sa position.

Exemple :

GET /api/v1/drivers/nearby/?lat=12.371427&lon=-1.519660

Options :

?limit=5

pour limiter le nombre de résultats.

?radius=10

pour ne retourner que les chauffeurs situés dans un rayon de 10 km.

Le backend :

sélectionne uniquement les chauffeurs AVAILABLE ;
ignore les chauffeurs sans coordonnées GPS ;
calcule leur distance avec Haversine ;
applique éventuellement le rayon ;
trie les chauffeurs du plus proche au plus éloigné ;
applique la limite demandée.
Principaux endpoints
Authentification
GET   /api/v1/auth/csrf/
POST  /api/v1/auth/register/
POST  /api/v1/auth/login/
POST  /api/v1/auth/refresh/
POST  /api/v1/auth/logout/
GET   /api/v1/auth/me/
Chauffeur
POST  /api/v1/drivers/me/
GET   /api/v1/drivers/me/
PATCH /api/v1/drivers/me/position/
PATCH /api/v1/drivers/me/status/
GET   /api/v1/drivers/nearby/
Véhicules
GET    /api/v1/vehicles/
POST   /api/v1/vehicles/
GET    /api/v1/vehicles/{id}/
PATCH  /api/v1/vehicles/{id}/
DELETE /api/v1/vehicles/{id}/
Courses
GET   /api/v1/rides/
POST  /api/v1/rides/
GET   /api/v1/rides/{id}/

GET   /api/v1/rides/available/

PATCH /api/v1/rides/{id}/accept/
PATCH /api/v1/rides/{id}/status/
PATCH /api/v1/rides/{id}/cancel/
Installation
1. Cloner le projet
git clone <URL_DU_DEPOT>
cd TaxiGo
2. Créer l'environnement virtuel

Sous Windows :

python -m venv venv
venv\Scripts\activate
3. Installer les dépendances
pip install -r requirements.txt
4. Configurer la clé secrète

Le projet attend la variable d'environnement :

DJANGO_SECRET_KEY

Sous Windows CMD :

set "DJANGO_SECRET_KEY=your-secret-key"

Pour générer une clé :

python -c "import secrets; print(secrets.token_urlsafe(50))"

Le fichier .env.example indique également les variables nécessaires.

5. Appliquer les migrations
python manage.py migrate
6. Démarrer le serveur
python manage.py runserver

L'API sera accessible à :

http://127.0.0.1:8000/api/v1/
Tests

Pour lancer l'ensemble des tests :

python manage.py test

État actuel de la suite :

53 tests
53 réussis
0 échec
0 erreur

Les tests couvrent notamment :

authentification JWT et cookies ;
Haversine ;
calcul du prix ;
véhicules ;
création des courses ;
contraintes d'unicité ;
acceptation ;
annulation ;
transitions de statut ;
historique et permissions ;
recherche des chauffeurs proches.
Structure simplifiée
TaxiGo/
│
├── apps/
│   ├── account/
│   │   └── tests/
│   │
│   ├── taxis/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   ├── views.py
│   │   ├── utils.py
│   │   └── tests/
│   │
│   └── commandes/
│       ├── models.py
│       ├── serializers.py
│       ├── permissions.py
│       ├── views.py
│       └── tests/
│
├── backend/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
Sécurité
Les JWT sont stockés dans des cookies HTTPOnly.
Les opérations sensibles utilisant les cookies sont protégées contre le CSRF.
Les mots de passe sont gérés par Django.
La clé secrète Django n'est pas stockée dans le dépôt.
Les utilisateurs ne peuvent accéder qu'aux ressources qui les concernent.
Les calculs de distance et de prix sont réalisés côté serveur.
Limites actuelles

TaxiGo est une API backend pédagogique.

Le projet ne comprend pas :

de frontend ;
de paiement en ligne ;
de suivi GPS temps réel par WebSocket ;
d'intégration avec une API cartographique externe ;
de système de notification push.

La recherche de proximité utilise les positions GPS stockées en base et la formule de Haversine.


Une petite précision : avant de garder la phrase **« 53 tests »** dans le README final, on refera encore une fois la suite après tous les derniers nettoyages. Si le nombre change, on mettra le vrai chiffre.

Après avoir créé `README.md` :

```bash
git add README.md
git status