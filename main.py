
import os
from dotenv import load_dotenv
from agent import creer_agent, interroger_agent



# Partie Intitulé Points Difficulté
# A1 Base de données MySql/Postgres 2 pts ⭐ Facile
# A2 Cours boursiers réels (yfinance) 2 pts ⭐ Facile
# A3 Recherche web (TavilySearch) 2 pts ⭐⭐ Moyen (genre si c'est une question d'actualite dont le LLM n'a pas connaissance)
# B1 Calcul de portefeuille boursier 2 pts ⭐⭐ Moyen
# B2 PythonREPLTool 4 pts ⭐⭐⭐ Difficile
# C1 Interface Streamlit 2 pts ⭐ Facile
# C2 Mémoire conversationnelle 2 pts ⭐⭐ Moyen
# D1 Api Rest Python + tool + database 4 pts ⭐⭐⭐ Difficile
# TOTAL 20 pts

load_dotenv()

SCENARIOS = {
    "1": (
        "Scénario 1 – Consultation base de données",
        "Quelles sont les informations du client Marie Dupont ? "
        "Quel est son solde et son type de compte ?"
    ),
    "2": (
        "Scénario 2 – Données financières",
        "Donne-moi le cours actuel d'Apple (AAPL) et du Bitcoin (BTC). "
        "Lequel a la plus forte variation aujourd'hui ?"
    ),
    "3": (
        "Scénario 3 – Calculs financiers multiples",
        "Je veux acheter un ordinateur portable (P001). "
        "Quel est son prix TTC avec la TVA à 20% ? "
        "Et quelle serait ma marge si je le revendais 1200€ ?"
    ),
    "4": (
        "Scénario 4 – Conversion de devises (API)",
        "Combien vaut 500 euros en dollars américains et en livres sterling ? "
        "Donne-moi les deux conversions."
    ),
    "5": (
        "Scénario 5 – Calcul de prêt + intérêts",
        "Je souhaite emprunter 150 000€ sur 20 ans à un taux de 4% par an. "
        "Quelle serait ma mensualité et combien paierais-je d'intérêts au total ? "
        "Si je place 20 000€ à 3% pendant 5 ans, quel capital j'obtiendrai-je ?"
    ),
    "6": (
        "Scénario 6 – Recommandation personnalisée",
        "Je suis un client Premium avec un budget de 400€. "
        "Je cherche du matériel informatique. "
        "Quels produits me recommanderais-tu ?"
    ),
    "7": (
        "Scénario 7 – Analyse de texte complète",
        "Résume ce texte : 'LangChain est un framework pour construire des "
        "applications intelligentes basées sur des modèles de langage.' "
        "Extrait ensuite les mots-clés et formate un rapport avec "
        "les champs Sujet:LangChain|Type:Résumé|Auteur:Agent."
    ),
    "8": (
        "Scénario 8 – Analyse financière complète (multi-outils)",
        "Analyse financière : "
        "1) Cours de Microsoft (MSFT) et d'Ethereum (ETH). "
        "2) Convertis 1000 USD en EUR. "
        "3) Si j'investis 5000€ à 7% pendant 10 ans, quel capital ?"
    ),
}

# Scénario C2 : 3 questions enchaînées qui nécessitent la mémoire
# Q1 → récupère le profil de Sophie Bernard (solde + type VIP)
# Q2 → recommande un produit en se souvenant qu'elle est VIP
# Q3 → calcule le prix TTC du produit recommandé ET vérifie si le solde suffit
SCENARIO_MEMOIRE = [
    (
        "C2 – Q1 : Profil client",
        "Donne-moi les informations du client Sophie Bernard : "
        "son solde de compte et son type de compte.",
    ),
    (
        "C2 – Q2 : Recommandation (contexte Q1)",
        "Quel produit informatique lui recommanderais-tu, "
        "en tenant compte de son profil ?",
    ),
    (
        "C2 – Q3 : Prix TTC + capacité d'achat (contexte Q1 + Q2)",
        "Calcule le prix TTC de ce produit avec la TVA à 20 %, "
        "et dis-moi si Sophie peut se le permettre avec son solde actuel.",
    ),
]


def afficher_menu():
    print("\n" + "="*60)
    print("        AGENT LANGCHAIN — MENU DES SCÉNARIOS")
    print("="*60)
    for num, (titre, _) in SCENARIOS.items():
        print(f"  {num}. {titre}")
    print("  9. Scénario 9 – Mémoire conversationnelle (3 questions liées)")
    print("  quit — Quitter")
    print("="*60)


if __name__ == "__main__":
    print("Initialisation de l'agent...")
    agent = creer_agent()
    print("Agent prêt.")

    while True:
        afficher_menu()
        choix = input("\nVotre choix : ").strip().lower()

        if choix in ("quit", "exit", "q"):
            print("\nAu revoir !")
            break
        elif choix == "9":
            print("\n>>> Scénario 9 – Démonstration de la mémoire conversationnelle")
            print("    L'agent répond à 3 questions liées ; chacune s'appuie sur les précédentes.")
            for titre, question in SCENARIO_MEMOIRE:
                input(f"\n  ↵  Appuyez sur Entrée pour poser la prochaine question ({titre})…")
                interroger_agent(agent, question)
        elif choix in SCENARIOS:
            titre, question = SCENARIOS[choix]
            print(f"\n>>> {titre}")
            interroger_agent(agent, question)
        else:
            print(f"\n  Choix invalide '{choix}'. Entrez un numéro entre 1 et 9, ou 'quit'.")



