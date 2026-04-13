"""
API REST — Agent d'analyse de portefeuille financier.

Endpoints :
  POST /api/agent/query          → question en langage naturel → réponse JSON
  GET  /api/portfolio/positions  → liste brute des positions
  GET  /api/portfolio/resume     → résumé global du portefeuille
  GET  /api/portfolio/risque     → analyse de risque
  GET  /health                   → statut du service
"""
import os
import time
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── Schémas Pydantic ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    verbose: Optional[bool] = False


class QueryResponse(BaseModel):
    question: str
    reponse: str
    duree_ms: int
    statut: str


class PositionOut(BaseModel):
    symbole: str
    nom: str
    type_actif: str
    secteur: str | None
    quantite: float
    prix_achat: float
    prix_actuel: float
    valeur_marche: float
    gain_pct: float
    beta: float


# ── Application FastAPI ───────────────────────────────────────────────────────

app = FastAPI(
    title="Agent Analyse Portefeuille",
    description="API REST propulsée par un agent LangChain ReAct.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Création de l'agent (chargé une seule fois au démarrage) ──────────────────

def _creer_agent_portefeuille():
    from langchain_openai import ChatOpenAI
    from langchain_classic.tools import Tool
    from langchain_classic.agents import AgentExecutor, create_react_agent
    from langchain_classic import hub
    from tools.portfolio import (
        lister_positions,
        resumer_portefeuille,
        analyser_risque,
        performance_actif,
        top_performances,
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    portfolio_tools = [
        Tool(
            name="lister_positions",
            func=lister_positions,
            description=(
                "Liste toutes les positions du portefeuille avec leur valorisation, "
                "P&L et poids. Utiliser pour obtenir une vue d'ensemble."
            ),
        ),
        Tool(
            name="resumer_portefeuille",
            func=resumer_portefeuille,
            description=(
                "Résumé global du portefeuille : valeur totale, capital investi, "
                "gain total, répartition par type d'actif et par secteur."
            ),
        ),
        Tool(
            name="analyser_risque",
            func=analyser_risque,
            description=(
                "Analyse de risque : beta pondéré, volatilité, actifs les plus risqués, "
                "concentration (HHI), alertes. "
                "Utiliser pour : 'actifs risqués', 'diversification', 'beta du portefeuille'."
            ),
        ),
        Tool(
            name="performance_actif",
            func=performance_actif,
            description=(
                "Performance détaillée d'un actif spécifique : P&L, historique 30j, "
                "plus haut/bas. Entrée : symbole ex AAPL, BTC, TSLA, AIR.PA."
            ),
        ),
        Tool(
            name="top_performances",
            func=top_performances,
            description=(
                "Classement des meilleurs et pires actifs du portefeuille par performance (%)."
            ),
        ),
    ]

    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=portfolio_tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=portfolio_tools,
        verbose=False,
        max_iterations=8,
        handle_parsing_errors=True,
    )


_agent_instance = None


def _get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = _creer_agent_portefeuille()
    return _agent_instance


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Vérifie que le service est opérationnel."""
    db_ok = os.path.exists(
        os.path.join(os.path.dirname(__file__), "portfolio.db")
    )
    return {
        "statut": "ok",
        "service": "agent-portefeuille",
        "portfolio_db": "présente" if db_ok else "MANQUANTE — lancez init_portfolio_db.py",
        "openai_key": "configurée" if os.getenv("OPENAI_API_KEY") else "MANQUANTE",
    }


@app.post("/api/agent/query", response_model=QueryResponse)
def query_agent(req: QueryRequest):
    """
    Envoie une question en langage naturel à l'agent.
    L'agent utilise ses outils pour interroger le portefeuille et formuler une réponse.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Le champ 'question' ne peut pas être vide.")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY non configurée dans .env.")

    t0 = time.time()
    try:
        agent = _get_agent()
        result = agent.invoke({"input": req.question})
        reponse = result.get("output", "Aucune réponse générée.")
        statut = "ok"
    except Exception as e:
        reponse = f"Erreur lors de l'exécution de l'agent : {e}"
        statut = "erreur"

    duree_ms = int((time.time() - t0) * 1000)
    return QueryResponse(
        question=req.question,
        reponse=reponse,
        duree_ms=duree_ms,
        statut=statut,
    )


@app.get("/api/portfolio/positions")
def get_positions():
    """Retourne la liste brute des positions depuis la base de données."""
    db_path = os.path.join(os.path.dirname(__file__), "portfolio.db")
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=503,
            detail="portfolio.db introuvable. Lancez : python init_portfolio_db.py"
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM positions ORDER BY type_actif, symbole").fetchall()
    conn.close()

    positions = []
    for r in rows:
        val = r["quantite"] * r["prix_actuel"]
        inv = r["quantite"] * r["prix_achat"]
        gain = (val - inv) / inv * 100 if inv else 0
        positions.append(PositionOut(
            symbole=r["symbole"],
            nom=r["nom"],
            type_actif=r["type_actif"],
            secteur=r["secteur"],
            quantite=r["quantite"],
            prix_achat=r["prix_achat"],
            prix_actuel=r["prix_actuel"],
            valeur_marche=round(val, 2),
            gain_pct=round(gain, 2),
            beta=r["beta"],
        ))
    return {"positions": positions, "total": len(positions)}


@app.get("/api/portfolio/resume")
def get_resume():
    """Retourne le résumé calculé du portefeuille."""
    from tools.portfolio import resumer_portefeuille
    return {"resume": resumer_portefeuille()}


@app.get("/api/portfolio/risque")
def get_risque():
    """Retourne l'analyse de risque du portefeuille."""
    from tools.portfolio import analyser_risque
    return {"risque": analyser_risque()}
