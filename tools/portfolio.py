"""
Outils d'analyse du portefeuille financier.
Interroge portfolio.db (SQLite) pour répondre aux questions de l'agent.
"""
import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio.db")


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ── helpers internes ──────────────────────────────────────────────────────────

def _valeur_position(row) -> float:
    return row["quantite"] * row["prix_actuel"]

def _valeur_investie(row) -> float:
    return row["quantite"] * row["prix_achat"]

def _gain_pct(row) -> float:
    inv = _valeur_investie(row)
    return ((_valeur_position(row) - inv) / inv * 100) if inv else 0.0


# ── Outil 1 : liste des positions ─────────────────────────────────────────────

def lister_positions(query: str = "") -> str:
    """Retourne toutes les positions du portefeuille avec valorisation et P&L."""
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM positions ORDER BY type_actif, symbole"
    ).fetchall()
    conn.close()

    if not rows:
        return "Aucune position dans le portefeuille."

    valeur_totale = sum(_valeur_position(r) for r in rows)
    lines = ["Portefeuille — positions détaillées :\n"]

    type_courant = None
    for r in rows:
        if r["type_actif"] != type_courant:
            type_courant = r["type_actif"]
            lines.append(f"\n  [{type_courant.upper()}]")

        val = _valeur_position(r)
        gain = _gain_pct(r)
        poids = val / valeur_totale * 100
        signe = "+" if gain >= 0 else ""
        lines.append(
            f"  {r['symbole']:10} {r['nom'][:24]:24} "
            f"qté={r['quantite']:>6}  "
            f"px={r['prix_actuel']:>10.2f} €  "
            f"val={val:>10.2f} €  "
            f"P&L={signe}{gain:.1f}%  "
            f"poids={poids:.1f}%"
        )

    valeur_investie = sum(_valeur_investie(r) for r in rows)
    gain_total = valeur_totale - valeur_investie
    gain_total_pct = gain_total / valeur_investie * 100 if valeur_investie else 0

    lines.append(f"\n  {'─'*70}")
    lines.append(
        f"  Valeur totale : {valeur_totale:,.2f} €  |  "
        f"Investi : {valeur_investie:,.2f} €  |  "
        f"Gain total : {gain_total:+,.2f} € ({gain_total_pct:+.1f}%)"
    )
    return "\n".join(lines)


# ── Outil 2 : résumé du portefeuille ─────────────────────────────────────────

def resumer_portefeuille(query: str = "") -> str:
    """Résumé global : valeur, performance, répartition par type et secteur."""
    conn = _conn()
    rows = conn.execute("SELECT * FROM positions").fetchall()
    conn.close()

    if not rows:
        return "Portefeuille vide."

    valeur_totale = sum(_valeur_position(r) for r in rows)
    valeur_investie = sum(_valeur_investie(r) for r in rows)
    gain_total = valeur_totale - valeur_investie
    gain_pct = gain_total / valeur_investie * 100 if valeur_investie else 0

    # Répartition par type
    par_type: dict[str, float] = {}
    for r in rows:
        par_type[r["type_actif"]] = par_type.get(r["type_actif"], 0) + _valeur_position(r)

    # Répartition par secteur
    par_secteur: dict[str, float] = {}
    for r in rows:
        par_secteur[r["secteur"]] = par_secteur.get(r["secteur"], 0) + _valeur_position(r)

    lines = [
        "=== RÉSUMÉ DU PORTEFEUILLE ===",
        f"  Valeur de marché   : {valeur_totale:>12,.2f} €",
        f"  Capital investi    : {valeur_investie:>12,.2f} €",
        f"  Plus/moins-value   : {gain_total:>+12,.2f} € ({gain_pct:+.1f}%)",
        f"  Nombre de lignes   : {len(rows)}",
        "",
        "  Répartition par type :",
    ]
    for typ, val in sorted(par_type.items(), key=lambda x: -x[1]):
        lines.append(f"    {typ:12} : {val:>10,.2f} € ({val/valeur_totale*100:.1f}%)")

    lines.append("\n  Répartition par secteur :")
    for sec, val in sorted(par_secteur.items(), key=lambda x: -x[1]):
        lines.append(f"    {sec:20} : {val:>10,.2f} € ({val/valeur_totale*100:.1f}%)")

    return "\n".join(lines)


# ── Outil 3 : analyse de risque ───────────────────────────────────────────────

