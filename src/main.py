from scraper import Scraper

if __name__ == "__main__":
    scraper = Scraper(testing=False)

    listings = scraper.extract_multiple_pages()  # Prebere vse strani (dodaj parameter max_page če hočeš omejiti do katere strani gre)
    scraper.update_csv_database(listings)

    print(f"Posodobljen data.csv z {len(listings)} trenutno videnimi oglasi.")
    print(f"Posodobljen history.csv z {len(listings)} novimi opažanji.")
