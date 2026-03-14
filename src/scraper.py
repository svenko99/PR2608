from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
import csv
import os
import re

import requests
from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv

from models import PaymentType, StudentListing, WorkSchedule

load_dotenv()


class Scraper:
    BASE_URL = "https://www.studentski-servis.com/studenti/prosta-dela"
    CSV_FILE = Path("../data/data.csv")
    HISTORY_CSV_FILE = Path("../data/history.csv")

    def __init__(
            self,
            testing: bool = False,
            testing_file: str = "testing.html",
            timeout: int = 15,
    ) -> None:
        self.testing = testing
        self.testing_file = Path(testing_file)
        self.timeout = timeout

        self.session = requests.Session()
        cookie = os.getenv("STUDENTSKI_SERVIS_COOKIE")
        if not self.testing and not cookie:
            raise ValueError("Manjka STUDENTSKI_SERVIS_COOKIE v .env")

        if cookie:
            self.session.headers.update({"Cookie": cookie})

    def get_html_content(self, page_number: int = 1) -> str:
        if self.testing:
            return self.testing_file.read_text(encoding="utf-8")

        params = {"page": page_number}
        response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def extract_data(self, page_number: int = 1, seen_at: datetime | None = None) -> list[StudentListing]:
        html_text = self.get_html_content(page_number)
        soup = BeautifulSoup(html_text, "html.parser")

        seen_at = seen_at or datetime.now(UTC)
        listings: list[StudentListing] = []

        for article in soup.select("article.job-item"):
            try:
                listings.append(self.parse_listing(article, seen_at=seen_at))
            except ValueError:
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

        return max(page_numbers) if page_numbers else 1

    def extract_multiple_pages(self, max_page: int | None = None) -> list[StudentListing]:
        seen_at = datetime.now(UTC)
        all_listings: list[StudentListing] = []

        total_pages = self.get_total_pages()
        final_page = min(max_page, total_pages) if max_page is not None else total_pages

        for page_number in range(1, final_page + 1):
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
            raise ValueError("Manjka ali je neveljaven data-jobid")

        left = self._get_left_column(article)

        title, subtitle = self._extract_titles(left)
        if not title:
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

        contact_name = self._extract_contact_name(article)
        contact_email = self._extract_contact_email(article)
        contact_phones = self._extract_contact_phones(article)
        contact_webpage = self._extract_contact_webpage(article)

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
            contact_name=contact_name,
            contact_phone=", ".join(contact_phones) if contact_phones else None,
            contact_email=contact_email,
            contact_webpage=contact_webpage,
            first_seen=seen_at,
            last_seen=seen_at,
        )

    def update_csv_database(
            self,
            current_listings: list[StudentListing],
            csv_path: Path | None = None,
            history_csv_path: Path | None = None,
    ) -> None:
        csv_path = csv_path or self.CSV_FILE
        history_csv_path = history_csv_path or self.HISTORY_CSV_FILE

        csv_path.parent.mkdir(parents=True, exist_ok=True)
        history_csv_path.parent.mkdir(parents=True, exist_ok=True)

        existing = self._load_existing_csv(csv_path)
        for listing in current_listings:
            if listing.id in existing:
                listing.first_seen = existing[listing.id].first_seen

            existing[listing.id] = listing

        self._write_csv(csv_path, existing)
        self._append_history_csv(history_csv_path, current_listings)

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

    def _append_history_csv(self, csv_path: Path, listings: list[StudentListing]) -> None:
        if not listings:
            return

        rows = [listing.to_history_row() for listing in listings]
        fieldnames = list(rows[0].keys())
        file_exists = csv_path.exists()

        with csv_path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows)

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
        except ValueError:
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

    def _get_contact_containers(self, article: Tag) -> list[Tag]:
        containers: list[Tag] = []
        containers.extend(article.select("[id^='job-details-mview-']"))
        containers.extend(article.select("[id^='jobDetail-']"))
        return containers

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

    def _extract_contact_name(self, article: Tag) -> str | None:
        for container in self._get_contact_containers(article):
            for span in container.select("span"):
                use = span.select_one("svg use")
                if self._get_icon_name(use) == "icon-person":
                    text = self._strip_svg_and_get_text(span)
                    if text and text.upper() != "KONTAKT DELODAJALCA":
                        return text
        return None

    def _extract_contact_email(self, article: Tag) -> str | None:
        for a in article.select("a[href]"):
            href = (a.get("href") or "").strip()
            if href.lower().startswith("mailto:"):
                return href[7:].strip() or None
        return None

    def _extract_contact_phones(self, article: Tag) -> list[str]:
        phones: list[str] = []
        for a in article.select("a[href]"):
            href = (a.get("href") or "").strip()
            if href.lower().startswith("tel:"):
                phone = href[4:].strip()
                if phone and phone not in phones:
                    phones.append(phone)
        return phones

    def _extract_contact_webpage(self, article: Tag) -> str | None:
        for container in self._get_contact_containers(article):
            for a in container.select("a[href]"):
                href = (a.get("href") or "").strip()
                if href.startswith("http"):
                    return href
        return None
