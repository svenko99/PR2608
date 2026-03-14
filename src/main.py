from scraper import Scraper

if __name__ == "__main__":
    scraper = Scraper(testing=False)

    listings = scraper.extract_multiple_pages()  # Prebere vse strani (dodaj parameter max_page če hočeš omejiti do katere strani gre)
    changes = scraper.update_csv_database(listings)

    print(f"Posodobljen data.csv z {len(listings)} trenutno videnimi oglasi.")
    print(f"Posodobljen changes.csv z {len(changes)} zaznanimi spremembami.")
