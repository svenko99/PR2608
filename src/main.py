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

    cleaner = Cleaner()
    cleaned_listings, changes, new_count = cleaner.run(listings)

    print(f"Novih oglasov: {new_count}.")
    print(f"Posodobljen data.csv z {len(cleaned_listings)} trenutno videnimi oglasi.")
    print(f"Posodobljen changes.csv z {len(changes)} zaznanimi spremembami.")
