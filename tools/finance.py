"""
Récupère les cours boursiers réels via la bibliothèque yfinance.
Les données proviennent de Yahoo Finance (cours, variation du jour, volume).
"""
import sys
import os

# Ajout du dossier .deps au path si yfinance n'est pas installé globalement
_DEPS = os.path.join(os.path.dirname(__file__), "..", ".deps")
if os.path.isdir(_DEPS) and _DEPS not in sys.path:
    sys.path.insert(0, _DEPS)

try:
    import yfinance as yf
    _YFINANCE_DISPONIBLE = True
except ImportError:
    _YFINANCE_DISPONIBLE = False


def _formater_volume(vol: int) -> str:
    """Formate un volume en K / M / Md pour la lisibilité."""
    if vol >= 1_000_000_000:
        return f"{vol / 1_000_000_000:.2f} Md"
    if vol >= 1_000_000:
        return f"{vol / 1_000_000:.2f} M"
    if vol >= 1_000:
        return f"{vol / 1_000:.1f} K"
    return str(vol)


def obtenir_cours_action(symbole: str) -> str:
    """Retourne le cours réel d'une action via yfinance : prix, variation du jour, volume."""
    if not _YFINANCE_DISPONIBLE:
        return "Erreur : la bibliothèque yfinance n'est pas installée."

    symbole = symbole.strip().upper()
    try:
        ticker = yf.Ticker(symbole)
        info = ticker.fast_info

        cours = info.last_price
        cloture_precedente = info.previous_close
        volume = info.last_volume
        devise = getattr(info, "currency", "USD")

        if cours is None or cloture_precedente is None:
            return f"Aucune donnée disponible pour le symbole '{symbole}'."

        variation_val = cours - cloture_precedente
        variation_pct = (variation_val / cloture_precedente) * 100
        tendance = "📈" if variation_pct >= 0 else "📉"

        return (
            f"{symbole} {tendance} : {cours:.2f} {devise} "
            f"({variation_pct:+.2f}% / {variation_val:+.2f} {devise}) | "
            f"Volume : {_formater_volume(int(volume))}"
        )

    except Exception:
        return (
            f"Impossible de récupérer le cours de '{symbole}'. "
            "Vérifiez le symbole ou la connexion réseau."
        )


def obtenir_cours_crypto(symbole: str) -> str:
    """Retourne le cours réel d'une cryptomonnaie via yfinance (paire SYMBOL-USD)."""
    if not _YFINANCE_DISPONIBLE:
        return "Erreur : la bibliothèque yfinance n'est pas installée."

    symbole = symbole.strip().upper()
    paire = f"{symbole}-USD"
    try:
        ticker = yf.Ticker(paire)
        info = ticker.fast_info

        cours = info.last_price
        cloture_precedente = info.previous_close
        volume = info.last_volume

        if cours is None or cloture_precedente is None:
            return f"Aucune donnée disponible pour la crypto '{symbole}'."

        variation_val = cours - cloture_precedente
        variation_pct = (variation_val / cloture_precedente) * 100
        tendance = "📈" if variation_pct >= 0 else "📉"

        return (
            f"{symbole} {tendance} : {cours:.2f} USD "
            f"({variation_pct:+.2f}% / {variation_val:+.2f} USD) | "
            f"Volume : {_formater_volume(int(volume))}"
        )

    except Exception:
        return (
            f"Impossible de récupérer le cours de '{symbole}'. "
            "Vérifiez le symbole ou la connexion réseau."
        )
