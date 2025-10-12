from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pathlib import Path
import shutil
import csv
import json
from typing import List, Dict, Any, Optional
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.models.workflow_models import Patient, PatientVisit
from datetime import datetime, timezone
import uuid

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / 'dataset' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


REQUIRED_COLUMNS = ["patient_id", "name", "dob"]


def parse_csv_preview(path: Path, mapping: Dict[str, str], max_rows: int = 10) -> Dict[str, Any]:
    headers: List[str] = []
    preview: List[Dict[str, Any]] = []
    row_errors: List[Dict[str, Any]] = []

    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        for idx, row in enumerate(reader):
            if idx >= max_rows:
                break
            canonical: Dict[str, Any] = {}
            for col in (mapping.keys() if mapping else headers):
                csv_header = mapping.get(col) if mapping else col
                canonical[col] = row.get(csv_header) if csv_header in row else row.get(col)

            missing = [c for c in REQUIRED_COLUMNS if not canonical.get(c)]
            if missing:
                row_errors.append({"row": idx + 1, "reason": f"missing {missing}"})

            preview.append(canonical)

    return {"headers": headers, "preview": preview, "row_errors": row_errors}


@router.post('/')
async def upload_dataset(file: UploadFile = File(...), mapping: Optional[str] = Form(None)):
    """
    Accept a CSV upload and optional mapping JSON. Returns a preview and any validation errors.
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail='Only CSV uploads are supported')

    dest = UPLOAD_DIR / file.filename
    try:
        with dest.open('wb') as f:
            shutil.copyfileobj(file.file, f)
    finally:
        await file.close()

    mapping_obj: Dict[str, str] = {}
    if mapping:
        try:
            mapping_obj = json.loads(mapping)
        except Exception:
            mapping_obj = {}

    parsed = parse_csv_preview(dest, mapping_obj)

    return {"filename": file.filename, **parsed}


@router.post('/import')
def import_uploaded_csv(filename: str = Form(...), mapping: Optional[str] = Form(None), dry_run: str = Form("false")):
    """
    Import a previously uploaded CSV into the DB. If dry_run is true, the transaction will be rolled back.
    Returns a simple report of inserted/updated/failed counts.
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail='Uploaded file not found')

    mapping_obj: Dict[str, str] = {}
    if mapping:
        try:
            mapping_obj = json.loads(mapping)
        except Exception:
            mapping_obj = {}

    # form fields can arrive as strings (e.g. 'false'/'true'); coerce to boolean
    dry_run_flag = False
    try:
        dry_run_flag = str(dry_run).lower() in ("true", "1", "yes")
    except Exception:
        dry_run_flag = False

    inserted = 0
    updated = 0
    failed: List[Dict[str, Any]] = []

    session: Optional[Session] = None
    try:
        session = SessionLocal()
        # use an explicit transaction
        with session.begin():
            with file_path.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    # build canonical row using mapping if provided
                    canonical: Dict[str, Any] = {}
                    for field in (list(mapping_obj.keys()) if mapping_obj else (row.keys())):
                        csv_header = mapping_obj.get(field) if mapping_obj else field
                        canonical[field] = row.get(csv_header) if csv_header in row else row.get(field)

                    # validate required columns
                    missing = [c for c in REQUIRED_COLUMNS if not canonical.get(c)]
                    if missing:
                        failed.append({'row': idx + 1, 'reason': f'missing {missing}'})
                        # collect failures but continue parsing to give a full report
                        continue

                    patient_identifier = canonical.get('patient_id') or f'P-{uuid.uuid4().hex[:8]}'
                    patient = session.query(Patient).filter(Patient.patient_id == patient_identifier).first()
                    if not patient:
                        patient = Patient(
                            patient_id=patient_identifier,
                            name=canonical.get('name'),
                            date_of_birth=(
                                None
                                if not canonical.get('dob')
                                else (datetime.strptime(canonical.get('dob'), '%Y-%m-%d') if '-' in canonical.get('dob') else None)
                            ),
                        )
                        session.add(patient)
                        # flush so patient.id is available for visits
                        session.flush()
                        inserted += 1
                    else:
                        if not patient.name and canonical.get('name'):
                            patient.name = canonical.get('name')
                            updated += 1

                    # create a PatientVisit referencing patient.id
                    visit = PatientVisit(
                        patient_id=patient.id,
                        visit_id=f'V{uuid.uuid4().hex[:8]}',
                        department='General',
                        appointment_type='Walk-in',
                        booking_type='Walk-in',
                        is_online_booking=False,
                        triage_category='Non-urgent',
                        reason_for_visit=canonical.get('diagnosis') or canonical.get('reason') or '',
                        appointment_time=datetime.now(timezone.utc),
                        actual_arrival_time=datetime.now(timezone.utc),
                        registration_time=datetime.now(timezone.utc),
                        check_in_time=datetime.now(timezone.utc),
                        first_seen_by_nurse_time=None,
                    )
                    session.add(visit)
                    inserted += 1

            # If dry_run, rollback the transaction and return the report
            if dry_run_flag:
                session.rollback()
                session.close()
                return {
                    'filename': filename,
                    'inserted': inserted,
                    'updated': updated,
                    'failed': failed,
                    'dry_run': True,
                }

            # If any failures occurred and this is not a dry run, rollback and return 400
            if failed:
                session.rollback()
                session.close()
                raise HTTPException(status_code=400, detail={
                    'filename': filename,
                    'inserted': inserted,
                    'updated': updated,
                    'failed': failed,
                    'dry_run': False,
                })

        # exiting the `with session.begin()` will commit
        if session is not None:
            session.close()

    except HTTPException:
        # Re-raise HTTP exceptions we created intentionally (e.g. validation failure -> 400)
        if session is not None:
            try:
                session.rollback()
            except Exception:
                pass
            try:
                session.close()
            except Exception:
                pass
        raise
    except Exception as e:
        if session is not None:
            try:
                session.rollback()
            except Exception:
                pass
            try:
                session.close()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f'Failed to import CSV: {e}')

    return {
        'filename': filename,
        'inserted': inserted,
        'updated': updated,
        'failed': failed,
        'dry_run': False,
    }
