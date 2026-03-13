# Podatkovno rudarjenje projekt

Člani: [Sven Ulčar](https://github.com/svenko99), [Lan Lebar](https://github.com/lebaaar), [Jan Tuhtar](https://github.com/jan2749), [Žan Mlinar](https://github.com/zanmlinar05-ops), [Jan Zamernik](https://github.com/janzamernik)

Osnutek na voljo [tukaj](/reports/osnutek.md).

## Zagon scraperja

Za zagon potrebuješ nameščen [`uv`](https://docs.astral.sh/uv/) in veljaven `STUDENTSKI_SERVIS_COOKIE`, shranjen v
datoteki `.env` v mapi `src`.

Scraper se nato zaganja iz mape `src`:

```bash
cd src
uv sync
echo 'STUDENTSKI_SERVIS_COOKIE=...' > .env
uv run python main.py
```

Ob zagonu se trenutni oglasi preberejo s portala, nato pa se podatki shranijo oziroma posodobijo v `data/data.csv` in
`data/history.csv`.

## TODO

- Izbriši atribut `currently_visible`
- Posodobi delovanje `history.csv`, da bo shranjevala zgolj spremembe (preimenuj v `changes.csv`)
- Dodajanje filtrov v osnutek.md
- Preveri delovanje piškotka pred scrapanjem (pošlji Discrod webhook). Ne scrapaj, če je expired.