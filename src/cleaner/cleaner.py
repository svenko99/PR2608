from __future__ import annotations

import csv
import re
from pathlib import Path

from models import ListingChange, PaymentType, StudentListing


class Cleaner:
    CSV_FILE = Path("../data/data.csv")
    CHANGES_CSV_FILE = Path("../data/changes.csv")
    NASELJA_CSV = Path("../data/naselja.csv")

    def __init__(self, naselja_csv_path: Path | None = None) -> None:
        self._naselja, self._naselja_regija, self._obcine_regija = self._load_naselja(
            naselja_csv_path or self.NASELJA_CSV,
        )

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
        city, region = self._parse_location(listing.location)
        listing.normalized_city = city
        listing.normalized_region = region
        return listing

    # Normalizacija

    @staticmethod
    def _load_naselja(csv_path: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
        """Naloži naselja.csv in vrne (naselje→naselje, naselje→regija, občina→regija) lookup."""
        naselja: dict[str, str] = {}
        naselja_regija: dict[str, str] = {}
        obcine_regija: dict[str, str] = {}
        if not csv_path.exists():
            return naselja, naselja_regija, obcine_regija

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["naselje"].strip().upper()
                obcina = row["obcina"].strip().upper()
                regija = row["regija"].strip()
                naselja[name] = name
                naselja_regija[name] = regija

                # Občina → regija lookup
                if obcina and obcina not in obcine_regija:
                    obcine_regija[obcina] = regija

                # Dvojezična imena: "KOPER/CAPODISTRIA" → dodaj tudi "KOPER"
                if "/" in name:
                    short = name.split("/")[0].strip()
                    naselja[short] = name
                    naselja_regija[short] = regija

        return naselja, naselja_regija, obcine_regija

    def _parse_location(self, value: str | None) -> tuple[str | None, str | None]:
        """Iz surovega location stringa izvleče normalized_city in normalized_region."""
        if not value:
            return None, None

        normalized = re.sub(r"\s+", " ", value).strip().upper()

        # "OD DOMA" in variante niso mesto
        if normalized in {"OD DOMA", "DELO OD DOMA", "DELO OD DOMA - REMOTE", "NA DALJAVO", "REMOTE"}:
            return None, None

        # Če je vrednost ime regije ali vsebuje ime regije, vrni samo regijo
        REGIJE = {
            "POMURSKA", "PODRAVSKA", "KOROŠKA", "SAVINJSKA", "ZASAVSKA",
            "POSAVSKA", "JUGOVZHODNA SLOVENIJA", "OSREDNJESLOVENSKA",
            "GORENJSKA", "PRIMORSKO-NOTRANJSKA", "GORIŠKA", "OBALNO-KRAŠKA",
        }
        REGIJA_ALIASI = {
            "DOLENJSKA": "JUGOVZHODNA SLOVENIJA",
            "DOLENJSKA REGIJA": "JUGOVZHODNA SLOVENIJA",
            "PRIMORSKA": "OBALNO-KRAŠKA",
            "J.PRIMORSKA": "OBALNO-KRAŠKA",
            "ŠTAJERSKA": "PODRAVSKA",
            "ŠTAJERSKA REGIJA": "PODRAVSKA",
            "SAVINJSKA REGIJA": "SAVINJSKA",
            "POMURSKA REGIJA": "POMURSKA",
            "KOROŠKA REGIJA": "KOROŠKA",
            "GORENJSKA REGIJA": "GORENJSKA",
            "OBALNO KRAŠKA REGIJA": "OBALNO-KRAŠKA",
        }

        # Direktni match na regijo
        if normalized in REGIJE:
            return None, normalized
        if normalized in REGIJA_ALIASI:
            return None, REGIJA_ALIASI[normalized]

        # Regija na začetku stringa (npr. "SAVINJSKA REGIJA, LOŽNICA PRI ŽALCU 58")
        candidate_before_comma = re.split(r"[,]", normalized)[0].strip()
        if candidate_before_comma in REGIJE:
            return None, candidate_before_comma
        if candidate_before_comma in REGIJA_ALIASI:
            return None, REGIJA_ALIASI[candidate_before_comma]

        # Izvleči kandidata: vse pred vejico, črtijo, oklepajem
        candidate = re.split(r"[,(\-]", normalized)[0].strip()

        # Odstrani morebitne presledke na koncu (npr. "VELENJE ")
        candidate = candidate.strip()

        if candidate in self._naselja:
            return self._naselja[candidate], self._naselja_regija.get(candidate)

        # Fallback: poskusi s krajšanjem besed z desne
        # npr. "MARIBOR RAZVANJE" → "MARIBOR"
        words = candidate.split()
        for i in range(len(words) - 1, 0, -1):
            shorter = " ".join(words[:i])
            if shorter in self._naselja:
                return self._naselja[shorter], self._naselja_regija.get(shorter)

        # Fallback: občinski lookup — če je kandidat ime občine, vrni samo regijo
        if candidate in self._obcine_regija:
            return None, self._obcine_regija[candidate]

        # Fallback: reverse lookup — poskusi najti naselje v delu za vejico
        # Generična imena ki se pogosto pojavijo v naslovih in povzročijo napačne matche
        _GENERIC_NAMES = {
            "CESTA", "NOVA VAS", "POTOK", "ULICA", "VAS", "SELO", "LOG",
            "PTUJSKA CESTA", "SV. DUH", "STEGNE",
        }
        parts = re.split(r"[,]", normalized)
        if len(parts) > 1:
            address_part = parts[1].strip()
            # Odstrani hišno številko z desne (npr. "AMBROŽ POD KRVAVCEM 71" → "AMBROŽ POD KRVAVCEM")
            addr_words = address_part.split()
            for i in range(len(addr_words), 0, -1):
                addr_candidate = " ".join(addr_words[:i])
                if addr_candidate in _GENERIC_NAMES:
                    continue
                if addr_candidate in self._naselja:
                    return self._naselja[addr_candidate], self._naselja_regija.get(addr_candidate)

        return None, None

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

    # CSV operacije

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

        # Normaliziraj tudi obstoječe listinge (ki niso bili v trenutnem scrape-u)
        for listing in existing.values():
            self._clean_listing(listing)

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
