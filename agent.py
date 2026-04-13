from dotenv import load_dotenv
load_dotenv()  # doit être appelé AVANT toute instanciation d'outil qui lit les variables d'env

from langchain_classic.tools import Tool
from langchain_tavily import TavilySearch
from langchain_experimental.tools import PythonREPLTool

# AVERTISSEMENT SÉCURITÉ : PythonREPLTool exécute du code Python arbitraire
# dans le processus courant, sans aucune isolation mémoire ou réseau.
# Risques : lecture/écriture de fichiers, exécution de commandes shell,
# boucles infinies, fuite de secrets présents en mémoire.
# Ne jamais exposer cet outil dans une API publique ou en production
# sans environnement sandbox dédié (Docker, gVisor, subprocess isolé…).
_python_repl = PythonREPLTool()
_python_repl.description = (
    'Exécute du code Python pour des calculs complexes ou traitements '
    'de données non couverts par les autres outils : statistiques avancées, '
    'tri et filtrage de listes, simulations, formatage de données, '
    'algorithmes personnalisés. '
    'Entrée : code Python valide sous forme de chaîne. '
    'Utiliser print() pour afficher les résultats.'
)
from tools.database import lister_tous_les_clients, rechercher_client, rechercher_produit
from tools.recommandation import recommander_produits
from tools.text import formater_rapport, extraire_mots_cles, convertir_majuscules_minuscules, resumer_texte
from tools.finance import obtenir_cours_action, obtenir_cours_crypto
from tools.api_publique import convertir_devise, obtenir_taux_du_jour
from tools.calculs import calculer_tva, calculer_interets_composes, calculer_marge, calculer_mensualite_pret
from tools.portefeuille import calculer_portefeuille

tools = [
     
     # ── Outil 1 : Base de données ─────────────────────────────────────
    
    Tool(name='rechercher_client', func=rechercher_client,
         description='Recherche un client par nom ou ID (ex: C001). '
                     'Retourne solde, type de compte, historique achats.'),
                     
    Tool(name='rechercher_produit', func=rechercher_produit,
         description='Recherche un produit par nom ou ID. '
                     'Retourne prix HT, TVA, prix TTC, stock.'),
                     
    # ── Outil 2 : Données financières ─────────────────────────────────
    
    Tool(name='cours_action', func=obtenir_cours_action,
         description='Cours boursier d\'une action. '
                     'Entrée : symbole majuscule ex AAPL, MSFT, TSLA, LVMH, AIR.'),
    
    Tool(name='cours_crypto', func=obtenir_cours_crypto,
         description='Cours d\'une crypto. '
                     'Entrée : symbole ex BTC, ETH, SOL, BNB, DOGE.'),

    # ── Outil 3 : Calculs financiers ──────────────────────────────────
    
    Tool(name='calculer_tva', func=calculer_tva,
         description='Calcule TVA et prix TTC. Entrée : prix_ht,taux ex 100,20.'),
    
    Tool(name='calculer_interets', func=calculer_interets_composes,
         description='Intérêts composés. Entrée : capital,taux_annuel,années ex 10000,5,3.'),
    
    Tool(name='calculer_marge', func=calculer_marge,
         description='Marge commerciale. Entrée : prix_vente,cout_achat ex 150,80.'),
    
    Tool(name='calculer_mensualite', func=calculer_mensualite_pret,
         description='Mensualité prêt. Entrée : capital,taux_annuel,mois ex 200000,3.5,240.'),

    # ── Outil 4 : API publique ────────────────────────────────────────
    
    Tool(name='convertir_devise', func=convertir_devise,
         description='Conversion de devises en temps réel (API Frankfurter). '
                     'Entrée : montant,DEV_SOURCE,DEV_CIBLE ex 100,USD,EUR.'),

    # ── Outil 5 : Transformation de texte ────────────────────────────
    
    Tool(name='resumer_texte', func=resumer_texte,
         description='Résume un texte et donne des statistiques. Entrée : texte complet.'),
    
    Tool(name='formater_rapport', func=formater_rapport,
         description='Formate en rapport. Entrée : Cle1:Val1|Cle2:Val2.'),
    
    Tool(name='extraire_mots_cles', func=extraire_mots_cles,
         description='Extrait les mots-clés d\'un texte. Entrée : texte complet.'),

    # ── Outil 6 : Recommandation ─────────────────────────────────────
    
    Tool(name='recommander_produits', func=recommander_produits,
         description='Recommandations produits. '
                     'Entrée : budget,categorie,type_compte ex 300,Informatique,Premium. '
                     'Catégories : Informatique, Mobilier, Audio, Toutes. '
                     'Types : Standard, Premium, VIP.'),

    # ── Outil 7 : Calcul de portefeuille boursier ────────────────────

    Tool(name='calculer_portefeuille', func=calculer_portefeuille,
         description=(
             'Calcule la valeur totale d\'un portefeuille boursier en temps réel via yfinance. '
             'Retourne valeur par ligne, valeur totale et variation du jour. '
             'Entrée : SYMBOLE:QUANTITE séparés par | '
             'ex AAPL:10|MSFT:5|BTC:0.5|AIR.PA:8'
         )),

    # ── Outil 8 : Python REPL ────────────────────────────────────────

    _python_repl,

    # ── Outil 9 : Recherche web (Tavily) ─────────────────────────────
    
    TavilySearch(
        max_results=5,
        name='recherche_web',
        description=(
            'Recherche web en temps réel via Tavily. '
            'Utiliser pour : actualités financières, résultats trimestriels, '
            'informations sur une entreprise, événements récents, '
            'tout sujet d\'actualité non couvert par les autres outils. '
            'Entrée : question ou mots-clés en langage naturel.'
        ),
    ),

]


def creer_agent():
    """
    Crée et retourne un agent LangChain avec mémoire conversationnelle.

    Utilise :
      - create_openai_tools_agent  : stratégie function-calling OpenAI
      - ConversationBufferMemory   : conserve l'intégralité de l'historique
      - ChatPromptTemplate         : prompt structuré avec slot chat_history
    """
    from langchain_openai import ChatOpenAI
    from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
    from langchain_classic.memory import ConversationBufferMemory
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    import os

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
    )

    # Prompt structuré : system → historique → question → scratchpad outils
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Tu es un assistant financier expert. "
            "Tu as accès à des outils pour interroger une base de données clients/produits, "
            "récupérer des cours boursiers en temps réel, effectuer des calculs financiers "
            "et faire des recherches web. "
            "Utilise toujours l'historique de la conversation pour résoudre les questions "
            "qui font référence à ce qui a été dit précédemment.",
        ),
        # Slot rempli automatiquement par ConversationBufferMemory
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        # Scratchpad interne : raisonnement + appels d'outils
        MessagesPlaceholder("agent_scratchpad"),
    ])

    # Mémoire tampon : conserve tous les échanges sous forme de messages
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,   # injecte des objets Message, pas des chaînes
    )

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )
    return agent_executor


def interroger_agent(agent, question: str):
    """Envoie une question à l'agent et affiche la réponse finale."""
    print(f"\n{'='*60}")
    print(f"Question : {question}")
    print('='*60)
    result = agent.invoke({"input": question})
    print(f"\nRéponse finale : {result['output']}")
    return result
