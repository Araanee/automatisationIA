"""
Outil de calcul de portefeuille boursier en temps réel.
Récupère les cours via yfinance et calcule la valeur de chaque ligne,
la valeur totale du portefeuille et la variation globale du jour.
"""
import sys
import os

_DEPS = os.path.join(os.path.dirname(__file__), "..", ".deps")
if os.path.isdir(_DEPS) and _DEPS not in sys.path:
    sys.path.insert(0, _DEPS)

try:
    import yfinance as yf
    _YFINANCE_DISPONIBLE = True
except ImportError:
    _YFINANCE_DISPONIBLE = False


def calculer_portefeuille(input_str: str) -> str:
    """
    Calcule la valeur totale d'un portefeuille boursier en temps réel.

    Entrée : liste d'actions au format SYMBOLE:QUANTITE séparés par |
    Exemple : "AAPL:10|MSFT:5|BTC:0.5|AIR.PA:8"

    Retourne la valeur de chaque ligne, la valeur totale
    et la variation globale du portefeuille sur la journée.
    """
    if not _YFINANCE_DISPONIBLE:
        return "Erreur : la bibliothèque yfinance n'est pas installée."

    input_str = input_str.strip()
    if not input_str:
        return "Entrée vide. Format attendu : SYMBOLE:QUANTITE|SYMBOLE:QUANTITE"

    # ── Parsing ────────────────────────────────────────────────────────
    lignes = []
    erreurs = []

    for partie in input_str.split("|"):
        partie = partie.strip()
        if not partie:
            continue
        if ":" not in partie:
            erreurs.append(f"Format invalide : '{partie}' (attendu SYMBOLE:QUANTITE)")
            continue
        symbole_raw, qte_raw = partie.split(":", 1)
        symbole = symbole_raw.strip().upper()
        try:
            quantite = float(qte_raw.strip())
        except ValueError:
            erreurs.append(f"Quantité invalide pour {symbole} : '{qte_raw}'")
            continue
        if quantite <= 0:
            erreurs.append(f"Quantité nulle ou négative ignorée : {symbole}:{quantite}")
            continue
        lignes.append((symbole, quantite))

    if not lignes:
        return "Aucune position valide trouvée.\n" + "\n".join(erreurs)

    # ── Récupération des cours yfinance ────────────────────────────────
    resultats = []
    valeur_totale = 0.0
    valeur_precedente_totale = 0.0

    for symbole, quantite in lignes:
        cours = None
        cloture_precedente = None
        devise = "USD"

        # Essai 1 : paire crypto SYMBOL-USD (BTC-USD, ETH-USD…)
        try:
            info = yf.Ticker(f"{symbole}-USD").fast_info
            cours = info.last_price
            cloture_precedente = info.previous_close
            devise = "USD"
        except Exception:
            cours = None

        # Essai 2 : symbole direct (actions, ETF, obligations…)
        if cours is None:
            try:
                info = yf.Ticker(symbole).fast_info
                cours = info.last_price
                cloture_precedente = info.previous_close
                devise = getattr(info, "currency", "USD")
            except Exception:
                cours = None

        if cours is None:
            resultats.append({
                "symbole": symbole,
                "quantite": quantite,
                "erreur": "cours indisponible",
            })
            continue

        if cours is None:
            resultats.append({
                "symbole": symbole,
                "quantite": quantite,
                "erreur": "cours indisponible",
            })
            continue

        # Si la clôture précédente est indisponible, variation = 0
        if cloture_precedente is None:
            cloture_precedente = cours

        valeur_ligne = quantite * cours
        valeur_ligne_precedente = quantite * cloture_precedente
        variation_pct = (cours - cloture_precedente) / cloture_precedente * 100 if cloture_precedente else 0
        variation_val = valeur_ligne - valeur_ligne_precedente

        valeur_totale += valeur_ligne
        valeur_precedente_totale += valeur_ligne_precedente

        resultats.append({
            "symbole": symbole,
            "quantite": quantite,
            "cours": cours,
            "devise": devise,
            "valeur_ligne": valeur_ligne,
            "variation_pct": variation_pct,
            "variation_val": variation_val,
            "erreur": None,
        })

    # ── Mise en forme de la réponse ────────────────────────────────────
    lines = ["=== VALORISATION DU PORTEFEUILLE ===\n"]

    for r in resultats:
        if r.get("erreur"):
            lines.append(
                f"  {'⚠':2} {r['symbole']:10} qté={r['quantite']:<8}  "
                f"[Erreur : {r['erreur']}]"
            )
            continue

        tendance = "📈" if r["variation_pct"] >= 0 else "📉"
        poids = r["valeur_ligne"] / valeur_totale * 100 if valeur_totale else 0
        lines.append(
            f"  {tendance} {r['symbole']:10} "
            f"qté={r['quantite']:<8}  "
            f"cours={r['cours']:>10.2f} {r['devise']}  "
            f"valeur={r['valeur_ligne']:>12.2f} {r['devise']}  "
            f"jour={r['variation_pct']:>+6.2f}% ({r['variation_val']:>+10.2f} {r['devise']})  "
            f"poids={poids:.1f}%"
        )

    # Variation globale du portefeuille sur la journée
    variation_globale_val = valeur_totale - valeur_precedente_totale
    variation_globale_pct = (
        variation_globale_val / valeur_precedente_totale * 100
        if valeur_precedente_totale else 0
    )
    tendance_globale = "📈" if variation_globale_pct >= 0 else "📉"

    lines.append(f"\n  {'─'*80}")
    lines.append(
        f"  {tendance_globale} Valeur totale    : {valeur_totale:>14,.2f}"
    )
    lines.append(
        f"     Variation du jour : {variation_globale_val:>+14,.2f}  "
        f"({variation_globale_pct:>+.2f}%)"
    )

    if erreurs:
        lines.append("\n  Avertissements :")
        for e in erreurs:
            lines.append(f"    • {e}")

    return "\n".join(lines)
