# Cet outil propose des recommandations personnalisées 
# de produits en fonction du budget, 
# de la catégorie souhaitée
# et du type de compte client (Standard, Premium, VIP).


CATALOGUE = [
    # id        nom                           prix     catégorie       score  cible
    {'id':'P001','nom':'Ordinateur Pro',     'prix':899.00, 'cat':'Informatique','score':4.7,'cible':['Premium','VIP']},
    {'id':'P002','nom':'Souris ergonomique', 'prix':49.90,  'cat':'Informatique','score':4.4,'cible':['Standard','Premium','VIP']},
    {'id':'P003','nom':'Bureau réglable',    'prix':350.00, 'cat':'Mobilier',    'score':4.5,'cible':['Premium','VIP']},
    {'id':'P004','nom':'Casque audio',       'prix':129.00, 'cat':'Audio',       'score':4.5,'cible':['Standard','Premium','VIP']},
    {'id':'P005','nom':'Écran 27" 4K',      'prix':549.00, 'cat':'Informatique','score':4.6,'cible':['Premium','VIP']},
    {'id':'P008','nom':'Chaise ergonomique', 'prix':280.00, 'cat':'Mobilier',    'score':4.6,'cible':['Standard','Premium','VIP']},
]


def recommander_produits(input_str: str) -> str:
    """
    Recommande des produits selon budget, catégorie et type de compte.
    Entrée : "budget,categorie,type_compte"
    Exemple : "300,Informatique,Premium"
    """
    budget, categorie, type_compte = input_str.strip().split(',')
    budget = float(budget)
    filtres = [
        p for p in CATALOGUE
        if p['prix'] <= budget
        and (categorie.lower() == 'toutes' or p['cat'].lower() == categorie.lower())
        and type_compte in p['cible']
    ]
    if not filtres:
        return 'Aucun produit trouvé pour ces critères.'
    filtres.sort(key=lambda x: x['score'], reverse=True)
    result = f"Recommandations (budget {budget:.0f}€, {categorie}, {type_compte}) :\n"
    for i, p in enumerate(filtres[:5], 1):
        result += f"  {i}. {p['nom']} – {p['prix']:.2f}€ – ⭐{p['score']}\n"
    return result

