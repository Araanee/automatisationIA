"""
Initialisation de la base de données SQLite du portefeuille.
Crée portfolio.db avec les tables :
  - positions    : actifs détenus (actions, crypto, ETF, obligations)
  - historique_prix : cours journaliers des 30 derniers jours
"""
import sqlite3
import os
import random
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")


def init_portfolio_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Table positions ──────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            symbole         TEXT NOT NULL UNIQUE,
            nom             TEXT NOT NULL,
            type_actif      TEXT NOT NULL,   -- action / crypto / ETF / obligation
            secteur         TEXT,
            quantite        REAL NOT NULL,
            prix_achat      REAL NOT NULL,   -- prix unitaire d'achat (EUR)
            prix_actuel     REAL NOT NULL,   -- dernier cours connu (EUR)
            date_achat      TEXT NOT NULL,
            beta            REAL DEFAULT 1.0,
            volatilite_30j  REAL DEFAULT 0.0  -- écart-type journalier sur 30j (%)
        )
    """)

    positions = [
        # symbole, nom, type, secteur, qté, px_achat, px_actuel, date_achat, beta, vol_30j
        ("AAPL",    "Apple Inc.",             "action",    "Technologie",   10,   150.00,  258.09, "2022-06-15", 1.20, 1.8),
        ("MSFT",    "Microsoft Corp.",        "action",    "Technologie",    5,   320.00,  381.81, "2022-09-01", 0.90, 1.5),
        ("AIR.PA",  "Airbus SE",             "action",    "Aéronautique",   8,   130.00,  170.46, "2023-01-10", 1.10, 2.1),
        ("MC.PA",   "LVMH Moët Hennessy",    "action",    "Luxe",           2,   620.00,  758.00, "2022-11-20", 0.85, 1.9),
        ("TSLA",    "Tesla Inc.",             "action",    "Automobile",     3,   200.00,  248.00, "2023-03-05", 2.00, 3.5),
        ("BTC",     "Bitcoin",               "crypto",    "Cryptomonnaie", 0.5, 45000.00,72223.97,"2021-12-01", 2.50, 5.2),
        ("ETH",     "Ethereum",              "crypto",    "Cryptomonnaie",  2,  2000.00, 2226.63, "2022-02-14", 2.20, 4.8),
        ("SP500",   "ETF S&P 500",           "ETF",       "Indice large",   5,   400.00,  462.00, "2022-01-03", 1.00, 1.2),
        ("OBL_FR",  "OAT France 10 ans 3%",  "obligation","Taux fixe",   1000,     1.00,    1.03, "2023-06-01", 0.10, 0.1),
    ]

    cur.executemany("""
        INSERT OR IGNORE INTO positions
            (symbole, nom, type_actif, secteur, quantite, prix_achat,
             prix_actuel, date_achat, beta, volatilite_30j)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, positions)

    # ── Table historique_prix ────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historique_prix (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            symbole      TEXT NOT NULL,
            date         TEXT NOT NULL,
            prix_cloture REAL NOT NULL,
            variation_pct REAL,
            volume       INTEGER,
            UNIQUE(symbole, date)
        )
    """)

    # Prix de base pour générer l'historique (30 jours)
    prix_base = {
        "AAPL":   (258.09, 1.8),
        "MSFT":   (381.81, 1.5),
        "AIR.PA": (170.46, 2.1),
        "MC.PA":  (758.00, 1.9),
        "TSLA":   (248.00, 3.5),
        "BTC":    (72223.97, 5.2),
        "ETH":    (2226.63, 4.8),
        "SP500":  (462.00, 1.2),
        "OBL_FR": (1.03, 0.1),
    }

    random.seed(42)  # résultats reproductibles
    historique_rows = []
    today = date.today()

    for symbole, (px_fin, vol_pct) in prix_base.items():
        # Reconstruction backward : partant du cours actuel, on remonte 30j
        prix = px_fin
        jours_historique = []
        for i in range(30):
            d = today - timedelta(days=i)
            if d.weekday() < 5:  # jours ouvrés seulement
                jours_historique.append((d.isoformat(), round(prix, 4)))
            variation = random.gauss(0, vol_pct / 100)
            prix = prix / (1 + variation)

        # On inverse pour avoir l'ordre chronologique
        for i, (d, p) in enumerate(reversed(jours_historique)):
            if i == 0:
                variation_j = None
                prev = p
            else:
                prev_p = jours_historique[len(jours_historique) - i][1]
                variation_j = round((p - prev_p) / prev_p * 100, 4) if prev_p else None
            volume = random.randint(500_000, 50_000_000) if symbole not in ("BTC", "ETH", "OBL_FR") else random.randint(1_000_000, 100_000_000)
            historique_rows.append((symbole, d, p, variation_j, volume))

    cur.executemany("""
        INSERT OR IGNORE INTO historique_prix
            (symbole, date, prix_cloture, variation_pct, volume)
        VALUES (?, ?, ?, ?, ?)
    """, historique_rows)

    conn.commit()
    conn.close()

    print(f"Base portefeuille initialisée : {DB_PATH}")
    print(f"  → {len(positions)} positions")
    print(f"  → {len(historique_rows)} entrées d'historique")


if __name__ == "__main__":
    init_portfolio_db()
