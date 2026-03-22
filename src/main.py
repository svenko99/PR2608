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

    print(f"Št. novih oglasov: {new_count}.")
    print(f"data.csv ima {len(cleaned_listings)} trenutno videnih oglasov.")
    print(f"changes.csv ima {len(changes)} novih sprememb.")
