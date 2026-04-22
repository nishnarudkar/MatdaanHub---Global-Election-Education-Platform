from pydantic import BaseModel, Field
from typing import List, Optional

class TimelinePhase(BaseModel):
    phase: str
    days: str
    description: str

class VotingStep(BaseModel):
    icon: str
    title: str
    detail: str

class ElectionProfile(BaseModel):
    name: str
    flag: str
    system: str
    body: str
    frequency: str
    voters: str
    color: str
    description: str
    timeline: List[TimelinePhase]
    steps: List[VotingStep]
    facts: List[str]

class GlossaryTerm(BaseModel):
    term: str
    definition: str
