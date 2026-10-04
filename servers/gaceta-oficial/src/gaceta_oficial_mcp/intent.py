"""Interpretación determinista de expresiones de fecha en español."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from .parsers import MESES

TZ = ZoneInfo("America/Havana")


def today() -> date:
    from datetime import datetime

    return datetime.now(TZ).date()


@dataclass(frozen=True)
class Period:
    start: date
    end: date
    label: str

    @property
    def months(self) -> list[tuple[int, int]]:
        """Pares (mes base cero, año) que cubre el periodo, del más reciente al más antiguo."""
        out, y, m = [], self.end.year, self.end.month
        while (y, m) >= (self.start.year, self.start.month):
            out.append((m - 1, y))
            y, m = (y, m - 1) if m > 1 else (y - 1, 12)
        return out


def _month_range(y: int, m: int) -> tuple[date, date]:
    start = date(y, m, 1)
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    return start, nxt - timedelta(days=1)


def parse_period(expr: str | None, ref: date | None = None) -> Period:
    """'hoy', 'ayer', 'esta semana', 'este mes', 'mes pasado', 'octubre 2025', '2026-10-02', '02/10/2026'."""
    ref = ref or today()
    e = (expr or "hoy").strip().lower()
    if e in ("hoy", "ahora", "actual"):
        return Period(ref, ref, "hoy")
    if e == "ayer":
        d = ref - timedelta(days=1)
        return Period(d, d, "ayer")
    if e in ("esta semana", "semana", "semana actual"):
        return Period(ref - timedelta(days=ref.weekday()), ref, "esta semana")
    if e in ("este mes", "mes actual", "mes"):
        s, en = _month_range(ref.year, ref.month)
        return Period(s, min(en, ref), "este mes")
    if e in ("mes pasado", "mes anterior"):
        y, m = (ref.year, ref.month - 1) if ref.month > 1 else (ref.year - 1, 12)
        return Period(*_month_range(y, m), "mes pasado")
    if m := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", e):
        d = date(int(m[1]), int(m[2]), int(m[3]))
        return Period(d, d, e)
    if m := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", e):
        d = date(int(m[3]), int(m[2]), int(m[1]))
        return Period(d, d, e)
    if m := re.fullmatch(r"(\d{4})-(\d{2})", e):
        return Period(*_month_range(int(m[1]), int(m[2])), e)
    m = re.fullmatch(r"([a-záéíóú]+)(?:\s+de)?(?:\s+(\d{4}))?", e)
    if m and m[1] in MESES:
        return Period(*_month_range(int(m[2] or ref.year), MESES[m[1]]), e)
    if re.fullmatch(r"\d{4}", e):
        return Period(date(int(e), 1, 1), date(int(e), 12, 31), e)
    raise ValueError(f"No entiendo la fecha '{expr}'. Usa 'hoy', 'ayer', 'este mes', 'octubre 2025' o AAAA-MM-DD.")
