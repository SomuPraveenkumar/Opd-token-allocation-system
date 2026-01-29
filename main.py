from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import heapq
import uuid
from datetime import datetime

app = FastAPI()

priority_map = {
    "emergency": 1,
    "paid": 2,
    "followup": 3,
    "online": 4,
    "walkin": 5
}

class BookRequest(BaseModel):
    doctor_id: int
    slot: str
    patient_type: str

class Patient:
    def __init__(self, priority, time, token_id, ptype):
        self.priority = priority
        self.time = time
        self.token_id = token_id
        self.ptype = ptype

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.time < other.time
        return self.priority < other.priority


doctors = {
    1: {
        "slots": ["9-10", "10-11", "11-12"],
        "data": {
            "9-10": {"limit": 3, "queue": []},
            "10-11": {"limit": 3, "queue": []},
            "11-12": {"limit": 3, "queue": []}
        }
    }
}


def try_add_patient(doc_id, start_index, patient):
    slots = doctors[doc_id]["slots"]
    data = doctors[doc_id]["data"]

    for i in range(start_index, len(slots)):
        slot = slots[i]
        queue = data[slot]["queue"]
        limit = data[slot]["limit"]

        if len(queue) < limit:
            heapq.heappush(queue, patient)
            return True

        last = max(queue, key=lambda x: (x.priority, x.time))
        queue.remove(last)
        heapq.heapify(queue)

        heapq.heappush(queue, patient)
        patient = last

    return False


@app.post("/book")
def book(req: BookRequest):
    if req.patient_type not in priority_map:
        raise HTTPException(400, "invalid patient type")

    if req.doctor_id not in doctors:
        raise HTTPException(404, "doctor not found")

    doctor = doctors[req.doctor_id]

    if req.slot not in doctor["slots"]:
        raise HTTPException(404, "slot not found")

    patient = Patient(
        priority_map[req.patient_type],
        datetime.now().timestamp(),
        str(uuid.uuid4()),
        req.patient_type
    )

    index = doctor["slots"].index(req.slot)

    ok = try_add_patient(req.doctor_id, index, patient)

    if not ok:
        return {"message": "no slot available today"}

    return {
        "message": "token booked",
        "token_id": patient.token_id
    }


@app.get("/status")
def status():
    output = {}

    for d_id, doc in doctors.items():
        output[d_id] = {}

        for slot in doc["slots"]:
            q = doc["data"][slot]["queue"]
            output[d_id][slot] = [
                {
                    "token_id": p.token_id,
                    "type": p.ptype
                }
                for p in sorted(q)
            ]

    return output
