# Podatkovno rudarjenje projekt

Člani: [Sven Ulčar](https://github.com/svenko99), [Lan Lebar](https://github.com/lebaaar), [Jan Tuhtar](https://github.com/jan2749), [Žan Mlinar](https://github.com/zanmlinar05-ops), [Jan Zamernik](https://github.com/janzamernik)

## Poročila

- [`osnutek.md`](/reports/osnutek.md)

## Scraper

Za zagon potrebuješ nameščen [`uv`](https://docs.astral.sh/uv/) in veljaven `STUDENTSKI_SERVIS_COOKIE`, shranjen v datoteki `.env` v mapi `src`. Scraper se nato zaganja iz mape `src`.

```bash
cd src
uv sync
echo 'STUDENTSKI_SERVIS_COOKIE=ess_sess...' > .env
uv run python main.py
```

Ob zagonu se trenutni oglasi preberejo s portala, nato pa se podatki shranijo oziroma posodobijo v `data/data.csv` in `data/changes.csv`.

Pred začetkom scrapanja scraper preveri veljavnost piškotka na prvi strani. Če pri vseh uspešno razbranih oglasih manjka `company`, se zagon prekine in v CSV datoteke ne zapisuje ničesar.

## TODO

- Dodajanje filtrov v `osnutek.md`
- Pošlji Discord webhook, če je cookie expired
