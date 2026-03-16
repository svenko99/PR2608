import sys

from scraper import InvalidCookieError, LoginError, Scraper

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

    listings = scraper.extract_multiple_pages()  # Prebere vse strani (dodaj parameter max_page če hočeš omejiti do katere strani gre)
    changes, new_count = scraper.update_csv_database(listings)

    print(f"Posodobljen data.csv z {len(listings)} trenutno videnimi oglasi.")
    print(f"Novih oglasov: {new_count}.")
    print(f"Posodobljen changes.csv z {len(changes)} zaznanimi spremembami.")
