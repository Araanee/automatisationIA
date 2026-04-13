"""
Interface web Streamlit pour l'agent LangChain.
Lancement : streamlit run app.py
"""
import os
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Configuration de la page ──────────────────────────────────────────────────

st.set_page_config(
    page_title="Agent IA – Automatisation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Bulle utilisateur */
    .msg-user {
        background: #1e3a5f;
        color: #e8f0fe;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin: 8px 0 8px 15%;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    /* Bulle agent */
    .msg-agent {
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin: 8px 15% 8px 0;
        font-size: 0.95rem;
        line-height: 1.5;
        border-left: 3px solid #89b4fa;
    }
    /* Chip durée */
    .chip {
        display: inline-block;
        background: #313244;
        color: #a6adc8;
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 999px;
        margin-top: 4px;
    }
    /* Titre sidebar */
    .sidebar-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6c7086;
        margin-bottom: 6px;
    }
    /* Badge outil */
    .tool-badge {
        background: #181825;
        border: 1px solid #313244;
        border-radius: 8px;
        padding: 6px 10px;
        margin-bottom: 5px;
        font-size: 0.82rem;
        color: #cdd6f4;
    }
    .tool-badge b { color: #89b4fa; }
</style>
""", unsafe_allow_html=True)

# ── Initialisation de l'état de session ───────────────────────────────────────

if "historique" not in st.session_state:
    st.session_state.historique = []          # liste de dict {role, contenu, duree_ms}

if "agent" not in st.session_state:
    st.session_state.agent = None

if "agent_erreur" not in st.session_state:
    st.session_state.agent_erreur = None

# ── Chargement de l'agent ─────────────────────────────────────────────────────
# L'agent est stocké dans st.session_state (PAS dans st.cache_resource) afin
# que chaque session navigateur possède sa propre ConversationBufferMemory.
# Un cache global partagerait la mémoire entre tous les utilisateurs connectés.

def get_agent():
    if st.session_state.agent is None:
        with st.spinner("Initialisation de l'agent…"):
            try:
                from agent import creer_agent
                st.session_state.agent = creer_agent()
                st.session_state.agent_erreur = None
            except Exception as e:
                st.session_state.agent_erreur = str(e)
    return st.session_state.agent


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=40)
    st.title("Agent LangChain")
    st.caption("Propulsé par GPT-4o-mini · ReAct")

    st.divider()

    # Bouton reset
    if st.button("🔄  Nouvelle conversation", use_container_width=True, type="primary"):
        st.session_state.historique = []
        st.rerun()

    st.divider()

    # Liste des outils
    st.markdown('<p class="sidebar-title">Outils disponibles</p>', unsafe_allow_html=True)

    # Définition statique pour ne pas dépendre du chargement de l'agent
    OUTILS = [
        ("🗄️",  "Base de données",        "Clients & produits SQLite"),
        ("📈",  "Cours boursiers",         "Actions en temps réel (yfinance)"),
        ("₿",   "Cours crypto",            "BTC, ETH, SOL… (yfinance)"),
        ("🧮",  "Calculs financiers",      "TVA, intérêts, marge, prêt"),
        ("💱",  "Conversion de devises",   "API Frankfurter temps réel"),
        ("📝",  "Traitement de texte",     "Résumé, mots-clés, rapport"),
        ("🎯",  "Recommandation",          "Produits par budget & profil"),
        ("💼",  "Portefeuille boursier",   "Valorisation multi-actifs"),
        ("🐍",  "Python REPL",             "Code arbitraire & stats"),
        ("🔍",  "Recherche web",           "Tavily — actualités & infos"),
    ]

    for icone, nom, desc in OUTILS:
        st.markdown(
            f'<div class="tool-badge">{icone} <b>{nom}</b><br>'
            f'<span style="color:#6c7086;font-size:0.78rem">{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Statut de la clé API
    openai_ok = bool(os.getenv("OPENAI_API_KEY"))
    tavily_ok = bool(os.getenv("TAVILY_API_KEY") and
                     os.getenv("TAVILY_API_KEY") != "tvly-REMPLACEZ_PAR_VOTRE_CLE_TAVILY")

    st.markdown('<p class="sidebar-title">Statut des clés API</p>', unsafe_allow_html=True)
    st.markdown(f"{'✅' if openai_ok else '❌'} OpenAI")
    st.markdown(f"{'✅' if tavily_ok else '⚠️'} Tavily (recherche web)")

    st.divider()
    st.caption("ℹ️ Les messages Python REPL s'exécutent localement.")


# ── Zone principale ───────────────────────────────────────────────────────────

st.markdown("## 🤖 Agent IA – Automatisation financière")
st.caption(
    "Posez vos questions sur les clients, produits, cours boursiers, calculs financiers "
    "ou demandez une analyse de portefeuille."
)

# Message de bienvenue si historique vide
if not st.session_state.historique:
    st.info(
        "💡 **Exemples de questions**\n\n"
        "- *Quelles sont les informations du client Marie Dupont ?*\n"
        "- *Donne-moi le cours actuel d'Apple et de Bitcoin*\n"
        "- *Calcule la valeur du portefeuille AAPL:10|MSFT:5|BTC:0.5*\n"
        "- *Je veux emprunter 200 000 € sur 20 ans à 3,5 %, quelle est ma mensualité ?*\n"
        "- *Quelles actualités récentes sur LVMH ?*",
        icon="💬",
    )

# Affichage de l'historique
for msg in st.session_state.historique:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-user">👤 {msg["contenu"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        duree = f'<span class="chip">⏱ {msg.get("duree_ms", 0) / 1000:.1f}s</span>'
        st.markdown(
            f'<div class="msg-agent">🤖 {msg["contenu"]}<br>{duree}</div>',
            unsafe_allow_html=True,
        )

# ── Saisie utilisateur ────────────────────────────────────────────────────────

question = st.chat_input("Posez votre question à l'agent…")

if question:
    # Ajout de la question à l'historique
    st.session_state.historique.append({"role": "user", "contenu": question})

    if not os.getenv("OPENAI_API_KEY"):
        st.session_state.historique.append({
            "role": "agent",
            "contenu": "⚠️ **OPENAI_API_KEY** manquante dans le fichier `.env`.",
            "duree_ms": 0,
        })
        st.rerun()

    # Appel à l'agent avec indicateur de chargement
    agent = get_agent()

    if agent is None:
        reponse = f"❌ Impossible de charger l'agent : {st.session_state.agent_erreur}"
        duree_ms = 0
    else:
        with st.spinner("L'agent réfléchit…"):
            t0 = time.time()
            try:
                result = agent.invoke({"input": question})
                reponse = result.get("output", "Aucune réponse générée.")
            except Exception as e:
                reponse = f"❌ Erreur lors de l'exécution : {e}"
            duree_ms = int((time.time() - t0) * 1000)

    st.session_state.historique.append({
        "role": "agent",
        "contenu": reponse,
        "duree_ms": duree_ms,
    })

    st.rerun()
