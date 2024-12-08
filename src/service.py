from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from db.datamodel import  AgentCreate, AgentUpdate, AgentResponse
from db.sql import Agent
from db import get_db

app = FastAPI()

@app.post("/agents/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = Agent(name=agent.name, status=agent.status, started_at=datetime.now())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.put("/agents/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent: AgentUpdate, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    db_agent.status = agent.status
    db_agent.completed_at = agent.completed_at if agent.completed_at else db_agent.completed_at
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@app.get("/agents/{agent_id}/history")
def get_agent_history(agent_id: int, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"steps": db_agent.steps, "status": db_agent.status}
