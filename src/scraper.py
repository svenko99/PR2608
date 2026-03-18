from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
import csv
import os
import re
import time

import requests
from bs4 import BeautifulSoup, Tag
from dotenv import find_dotenv, load_dotenv, set_key

from models import ListingChange, PaymentType, StudentListing, WorkSchedule

load_dotenv()


class InvalidCookieError(RuntimeError):
    pass


class LoginError(RuntimeError):
    pass


class Scraper:
    BASE_URL = "https://www.studentski-servis.com/studenti/prosta-dela"
    CSV_FILE = Path("../data/data.csv")
    CHANGES_CSV_FILE = Path("../data/changes.csv")

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    def __init__(
            self,
            testing: bool = False,
            testing_file: str = "testing.html",
            timeout: int = 15,
            page_delay: float = 2,
    ) -> None:
        self.testing = testing
        self.testing_file = Path(testing_file)
        self.timeout = timeout
        self.page_delay = page_delay

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        cookie = os.getenv("STUDENTSKI_SERVIS_COOKIE")
        has_credentials = bool(
            os.getenv("STUDENTSKI_SERVIS_EMAIL") and os.getenv("STUDENTSKI_SERVIS_PASSWORD")
        )
        if not self.testing and not cookie and not has_credentials:
            raise ValueError(
                "Manjka STUDENTSKI_SERVIS_COOKIE ali "
                "STUDENTSKI_SERVIS_EMAIL + STUDENTSKI_SERVIS_PASSWORD v .env"
            )

        if cookie:
            self.session.headers.update({"Cookie": cookie})

    def login(self) -> None:
        """Prijavi se z email/geslom in posodobi session cookie."""
        email = os.getenv("STUDENTSKI_SERVIS_EMAIL")
        password = os.getenv("STUDENTSKI_SERVIS_PASSWORD")

        if not email or not password:
            raise LoginError(
                "Manjka STUDENTSKI_SERVIS_EMAIL ali STUDENTSKI_SERVIS_PASSWORD v .env"
            )

        # Pridobi CSRF tokene s strani
        response = self.session.get(self.BASE_URL, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        session_key_el = soup.select_one('input[name="_session_key"]')
        token_el = soup.select_one('input[name="_token"]')

        if not session_key_el or not token_el:
            raise LoginError("Ni mogoče najti CSRF tokenov na strani za prijavo.")

        login_response = self.session.post(
            self.BASE_URL,
            headers={
                "X-OCTOBER-REQUEST-HANDLER": "onSignin",
                "X-OCTOBER-REQUEST-PARTIALS": "",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": self.BASE_URL,
            },
            data={
                "_session_key": session_key_el["value"],
                "_token": token_el["value"],
                "login": email,
                "password": password,
                "remember": "1",
                "artref": "",
            },
            timeout=self.timeout,
        )
        login_response.raise_for_status()

        # Posodobi Cookie header iz session cookie jara
        new_cookie = "; ".join(
            f"{c.name}={c.value}" for c in self.session.cookies
        )
        if not new_cookie:
            raise LoginError("Prijava ni uspela: strežnik ni vrnil nobenega cookija.")

        self.session.headers.update({"Cookie": new_cookie})

        dotenv_path = find_dotenv(usecwd=True) or find_dotenv(
            filename=".env",
            raise_error_if_not_found=False,
            usecwd=False,
        )
        if dotenv_path:
            set_key(dotenv_path, "STUDENTSKI_SERVIS_COOKIE", new_cookie)

    def get_html_content(self, page_number: int = 1) -> str:
        if self.testing:
            return self.testing_file.read_text(encoding="utf-8")

        params = {"page": page_number}
        response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def extract_data(self, page_number: int = 1, seen_at: datetime | None = None) -> list[StudentListing]:
        html_text = self.get_html_content(page_number)
        return self._parse_listings_from_html(html_text, seen_at=seen_at)

    def validate_cookie(self) -> None:
        html_text = self.get_html_content(page_number=1)
        listings = self._parse_listings_from_html(html_text)

        if not listings:
            raise InvalidCookieError(
                "Cookie ni veljaven: na prvi strani ni bilo mogoče uspešno razbrati nobenega oglasa."
            )

        if all(not listing.company for listing in listings):
            raise InvalidCookieError(
                "Cookie ni veljaven: noben oglas na prvi strani nima izpolnjenega polja company."
            )

    def _parse_listings_from_html(
            self,
            html_text: str,
            seen_at: datetime | None = None,
    ) -> list[StudentListing]:
        soup = BeautifulSoup(html_text, "html.parser")

        seen_at = seen_at or datetime.now(UTC)
        listings: list[StudentListing] = []

        for article in soup.select("article.job-item"):
            try:
                listings.append(self.parse_listing(article, seen_at=seen_at))
            except ValueError as e:
                print("Parse listing error:", e)
                continue

        return listings

    def get_total_pages(self) -> int:
        html_text = self.get_html_content(page_number=1)
        soup = BeautifulSoup(html_text, "html.parser")

        page_numbers = []

        for a in soup.select(".pagination a[data-page]"):
            raw = a.get("data-page")
            if raw and raw.isdigit():
                page_numbers.append(int(raw))

        print("TOTAL_PAGES:", page_numbers)
        return max(page_numbers) if page_numbers else 1

    def extract_multiple_pages(self, max_page: int | None = None) -> list[StudentListing]:
        seen_at = datetime.now(UTC)
        all_listings: list[StudentListing] = []

        total_pages = self.get_total_pages()
        final_page = min(max_page, total_pages) if max_page is not None else total_pages
        print(f"Skupaj strani za obdelat: {final_page}")

        for page_number in range(1, final_page + 1):
            if page_number > 1:
                time.sleep(self.page_delay)
            page_listings = self.extract_data(page_number, seen_at=seen_at)
            print(f"Stran {page_number}: {len(page_listings)} listingov")
            all_listings.extend(page_listings)

        deduped: dict[int, StudentListing] = {}
        for listing in all_listings:
            deduped[listing.id] = listing

        return list(deduped.values())

    def parse_listing(self, article: Tag, seen_at: datetime) -> StudentListing:
        listing_id = self._parse_int(article.get("data-jobid"))
        if listing_id is None:
            print("Oglas preskočen, ker nima veljavnega data-jobid:", article)
            raise ValueError("Manjka ali je neveljaven data-jobid")

        left = self._get_left_column(article)

        title, subtitle = self._extract_titles(left)
        if not title:
            print(f"Oglas {listing_id} preskočen, ker nima naslova:", article)
            raise ValueError(f"Oglas {listing_id} nima naslova")

        company = self._extract_icon_text_from_ps(left, "icon-building") or ""
        location = self._extract_icon_text_from_ps(left, "icon-location")
        sublocation = self._extract_icon_text_from_ps(left, "icon-target")

        payment_li = left.select_one("li.job-payment")
        payment_text = self._clean_text(payment_li)
        hourly_rate_neto, hourly_rate_bruto, hourly_rate_from = self._parse_hourly_rate(payment_text)
        payment_type = self._parse_payment_type(hourly_rate_from)

        description = self._clean_text(left.select_one("p.description"))

        attrs = self._extract_label_value_map(article)
        open_positions = self._parse_int(attrs.get("Prosta mesta"))
        duration = attrs.get("Trajanje")
        work_schedule = self._parse_work_schedule(attrs.get("Delovnik"))
        start_date = self._parse_slovenian_date(attrs.get("Začetek dela"))

        return StudentListing(
            id=listing_id,
            title=title,
            subtitle=subtitle,
            company=company,
            location=location,
            sublocation=sublocation,
            hourly_rate_neto=hourly_rate_neto,
            hourly_rate_bruto=hourly_rate_bruto,
            hourly_rate_from=hourly_rate_from,
            payment_type=payment_type,
            description=description,
            open_positions=open_positions,
            duration=duration,
            work_schedule=work_schedule,
            start_date=start_date,
            first_seen=seen_at,
            last_seen=seen_at,
        )

    def update_csv_database(
            self,
            current_listings: list[StudentListing],
            csv_path: Path | None = None,
            changes_csv_path: Path | None = None,
    ) -> tuple[list[ListingChange], int]:
        csv_path = csv_path or self.CSV_FILE
        changes_csv_path = changes_csv_path or self.CHANGES_CSV_FILE

        csv_path.parent.mkdir(parents=True, exist_ok=True)
        changes_csv_path.parent.mkdir(parents=True, exist_ok=True)

        existing = self._load_existing_csv(csv_path)
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

    def _load_existing_csv(self, csv_path: Path) -> dict[int, StudentListing]:
        if not csv_path.exists():
            return {}

        listings: dict[int, StudentListing] = {}
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                listing = StudentListing.from_csv_row(row)
                listings[listing.id] = listing

        return listings

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

    def _clean_text(self, node: Tag | None) -> str | None:
        if node is None:
            return None
        text = node.get_text(" ", strip=True)
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text or None

    def _strip_svg_and_get_text(self, node: Tag | None) -> str | None:
        if node is None:
            return None

        clone = BeautifulSoup(str(node), "html.parser")
        for svg in clone.select("svg"):
            svg.decompose()

        text = clone.get_text(" ", strip=True)
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text or None

    def _parse_int(self, value: str | None) -> int | None:
        if not value:
            return None
        normalized = value.replace(".", "").replace(" ", "")
        match = re.search(r"\d+", normalized)
        return int(match.group()) if match else None

    def _parse_slovenian_date(self, value: str | None) -> date | None:
        if not value:
            return None
        value = re.sub(r"\s+", " ", value).strip()
        try:
            return datetime.strptime(value, "%d. %m. %Y").date()
        except ValueError as e:
            print("Error parse_date:", e)
            return None

    def _parse_work_schedule(self, value: str | None) -> WorkSchedule | None:
        if not value:
            return None

        normalized = re.sub(r"\s+", " ", value).strip().upper()
        mapping = {
            "PO DOGOVORU": WorkSchedule.BY_AGREEMENT,
            "DOPOLDAN": WorkSchedule.MORNING,
            "IZMENSKO": WorkSchedule.SHIFT,
            "POPOLDAN": WorkSchedule.AFTERNOON,
            "MED VIKENDI": WorkSchedule.WEEKENDS,
        }
        return mapping.get(normalized)

    def _parse_payment_type(self, value: str | None) -> PaymentType | None:
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

    def _parse_hourly_rate(self, text: str | None) -> tuple[float | None, float | None, str | None]:
        if not text:
            return None, None, None

        raw = re.sub(r"\s+", " ", text).strip()
        upper = raw.upper()

        if "DOGOVOR" in upper:
            return None, None, raw

        neto = None
        bruto = None

        m_neto = re.search(r"(\d+(?:[.,]\d+)?)\s*€\s*/h\s*neto", raw, re.IGNORECASE)
        m_bruto = re.search(r"(\d+(?:[.,]\d+)?)\s*€\s*/h\s*bruto", raw, re.IGNORECASE)

        if m_neto:
            neto = float(m_neto.group(1).replace(",", "."))
        if m_bruto:
            bruto = float(m_bruto.group(1).replace(",", "."))

        return neto, bruto, raw

    def _extract_label_value_map(self, article: Tag) -> dict[str, str]:
        result: dict[str, str] = {}
        for ul in article.select("ul.job-attributes"):
            if ul.select_one("li.job-payment"):
                continue
            for li in ul.select("li"):
                text = self._clean_text(li)
                if not text or ":" not in text:
                    continue
                label, value = text.split(":", 1)
                result[label.strip()] = value.strip()
        return result

    def _get_left_column(self, article: Tag) -> Tag:
        return article.select_one("div.col-12.col-md-8") or article

    def _get_icon_name(self, use_tag: Tag | None) -> str | None:
        if use_tag is None:
            return None
        href = use_tag.get("xlink:href") or use_tag.get("href") or ""
        match = re.search(r"#(icon-[\w-]+)$", href)
        return match.group(1) if match else None

    def _extract_icon_text_from_ps(self, scope: Tag, icon_name: str) -> str | None:
        for p in scope.select("p"):
            use = p.select_one("svg use")
            if self._get_icon_name(use) == icon_name:
                return self._strip_svg_and_get_text(p)
        return None

    def _extract_titles(self, left: Tag) -> tuple[str | None, str | None]:
        h5s = left.select("h5")
        titles = [self._clean_text(h5) for h5 in h5s]
        titles = [t for t in titles if t]
        title = titles[0] if len(titles) > 0 else None
        subtitle = titles[1] if len(titles) > 1 else None
        return title, subtitle
