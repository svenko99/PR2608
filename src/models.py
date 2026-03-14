from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class WorkSchedule(Enum):
    BY_AGREEMENT = "PO DOGOVORU"
    MORNING = "DOPOLDAN"
    SHIFT = "IZMENSKO"
    AFTERNOON = "POPOLDAN"
    WEEKENDS = "MED VIKENDI"


class PaymentType(Enum):
    HOURLY = "HOURLY"
    NEGOTIABLE = "NEGOTIABLE"
    PROJECT = "PROJECT"
    PER_EVENT = "PER_EVENT"
    PER_TRIP = "PER_TRIP"
    OTHER = "OTHER"


@dataclass
class StudentListing:
    id: int
    title: str
    subtitle: str | None
    company: str
    location: str | None
    sublocation: str | None

    hourly_rate_neto: float | None
    hourly_rate_bruto: float | None
    hourly_rate_from: str | None
    payment_type: PaymentType | None

    description: str | None
    open_positions: int | None
    duration: str | None
    work_schedule: WorkSchedule | None
    start_date: date | None

    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    contact_webpage: str | None

    first_seen: datetime
    last_seen: datetime

    def to_csv_row(self) -> dict[str, str]:
        return {
            "id": str(self.id),
            "title": self.title,
            "subtitle": self.subtitle or "",
            "company": self.company,
            "location": self.location or "",
            "sublocation": self.sublocation or "",
            "hourly_rate_neto": "" if self.hourly_rate_neto is None else str(self.hourly_rate_neto),
            "hourly_rate_bruto": "" if self.hourly_rate_bruto is None else str(self.hourly_rate_bruto),
            "hourly_rate_from": self.hourly_rate_from or "",
            "payment_type": self.payment_type.value if self.payment_type else "",
            "description": self.description or "",
            "open_positions": "" if self.open_positions is None else str(self.open_positions),
            "duration": self.duration or "",
            "work_schedule": self.work_schedule.value if self.work_schedule else "",
            "start_date": self.start_date.isoformat() if self.start_date else "",
            "contact_name": self.contact_name or "",
            "contact_phone": self.contact_phone or "",
            "contact_email": self.contact_email or "",
            "contact_webpage": self.contact_webpage or "",
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
        }

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "StudentListing":
        work_schedule_raw = row.get("work_schedule", "").strip()
        work_schedule = WorkSchedule(work_schedule_raw) if work_schedule_raw else None

        payment_type_raw = row.get("payment_type", "").strip()
        payment_type = PaymentType(payment_type_raw) if payment_type_raw else None

        start_date_raw = row.get("start_date", "").strip()
        start_date = date.fromisoformat(start_date_raw) if start_date_raw else None

        return cls(
            id=int(row["id"]),
            title=row["title"],
            subtitle=row["subtitle"] or None,
            company=row["company"],
            location=row["location"] or None,
            sublocation=row["sublocation"] or None,
            hourly_rate_neto=float(row["hourly_rate_neto"]) if row["hourly_rate_neto"] else None,
            hourly_rate_bruto=float(row["hourly_rate_bruto"]) if row["hourly_rate_bruto"] else None,
            hourly_rate_from=row["hourly_rate_from"] or None,
            payment_type=payment_type,
            description=row["description"] or None,
            open_positions=int(row["open_positions"]) if row["open_positions"] else None,
            duration=row["duration"] or None,
            work_schedule=work_schedule,
            start_date=start_date,
            contact_name=row["contact_name"] or None,
            contact_phone=row["contact_phone"] or None,
            contact_email=row["contact_email"] or None,
            contact_webpage=row["contact_webpage"] or None,
            first_seen=datetime.fromisoformat(row["first_seen"]),
            last_seen=datetime.fromisoformat(row["last_seen"]),
        )

    def to_history_row(self) -> dict[str, str]:
        return {
            "listing_id": str(self.id),
            "seen_at": self.last_seen.isoformat(),
            "title": self.title,
            "subtitle": self.subtitle or "",
            "company": self.company,
            "location": self.location or "",
            "sublocation": self.sublocation or "",
            "hourly_rate_neto": "" if self.hourly_rate_neto is None else str(self.hourly_rate_neto),
            "hourly_rate_bruto": "" if self.hourly_rate_bruto is None else str(self.hourly_rate_bruto),
            "hourly_rate_from": self.hourly_rate_from or "",
            "payment_type": self.payment_type.value if self.payment_type else "",
            "description": self.description or "",
            "open_positions": "" if self.open_positions is None else str(self.open_positions),
            "duration": self.duration or "",
            "work_schedule": self.work_schedule.value if self.work_schedule else "",
            "start_date": self.start_date.isoformat() if self.start_date else "",
            "contact_name": self.contact_name or "",
            "contact_phone": self.contact_phone or "",
            "contact_email": self.contact_email or "",
            "contact_webpage": self.contact_webpage or "",
        }
