from fastapi import APIRouter, HTTPException
from typing import List, Dict
import csv
from pathlib import Path

router = APIRouter()

DATA_PATH = Path(__file__).resolve().parents[2] / 'dataset' / 'patient_history.csv'


def _read_csv_rows() -> List[Dict[str, str]]:
    rows = []
    if not DATA_PATH.exists():
        return rows
    with DATA_PATH.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


@router.get('/{patient_id}')
def get_patient_history(patient_id: str):
    """Return patient history rows that match a given patient_id (exact match)."""
    rows = _read_csv_rows()
    matched = [r for r in rows if r.get('patient_id') == patient_id]
    if not matched:
        raise HTTPException(status_code=404, detail='Patient history not found')

    # Return all matched records (could be multiple visits)
    return matched
