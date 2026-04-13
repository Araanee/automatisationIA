# Cet outil effectue différentes transformations sur du texte :
# résumé automatique, formatage en rapport, extraction de mots-clés et transformation de casse.


import re
from datetime import datetime


def resumer_texte(texte: str) -> str:
    """Génère un résumé avec statistiques (mots, phrases, temps de lecture)."""
    nb_mots = len(texte.split())
    phrases = [p.strip() for p in re.split(r'[.!?]+', texte) if len(p.strip()) > 10]
    resume = '. '.join(phrases[:2]) + '.' if len(phrases) >= 2 else texte[:150]
    temps = max(1, nb_mots // 200)   # ~200 mots/minute
    return f"Résumé : {resume}\nMots : {nb_mots} | Temps lecture : {temps} min"


def formater_rapport(input_str: str) -> str:
    """Formate paires clé:valeur en rapport. Entrée : "Cle1:Val1|Cle2:Val2" """
    date = datetime.now().strftime('%d/%m/%Y %H:%M')
    if '|' in input_str and ':' in input_str:
        lignes = []
        for paire in input_str.split('|'):
            if ':' in paire:
                cle, val = paire.split(':', 1)
                lignes.append(f"  • {cle.strip()} : {val.strip()}")
        return f"=== RAPPORT ({date}) ===\n" + '\n'.join(lignes)
    return f"=== RAPPORT ({date}) ===\n  {input_str.strip()}"


def extraire_mots_cles(texte: str) -> str:
    """Extrait les mots-clés (filtre les mots vides français)."""
    mots_vides = {'le','la','les','un','une','des','de','du','en','et','ou',
                  'est','sont','à','au','aux','par','sur','dans','avec'}
    mots_nettoyes = re.sub(r'[^\w\s]', ' ', texte.lower()).split()
    compteur = {}
    for mot in mots_nettoyes:
        if mot not in mots_vides and len(mot) > 3:
            compteur[mot] = compteur.get(mot, 0) + 1
    tries = sorted(compteur.items(), key=lambda x: x[1], reverse=True)[:10]
    return '\n'.join([f"  {mot}: {freq}x" for mot, freq in tries])


def convertir_majuscules_minuscules(input_str: str) -> str:
    """
    Transforme la casse d'un texte.
    Entrée : "mode,texte" — modes : upper, lower, title, swap
    Exemple : "upper,bonjour le monde"
    """
    parties = input_str.strip().split(',', 1)
    if len(parties) < 2:
        return "Format attendu : 'mode,texte' (modes : upper, lower, title, swap)"
    mode, texte = parties[0].strip().lower(), parties[1].strip()
    if mode == 'upper':
        return f"MAJUSCULES : {texte.upper()}"
    elif mode == 'lower':
        return f"minuscules : {texte.lower()}"
    elif mode == 'title':
        return f"Titre : {texte.title()}"
    elif mode == 'swap':
        return f"Inversé : {texte.swapcase()}"
    else:
        return f"Mode inconnu '{mode}'. Modes disponibles : upper, lower, title, swap"

