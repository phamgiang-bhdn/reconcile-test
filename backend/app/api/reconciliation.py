from fastapi import APIRouter, Query, Response

from app.db import pool
from app.domain.reconciliation import logic
from app.errors import AppError
from app.exports.reconciliation_export import build_workbook_bytes
from app.repositories.reconciliation_repo import ReconciliationRepo

router = APIRouter(tags=["reconciliation"])

XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _validate_status(status: str | None) -> None:
    if status is not None and status not in logic.ALL_STATUSES:
        raise AppError("INVALID_INPUT", f"unknown status: {status}")


def _fetch_rows(status: str | None) -> list[dict]:
    with pool.connection() as conn:
        repo = ReconciliationRepo(conn)
        rows = logic.reconcile(repo.fetch_orders(), repo.fetch_settlements())
    return [r for r in rows if r["reconcile_status"] == status] if status else rows


@router.get("/reconciliation")
def list_reconciliation(status: str | None = Query(default=None)):
    _validate_status(status)
    rows = _fetch_rows(status)
    return {"data": rows, "meta": {"size": len(rows), "total": len(rows)}}


@router.get("/reconciliation/export")
def export_reconciliation(status: str | None = Query(default=None)):
    _validate_status(status)
    rows = _fetch_rows(status)
    with pool.connection() as conn:
        repo = ReconciliationRepo(conn)
        kpi = logic.compute_kpi(repo.fetch_orders(), repo.fetch_settlements())
    content = build_workbook_bytes(rows, kpi)
    return Response(
        content=content,
        media_type=XLSX_MEDIA,
        headers={"Content-Disposition": 'attachment; filename="reconciliation.xlsx"'},
    )


@router.get("/kpi")
def get_kpi():
    with pool.connection() as conn:
        repo = ReconciliationRepo(conn)
        kpi = logic.compute_kpi(repo.fetch_orders(), repo.fetch_settlements())
    return {"data": kpi}
