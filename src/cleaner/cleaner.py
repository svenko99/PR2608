from __future__ import annotations

import csv
import re
from pathlib import Path

from models import ListingChange, PaymentType, StudentListing


class Cleaner:
    CSV_FILE = Path("../data/data.csv")
    CHANGES_CSV_FILE = Path("../data/changes.csv")

    def run(
            self,
            raw_listings: list[StudentListing],
            csv_path: Path | None = None,
            changes_csv_path: Path | None = None,
    ) -> tuple[list[StudentListing], list[ListingChange], int]:
        """Očisti surove listinge in posodobi CSV bazo."""
        csv_path = csv_path or self.CSV_FILE
        changes_csv_path = changes_csv_path or self.CHANGES_CSV_FILE

        cleaned_listings = [self._clean_listing(listing) for listing in raw_listings]

        changes, new_count = self._update_csv_database(
            cleaned_listings, csv_path, changes_csv_path,
        )

        return cleaned_listings, changes, new_count

    def _clean_listing(self, listing: StudentListing) -> StudentListing:
        """Normalizira polja listinga."""
        listing.normalized_payment_type = self._parse_payment_type(listing.payment_type)
        return listing

    # ── Normalizacija ────────────────────────────────────────────────

    @staticmethod
    def _parse_payment_type(value: str | None) -> PaymentType | None:
        if not value:
            return None

        normalized = re.sub(r"\s+", " ", value).strip().upper()
        if "/H" in normalized or "€/H" in normalized:
            return PaymentType.HOURLY
        if "DOGOVOR" in normalized:
            return PaymentType.NEGOTIABLE
        if "PROJEKT" in normalized:
            return PaymentType.PROJECT
        if "DOGODEK" in normalized:
            return PaymentType.PER_EVENT
        if "IZLET" in normalized:
            return PaymentType.PER_TRIP
        return PaymentType.OTHER

    # ── CSV operacije ────────────────────────────────────────────────

    def _update_csv_database(
            self,
            current_listings: list[StudentListing],
            csv_path: Path,
            changes_csv_path: Path,
    ) -> tuple[list[ListingChange], int]:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        changes_csv_path.parent.mkdir(parents=True, exist_ok=True)

        existing = {}
        if csv_path.exists():
            with csv_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    listing = StudentListing.from_csv_row(row)
                    existing[listing.id] = listing

        changes: list[ListingChange] = []
        new_count = 0

        for listing in current_listings:
            old_listing = existing.get(listing.id)
            if old_listing is not None:
                changes.extend(self._build_listing_changes(old_listing, listing))
                listing.first_seen = old_listing.first_seen
            else:
                new_count += 1

            existing[listing.id] = listing

        self._write_csv(csv_path, existing)
        self._append_changes_csv(changes_csv_path, changes)

        return changes, new_count

    def _write_csv(self, csv_path: Path, listings_by_id: dict[int, StudentListing]) -> None:
        rows = [listing.to_csv_row() for listing in sorted(listings_by_id.values(), key=lambda x: x.id)]
        if not rows:
            return

        fieldnames = list(rows[0].keys())
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _append_changes_csv(self, csv_path: Path, changes: list[ListingChange]) -> None:
        file_exists = csv_path.exists()

        with csv_path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ListingChange.csv_fieldnames())
            if not file_exists:
                writer.writeheader()
            if changes:
                writer.writerows(change.to_csv_row() for change in changes)

    def _build_listing_changes(
            self,
            old_listing: StudentListing,
            new_listing: StudentListing,
    ) -> list[ListingChange]:
        changes: list[ListingChange] = []

        for field_name in StudentListing.comparable_fields():
            old_value = getattr(old_listing, field_name)
            new_value = getattr(new_listing, field_name)
            if old_value == new_value:
                continue

            changes.append(
                ListingChange(
                    listing_id=new_listing.id,
                    changed_at=new_listing.last_seen,
                    field=field_name,
                    old_value=StudentListing.serialize_value(old_value),
                    new_value=StudentListing.serialize_value(new_value),
                )
            )

        return changes
