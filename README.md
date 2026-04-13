# Agent LangChain — Automatisation Financière

Agent conversationnel ReAct/OpenAI-Tools propulsé par **LangChain** et **GPT-4o-mini**.  
Il combine base de données SQLite, données boursières en temps réel (yfinance), calculs financiers,
recherche web (Tavily) et exécution de code Python, le tout exposé en trois interfaces :
terminal interactif, interface web Streamlit et API REST FastAPI.

---

## Prérequis

| Outil | Version minimale |
|---|---|
| Python | 3.11+ |
| pip / venv | inclus avec Python |

---

## Installation

### 1 — Cloner / ouvrir le projet

```bash
cd /home/epita/Documents/automatisation
```

### 2 — Créer et activer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```


### 3 — Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4 — Configurer les clés API

```bash
cp .env.example .env
```

Éditez `.env` et renseignez vos clés :

```env
OPENAI_API_KEY="sk-proj-..."   # https://platform.openai.com/api-keys
TAVILY_API_KEY="tvly-..."      # https://tavily.com  (gratuit, 1000 req/mois)
```

### 5 — Initialiser les bases de données

```bash
# Base clients + produits (A1)
python init_db.py

# Base portefeuille financier (D1)
python init_portfolio_db.py
```

---

## Lancement

### Interface terminal — `main.py`

```bash
python main.py
```

Un menu interactif propose 9 scénarios numérotés :

```
  1. Scénario 1 – Consultation base de données
  2. Scénario 2 – Données financières
  3. Scénario 3 – Calculs financiers multiples
  4. Scénario 4 – Conversion de devises (API)
  5. Scénario 5 – Calcul de prêt + intérêts
  6. Scénario 6 – Recommandation personnalisée
  7. Scénario 7 – Analyse de texte complète
  8. Scénario 8 – Analyse financière complète (multi-outils)
  9. Scénario 9 – Mémoire conversationnelle (3 questions liées)
```

---

### Interface web — `app.py` (Streamlit)

```bash
streamlit run app.py
# → http://localhost:8501
```

- Champ de saisie en bas de page
- Historique complet de la conversation avec durée de réponse
- Panneau latéral listant les 10 outils disponibles
- Bouton « Nouvelle conversation » pour réinitialiser
- Mémoire conversationnelle isolée par onglet/session

---

### API REST — `api.py` (FastAPI)

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
# → http://localhost:8000/docs  (Swagger UI)
```

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/api/agent/query` | Question → réponse JSON |
| `GET` | `/api/portfolio/positions` | Liste des positions du portefeuille |
| `GET` | `/api/portfolio/resume` | Résumé global du portefeuille |
| `GET` | `/api/portfolio/risque` | Analyse de risque |
| `GET` | `/health` | Statut du service |

**Exemple d'appel :**

```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Quels sont mes actifs les plus risqués ?"}'
```

```json
{
  "question": "Quels sont mes actifs les plus risqués ?",
  "reponse": "BTC (beta 2.50, 69 % du portefeuille) et ETH (beta 2.20)…",
  "duree_ms": 3241,
  "statut": "ok"
}
```

---

## Structure du projet

```
automatisation/
│
├── agent.py                  # Définition des outils + creer_agent() avec mémoire
├── main.py                   # Interface terminal avec menu des scénarios
├── app.py                    # Interface web Streamlit (C1)
├── api.py                    # API REST FastAPI (D1)
│
├── init_db.py                # Initialisation base clients/produits (A1)
├── init_portfolio_db.py      # Initialisation base portefeuille (D1)
│
├── tools/
│   ├── database.py           # Recherche client/produit via SQLite (A1)
│   ├── finance.py            # Cours actions/crypto via yfinance (A2)
│   ├── portefeuille.py       # Valorisation multi-actifs en temps réel (B1)
│   ├── portfolio.py          # Analyse portefeuille SQLite (D1)
│   ├── calculs.py            # TVA, intérêts, marge, mensualité (A-base)
│   ├── api_publique.py       # Conversion devises Frankfurter (A-base)
│   ├── recommandation.py     # Recommandation produits par profil (A-base)
│   └── text.py               # Résumé, mots-clés, formatage (A-base)
│
├── .env                      # Clés API (ne pas committer)
├── .env.example              # Modèle de configuration
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
```

---

## Outils de l'agent

| # | Nom | Module | Description |
|---|---|---|---|
| 1 | `rechercher_client` | `tools/database.py` | Client par nom ou ID (SQLite) |
| 2 | `rechercher_produit` | `tools/database.py` | Produit par nom ou ID (SQLite) |
| 3 | `cours_action` | `tools/finance.py` | Cours boursier réel (yfinance) |
| 4 | `cours_crypto` | `tools/finance.py` | Cours crypto réel (yfinance) |
| 5 | `calculer_tva` | `tools/calculs.py` | Prix HT → TTC |
| 6 | `calculer_interets` | `tools/calculs.py` | Intérêts composés |
| 7 | `calculer_marge` | `tools/calculs.py` | Marge commerciale |
| 8 | `calculer_mensualite` | `tools/calculs.py` | Mensualité de prêt |
| 9 | `convertir_devise` | `tools/api_publique.py` | Taux de change (Frankfurter) |
| 10 | `resumer_texte` | `tools/text.py` | Résumé + statistiques |
| 11 | `formater_rapport` | `tools/text.py` | Mise en forme clé:valeur |
| 12 | `extraire_mots_cles` | `tools/text.py` | Extraction de mots-clés |
| 13 | `recommander_produits` | `tools/recommandation.py` | Produits par budget et profil |
| 14 | `calculer_portefeuille` | `tools/portefeuille.py` | Valorisation temps réel (B1) |
| 15 | `Python_REPL` | `langchain_experimental` | Exécution de code Python (B2) ⚠️ |
| 16 | `recherche_web` | `langchain_tavily` | Recherche Tavily (A3) |

> ⚠️ `Python_REPL` exécute du code arbitraire. Ne pas exposer en production sans sandbox.