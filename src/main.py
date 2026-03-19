import sys

from scraper import InvalidCookieError, LoginError, Scraper
from cleaner import Cleaner

if __name__ == "__main__":
    scraper = Scraper(testing=False)

    try:
        scraper.validate_cookie()
    except InvalidCookieError:
        print("Cookie je potekel ali neveljaven, poskušam prijavo...", file=sys.stderr)
        try:
            scraper.login()
            scraper.validate_cookie()
        except (LoginError, InvalidCookieError) as exc:
            print(f"Napaka pri prijavi: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        print("Prijava uspešna.")

    listings = scraper.extract_multiple_pages()
    scraper.save_raw_csv(listings)

    print(f"Surovi podatki shranjeni v data/raw/data.csv ({len(listings)} oglasov).")

    cleaner = Cleaner()
    cleaned_listings, changes, new_count = cleaner.run()

    print(f"Novih oglasov: {new_count}.")
    print(f"Posodobljen data/clean/data.csv z {len(cleaned_listings)} trenutno videnimi oglasi.")
    print(f"Posodobljen data/clean/changes.csv z {len(changes)} zaznanimi spremembami.")
