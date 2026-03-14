import sys

from scraper import InvalidCookieError, Scraper

if __name__ == "__main__":
    try:
        scraper = Scraper(testing=False)
        scraper.validate_cookie()
    except InvalidCookieError as exc:
        print(f"Napaka: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    listings = scraper.extract_multiple_pages()  # Prebere vse strani (dodaj parameter max_page če hočeš omejiti do katere strani gre)
    changes = scraper.update_csv_database(listings)

    print(f"Posodobljen data.csv z {len(listings)} trenutno videnimi oglasi.")
    print(f"Posodobljen changes.csv z {len(changes)} zaznanimi spremembami.")
