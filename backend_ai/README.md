# Backend IA - Analyse de Documents Administratifs

Système d'analyse automatique de dossiers administratifs utilisant l'IA pour l'extraction de texte (OCR), l'analyse de mise en page et la vérification de conformité.

## Fonctionnalités

- **OCR avancé** : Extraction de texte à partir d'images et PDFs avec PaddleOCR
- **Analyse de mise en page** : Classification de documents avec LayoutLMv3
- **Vérification sémantique** : Analyse de cohérence et conformité avec Llama 3
- **API REST** : Interface complète pour gérer dossiers, documents et rapports
- **Traitement multi-documents** : Support PDF multi-pages et images

## Prérequis

- Python 3.10 ou supérieur
- PostgreSQL (ou SQLite pour environnement de développement)
- Compte OpenRouter (pour l'accès à Llama 3)

## Installation

### 1. Cloner le projet et créer l'environnement virtuel

```bash
cd backend_ai
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```bash
cp .env.example .env
```

Éditer `.env` avec vos configurations :

```env
SECRET_KEY=votre-clé-secrète-django
DEBUG=True
OPENROUTER_API_KEY=sk-or-v1-votre-clé-openrouter
```

### 4. Effectuer les migrations

```bash
python manage.py migrate
```

### 5. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur de développement

```bash
python manage.py runserver
```

L'API sera accessible sur `http://localhost:8000/api/`

## Documentation de l'API

### Endpoints - Dossiers

- `GET /api/dossiers/` - Liste tous les dossiers
- `POST /api/dossiers/` - Créer un nouveau dossier
- `GET /api/dossiers/{id}/` - Détails d'un dossier
- `POST /api/dossiers/{id}/analyze/` - Lancer l'analyse d'un dossier

### Endpoints - Documents

- `GET /api/documents/` - Liste tous les documents
- `POST /api/documents/` - Uploader un document
- `GET /api/documents/{id}/` - Détails d'un document

### Endpoints - Rapports

- `GET /api/reports/` - Liste tous les rapports
- `GET /api/reports/{id}/` - Détails d'un rapport

## Architecture du projet

```
backend_ai/
├── ai_engine/          # Moteur d'IA
│   ├── ocr/           # Module OCR (PaddleOCR)
│   ├── layout/        # Analyse de layout (LayoutLM)
│   ├── analysis/      # Analyse sémantique (Llama)
│   ├── pipeline.py    # Pipeline d'orchestration
│   └── utils.py       # Utilitaires
├── back/              # Application Django principale
│   ├── models.py      # Modèles de données
│   ├── views.py       # API Views
│   ├── serializers.py # Serializers DRF
│   └── services.py    # Logique métier
└── backend_ai/        # Configuration Django
    └── settings.py
```

## Workflow de traitement

1. **Upload** : L'utilisateur upload des documents dans un dossier
2. **Déclenchement** : Appel à `/api/dossiers/{id}/analyze/`
3. **OCR** : Extraction du texte avec PaddleOCR
4. **Layout** : Classification et structuration avec LayoutLM
5. **Analyse** : Vérification de cohérence avec Llama 3
6. **Rapport** : Génération d'un rapport de conformité

## Tests

```bash
# Exécuter tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test back
python manage.py test ai_engine
```

## Débogage

Activer les logs détaillés dans `settings.py` :

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'ai_engine': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Dépendances principales

- **Django 6.0** : Framework web - [Documentation](https://docs.djangoproject.com/)
- **Django REST Framework** : API REST - [Documentation](https://www.django-rest-framework.org/)
- **PaddleOCR** : Reconnaissance optique de caractères - [GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- **Transformers (Hugging Face)** : LayoutLMv3 - [Documentation](https://huggingface.co/docs/transformers/)
- **OpenAI** : Client pour OpenRouter/Llama 3 - [Documentation](https://platform.openai.com/docs/)
- **Pillow** : Traitement d'images - [Documentation](https://pillow.readthedocs.io/)
- **PyMuPDF (fitz)** : Conversion PDF - [Documentation](https://pymupdf.readthedocs.io/)

## Déploiement en production

### Checklist de déploiement

- [ ] Définir `DEBUG=False`
- [ ] Configurer `ALLOWED_HOSTS`
- [ ] Utiliser une base de données PostgreSQL
- [ ] Configurer un serveur de fichiers (S3, etc.)
- [ ] Implémenter Celery pour les tâches asynchrones
- [ ] Configurer HTTPS
- [ ] Mettre en place un monitoring (Sentry)
- [ ] Configurer les CORS pour le frontend

### Recommandations

- Utiliser un serveur WSGI comme Gunicorn ou uWSGI
- Configurer un reverse proxy (Nginx ou Apache)
- Mettre en place un système de cache (Redis)
- Implémenter une stratégie de sauvegarde de la base de données

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

### Standards de code

- Suivre PEP 8 pour le style Python
- Documenter les fonctions et classes avec docstrings
- Ajouter des tests unitaires pour toute nouvelle fonctionnalité
- Vérifier le code avec pylint avant de soumettre

## Roadmap

- [ ] Implémenter Celery pour les tâches d'arrière-plan
- [ ] Fine-tuner LayoutLM pour les documents spécifiques
- [ ] Ajouter plus de tests unitaires
- [ ] Ajouter authentification JWT
- [ ] Créer un dashboard d'administration
- [ ] Améliorer la détection des types de documents

## Références

- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [REST API Design Guidelines](https://restfulapi.net/)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/README_en.md)
- [LayoutLMv3 Paper](https://arxiv.org/abs/2204.08387)

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Auteurs

Équipe GL3 - Projet IA

## Support

Pour toute question ou problème :
- Ouvrir une issue sur le repository GitHub
- Consulter la documentation dans le dossier `/docs`
- Contacter l'équipe de développement