def analyser_risque(query: str = "") -> str:
    """
    Analyse de risque du portefeuille :
    beta pondéré, actifs les plus risqués, concentration, diversification.
    """
    conn = _conn()
    rows = conn.execute("SELECT * FROM positions").fetchall()
    conn.close()

    if not rows:
        return "Aucune position à analyser."

    valeur_totale = sum(_valeur_position(r) for r in rows)

    # Beta pondéré du portefeuille
    beta_pond = sum(
        r["beta"] * (_valeur_position(r) / valeur_totale) for r in rows
    )

    # Volatilité pondérée
    vol_pond = sum(
        r["volatilite_30j"] * (_valeur_position(r) / valeur_totale) for r in rows
    )

    # Classement par niveau de risque (beta + volatilité)
    actifs_risques = sorted(
        rows,
        key=lambda r: r["beta"] * 0.5 + r["volatilite_30j"] * 0.5,
        reverse=True,
    )

    # Concentration (Herfindahl)
    hhi = sum((_valeur_position(r) / valeur_totale) ** 2 for r in rows) * 100

    lines = [
        "=== ANALYSE DE RISQUE DU PORTEFEUILLE ===",
        "",
        f"  Beta pondéré          : {beta_pond:.2f}  "
        f"({'> marché' if beta_pond > 1 else '< marché ou neutre'})",
        f"  Volatilité pondérée   : {vol_pond:.2f} % / jour",
        f"  Indice HHI (conc.)    : {hhi:.1f}  "
        f"({'concentré' if hhi > 25 else 'diversifié'})",
        "",
        "  Actifs les plus risqués (beta × volatilité) :",
    ]

    for r in actifs_risques[:5]:
        score = r["beta"] * 0.5 + r["volatilite_30j"] * 0.5
        poids = _valeur_position(r) / valeur_totale * 100
        niveau = "⚠ ÉLEVÉ" if score > 3 else ("↑ MOYEN" if score > 1.5 else "✓ FAIBLE")
        lines.append(
            f"    {r['symbole']:10} beta={r['beta']:.2f}  "
            f"vol={r['volatilite_30j']:.1f}%  "
            f"poids={poids:.1f}%  [{niveau}]"
        )

    # Alertes
    lines.append("\n  Alertes :")
    alertes = []
    for r in rows:
        poids = _valeur_position(r) / valeur_totale * 100
        if poids > 25:
            alertes.append(f"    • {r['symbole']} représente {poids:.1f}% du portefeuille (surpondération)")
        if r["type_actif"] == "crypto" and poids > 15:
            alertes.append(f"    • {r['symbole']} (crypto) : exposition élevée ({poids:.1f}%)")
        if r["beta"] > 1.8:
            alertes.append(f"    • {r['symbole']} : beta très élevé ({r['beta']:.2f}) — actif très volatil")

    lines += alertes if alertes else ["    Aucune alerte majeure."]
    return "\n".join(lines)


# ── Outil 4 : performance d'un actif ─────────────────────────────────────────

def performance_actif(symbole: str) -> str:
    """
    Performance détaillée d'un actif spécifique.
    Entrée : symbole ex AAPL, BTC, AIR.PA
    """
    symbole = symbole.strip().upper()
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM positions WHERE UPPER(symbole) = ?", (symbole,)
    ).fetchone()

    if row is None:
        # Recherche partielle
        row = conn.execute(
            "SELECT * FROM positions WHERE UPPER(nom) LIKE ?",
            (f"%{symbole}%",)
        ).fetchone()

    if row is None:
        conn.close()
        return f"Actif '{symbole}' introuvable dans le portefeuille."

    # Historique des 30 derniers jours
    historique = conn.execute(
        "SELECT date, prix_cloture, variation_pct FROM historique_prix "
        "WHERE symbole = ? ORDER BY date DESC LIMIT 30",
        (row["symbole"],)
    ).fetchall()
    conn.close()

    val = _valeur_position(row)
    inv = _valeur_investie(row)
    gain = val - inv
    gain_pct = _gain_pct(row)

    lines = [
        f"=== PERFORMANCE : {row['symbole']} — {row['nom']} ===",
        f"  Type        : {row['type_actif']} | Secteur : {row['secteur']}",
        f"  Quantité    : {row['quantite']}",
        f"  Prix achat  : {row['prix_achat']:.2f} €  (le {row['date_achat']})",
        f"  Prix actuel : {row['prix_actuel']:.2f} €",
        f"  Valorisation: {val:.2f} €",
        f"  P&L         : {gain:+.2f} € ({gain_pct:+.1f}%)",
        f"  Beta        : {row['beta']:.2f} | Volatilité 30j : {row['volatilite_30j']:.1f}%/j",
    ]

    if historique:
        variations = [h["variation_pct"] for h in historique if h["variation_pct"] is not None]
        if variations:
            lines.append(f"\n  Historique 30 jours :")
            lines.append(f"    Plus haute clôture : {max(h['prix_cloture'] for h in historique):.2f} €")
            lines.append(f"    Plus basse clôture : {min(h['prix_cloture'] for h in historique):.2f} €")
            lines.append(f"    Variation moy/jour : {sum(variations)/len(variations):+.2f}%")
            lines.append(f"    Dernière clôture   : {historique[0]['prix_cloture']:.2f} € "
                         f"({historique[0]['variation_pct']:+.2f}% le {historique[0]['date']})")

    return "\n".join(lines)


# ── Outil 5 : meilleures et pires performances ────────────────────────────────

def top_performances(query: str = "") -> str:
    """
    Classement des actifs par performance (meilleurs et pires P&L en %).
    """
    conn = _conn()
    rows = conn.execute("SELECT * FROM positions").fetchall()
    conn.close()

    if not rows:
        return "Portefeuille vide."

    classes = sorted(rows, key=_gain_pct, reverse=True)

    lines = ["=== CLASSEMENT DES PERFORMANCES ===", ""]
    lines.append("  Top performers (gains) :")
    for r in classes[:4]:
        g = _gain_pct(r)
        lines.append(f"    {'📈' if g >= 0 else '📉'} {r['symbole']:10} {g:+.1f}%  "
                     f"({r['prix_achat']:.2f} → {r['prix_actuel']:.2f} €)")

    lines.append("\n  Moins bons performers :")
    for r in classes[-3:]:
        g = _gain_pct(r)
        lines.append(f"    {'📈' if g >= 0 else '📉'} {r['symbole']:10} {g:+.1f}%  "
                     f"({r['prix_achat']:.2f} → {r['prix_actuel']:.2f} €)")

    return "\n".join(lines)
