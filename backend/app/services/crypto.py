import hashlib
import json
from models import SensorReading
from database import get_db

GENESIS_HASH = "GENESIS"

def compute_entry_hash(sensor_id: str, value: float, timestamp, previous_hash: str):
    
    """
    Deterministically hash a reading's core fields plus the previous hash.
    sort_keys=True ensures identical output regardless of dict insertion order.
    """

    payload = {
        "sensor_id": sensor_id,
        "value": value,
        "timestamp": timestamp.isoformat(),
        "previous_hash": previous_hash
    }

    seralised = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(seralised.encode()).hexdigest()

def get_last_hash(db_session) -> str:
    
    """
    Fetch the entry_hash of the most recently written row.
    Returns GENESIS if the table is empty — that's the anchor of the chain.
    """

    last = (
        db_session.query(SensorReading)
        .order_by(SensorReading.id.desc())
        .first()
    )
    if last is None or last.entry_hash is None:
        return GENESIS_HASH
    return last.entry_hash

def verify_chain(db_session) -> list[dict]:

    """
    Walk every row in insertion order and check:
      1. The stored entry_hash matches a fresh recomputation
      2. The previous_hash links correctly to the row before it

    Returns a list of result dicts — one per row — so the API
    can return structured JSON rather than just pass/fail.
    """
    readings = (
        db_session.query(SensorReading)
        .order_by(SensorReading.id.asc())
        .all()
    )

    results = []
    previous_hash = GENESIS_HASH

    for i, row in enumerate(readings):
        recomputed = compute_entry_hash(
            row.sensor_id, row.value, row.timestamp, row.previous_hash
        )
    
        hash_ok = (row.entry_hash == recomputed)
        chain_ok = (row.previous_hash == previous_hash)

        results.append({
            "row_id": row.id,
            "sensor_id": row.sensor_id,
            "timestamp": row.timestamp.isoformat(),
            "hash_ok": hash_ok,
            "chain_ok": chain_ok,
            "status": "OK" if hash_ok and chain_ok else "TAMPERED"
        })

        previous_hash = row.entry_hash

    return results

