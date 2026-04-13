"""
Script d'initialisation de la base de données SQLite.
Crée le fichier database.db avec les tables clients et produits,
puis insère les données initiales.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Table clients ────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id              TEXT PRIMARY KEY,
            nom             TEXT NOT NULL,
            email           TEXT,
            ville           TEXT,
            solde_compte    REAL DEFAULT 0.0,
            type_compte     TEXT DEFAULT 'Standard',
            date_inscription TEXT,
            achats_total    REAL DEFAULT 0.0
        )
    """)

    clients = [
        ("C001", "Marie Dupont",    "marie.dupont@email.fr", "Paris",  15420.50, "Premium",  "2021-03-15", 8750.00),
        ("C002", "Jean Martin",     None,                    None,      3200.00, "Standard", None,         0.00),
        ("C003", "Sophie Bernard",  None,                    None,     28900.00, "VIP",      None,         0.00),
        ("C004", "Lucas Petit",     None,                    None,       750.00, "Standard", None,         0.00),
    ]

    cur.executemany("""
        INSERT OR IGNORE INTO clients
            (id, nom, email, ville, solde_compte, type_compte, date_inscription, achats_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, clients)

    # ── Table produits ───────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produits (
            id      TEXT PRIMARY KEY,
            nom     TEXT NOT NULL,
            prix_ht REAL NOT NULL,
            stock   INTEGER DEFAULT 0
        )
    """)

    produits = [
        ("P001", "Ordinateur portable Pro", 899.00, 45),
        ("P002", "Souris ergonomique",       49.90, 120),
        ("P003", "Bureau réglable",          350.00,  18),
        ("P004", "Casque audio sans fil",    129.00,  67),
        ("P005", "Écran 27 pouces 4K",       549.00,  30),
    ]

    cur.executemany("""
        INSERT OR IGNORE INTO produits (id, nom, prix_ht, stock)
        VALUES (?, ?, ?, ?)
    """, produits)

    conn.commit()
    conn.close()
    print(f"Base de données initialisée : {DB_PATH}")
    print("  → Table 'clients'  : 4 enregistrements")
    print("  → Table 'produits' : 5 enregistrements")


if __name__ == "__main__":
    init_db()
