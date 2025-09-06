from dataclasses import dataclass
from typing import Literal
import uuid


Decision = Literal["pending", "approved", "rejected"]


@dataclass
class HITLRequest:
    id: str
    action: str
    context: dict
    decision: Decision = "pending"




class HITLApproval:
    def __init__(self):
        self._store: dict[str, HITLRequest] = {}


    def create(self, action: str, context: dict) -> HITLRequest:
        rid = str(uuid.uuid4())
        req = HITLRequest(id=rid, action=action, context=context)
        self._store[rid] = req
        return req


    def decide(self, rid: str, decision: Decision):
        if rid not in self._store:
            raise KeyError("not found")
        self._store[rid].decision = decision
        return self._store[rid]


    def get(self, rid: str) -> HITLRequest:
        if rid not in self._store:
            raise KeyError("not found")
        return self._store[rid]


hitl = HITLApproval()