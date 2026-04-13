"""
Accès à la base de données SQLite (database.db).
Fournit des fonctions de recherche de clients et de produits
utilisées comme outils par l'agent LangChain.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database.db")


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rechercher_client(query: str) -> str:
    """Recherche un client par nom ou par identifiant."""
    query = query.strip()
    conn = _get_connection()
    cur = conn.cursor()

    # Recherche par ID exact
    cur.execute("SELECT * FROM clients WHERE UPPER(id) = ?", (query.upper(),))
    row = cur.fetchone()

    if row is None:
        # Recherche par nom (insensible à la casse)
        cur.execute("SELECT * FROM clients WHERE LOWER(nom) LIKE ?", (f"%{query.lower()}%",))
        row = cur.fetchone()

    conn.close()

    if row is None:
        return f"Aucun client trouvé pour : '{query}'"

    return (
        f"Client : {row['nom']} | "
        f"Solde : {row['solde_compte']:.2f} € | "
        f"Type de compte : {row['type_compte']}"
    )


def rechercher_produit(query: str) -> str:
    """Recherche un produit par nom ou identifiant. Retourne prix HT, TVA, prix TTC, stock."""
    query = query.strip()
    conn = _get_connection()
    cur = conn.cursor()

    # Recherche par ID exact
    cur.execute("SELECT * FROM produits WHERE UPPER(id) = ?", (query.upper(),))
    row = cur.fetchone()

    if row is None:
        # Recherche par nom (insensible à la casse)
        cur.execute("SELECT * FROM produits WHERE LOWER(nom) LIKE ?", (f"%{query.lower()}%",))
        row = cur.fetchone()

    conn.close()

    if row is None:
        return f"Aucun produit trouvé pour : '{query}'"

    tva = row['prix_ht'] * 0.20
    prix_ttc = row['prix_ht'] + tva
    return (
        f"Produit : {row['nom']} | "
        f"Prix HT : {row['prix_ht']:.2f} € | "
        f"TVA : {tva:.2f} € | "
        f"Prix TTC : {prix_ttc:.2f} € | "
        f"Stock : {row['stock']}"
    )


def lister_tous_les_clients(query: str = "") -> str:
    """Retourne la liste complète de tous les clients."""
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, type_compte, solde_compte FROM clients ORDER BY id")
    rows = cur.fetchall()
    conn.close()

    result = "Liste des clients :\n"
    for row in rows:
        result += (
            f"  {row['id']} : {row['nom']} | "
            f"{row['type_compte']} | "
            f"Solde : {row['solde_compte']:.2f} €\n"
        )
    return result
