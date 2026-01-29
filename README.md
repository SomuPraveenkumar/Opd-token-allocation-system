# OPD Token Allocation System

## Overview
This project implements a backend system for hospital OPD token allocation. 
Doctors operate in fixed time slots with limited capacity, and patients arrive from multiple sources such as walk-ins and emergency cases.

The system dynamically allocates and reallocates tokens based on patient priority and slot availability, simulating real hospital workflows.

---

## Features
- Fixed time-slot based OPD scheduling
- Hard capacity limits per slot
- Priority-based token allocation
- Emergency handling
- Automatic patient shifting to future slots
- REST API-based backend service
- Real-life OPD day simulation

---

## Patient Priority Order
1. Emergency  
2. Paid  
3. Follow-up  
4. Online  
5. Walk-in  

Higher-priority patients are always handled earlier.

---

## Core Logic
- If a requested slot has available capacity, the token is assigned.
- If the slot is full, the lowest-priority patient is moved to the next available slot.
- This reallocation continues until a free slot is found.
- If all slots are full, the system returns a no-availability response.

This ensures fairness and realistic OPD operation.

---

## API Endpoints

### POST /book
Used to book an OPD token.

Example request:
```json
{
  "doctor_id": 1,
  "slot": "9-10",
  "patient_type": "walkin"
}
