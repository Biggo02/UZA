# UZA — Marketplace Django

UZA est une marketplace RDC de vente et revente d’électronique et d’électroménager, avec UZA comme tiers de confiance. Le vendeur et l’acheteur ne reçoivent jamais les coordonnées personnelles de l’autre. La transaction finale est organisée physiquement dans les locaux UZA.

## Stack
- Python / Django 4.2.7
- PostgreSQL (production et Codespaces) / SQLite (fallback local)
- Pillow pour les images
- Templates Django + CSS responsive

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

## Workflow métier
1. Inscription avec un compte unique acheteur/vendeur.
2. Certification : document recto, verso et selfie par upload, jamais par URL.
3. Un compte non certifié ne peut pas publier ni demander un achat.
4. Une annonce créée est `PENDING` et reste invisible.
5. UZA la contrôle, définit sa marge et la publie.
6. Une demande concerne exactement une annonce.
7. Le propriétaire accepte/refuse.
8. UZA approuve/refuse.
9. Les deux validations créent une transaction planifiée.
10. Le rendez-vous se déroule chez UZA.
11. UZA confirme paiement + remise et clôture la transaction.
12. L’historique et les notifications sont mis à jour.

## Administration
`/admin/` permet de gérer utilisateurs, KYC, catégories, annonces, demandes, transactions, notifications, messages et journal d’audit.
