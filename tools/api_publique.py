# Cet outil appelle l'API publique gratuite Frankfurter (api.frankfurter.app)
# pour récupérer les taux de change officiels de la Banque Centrale Européenne.
# Aucune clé d'authentification n'est nécessaire.


import requests

API_BASE_URL = 'https://api.frankfurter.app'


def convertir_devise(input_str: str) -> str:
    """
    Convertit un montant entre deux devises via l'API Frankfurter.
    Entrée : "montant,devise_source,devise_cible"
    Exemple : "100,USD,EUR" → convertit 100 dollars en euros
    """
    parties = input_str.strip().split(',')
    montant = float(parties[0])
    devise_from = parties[1].strip().upper()
    devise_to   = parties[2].strip().upper()
    # Appel à l'API publique (gratuit, sans clé)
    url = f"{API_BASE_URL}/latest"
    params = {'amount': montant, 'from': devise_from, 'to': devise_to}
    response = requests.get(url, params=params, timeout=5)
    if response.status_code != 200:
        return f"Erreur API : {response.status_code}"
    data = response.json()
    montant_converti = data['rates'][devise_to]
    taux = montant_converti / montant
    return (
        f"{montant:.2f} {devise_from} = {montant_converti:.2f} {devise_to}\n"
        f"Taux : 1 {devise_from} = {taux:.4f} {devise_to}"
    )


def obtenir_taux_du_jour(devise_base: str = "EUR") -> str:
    """
    Retourne les principaux taux de change du jour pour une devise de base.
    Entrée : code devise ex: "EUR", "USD", "GBP"
    """
    devise_base = devise_base.strip().upper()
    url = f"{API_BASE_URL}/latest"
    params = {'from': devise_base}
    response = requests.get(url, params=params, timeout=5)
    if response.status_code != 200:
        return f"Erreur API : {response.status_code}"
    data = response.json()
    devises_cles = ['USD', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY']
    result = f"Taux du jour ({data['date']}) — Base : {devise_base}\n"
    for dev in devises_cles:
        if dev in data['rates'] and dev != devise_base:
            result += f"  1 {devise_base} = {data['rates'][dev]:.4f} {dev}\n"
    return result

