# Podatkovno rudarjenje projekt

Člani: [Sven Ulčar](https://github.com/svenko99), [Lan Lebar](https://github.com/lebaaar), [Jan Tuhtar](https://github.com/jan2749), [Žan Mlinar](https://github.com/zanmlinar05-ops), [Jan Zamernik](https://github.com/janzamernik)

## Poročila

- [`osnutek.md`](/reports/osnutek.md)

## Scraper

Za zagon potrebuješ nameščen [`uv`](https://docs.astral.sh/uv/) ter datoteko `.env` v mapi `src` s poverilnico (`STUDENTSKI_SERVIS_EMAIL` in `STUDENTSKI_SERVIS_PASSWORD`) ali veljavnim `STUDENTSKI_SERVIS_COOKIE`. Scraper se zaganja iz mape `src`.

```bash
cd src
uv sync
uv run python main.py
```

Ob zagonu se trenutni oglasi preberejo s portala, nato pa se podatki shranijo oziroma posodobijo v `data/data.csv` in `data/changes.csv`.

Pred začetkom scrapanja scraper preveri veljavnost piškotka na prvi strani. Če je potekel, se samodejno prijavi z email/geslom in nov cookie shrani v `.env`. Če pri vseh uspešno razbranih oglasih manjka `company`, se zagon prekine in v CSV datoteke ne zapisuje ničesar.

## TODO

- Dodajanje filtrov v `osnutek.md`
- Pošlji Discord webhook, če je cookie expired
