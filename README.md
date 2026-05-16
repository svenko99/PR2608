# Podatkovno rudarjenje projekt

Člani: [Sven Ulčar](https://github.com/svenko99), [Lan Lebar](https://github.com/lebaaar), [Jan Tuhtar](https://github.com/jan2749), [Žan Mlinar](https://github.com/zanmlinar05-ops), [Jan Zamernik](https://github.com/janzamernik)

## Poročila

- [`osnutek.md`](/reports/osnutek.md)
- [`VMESNO.md`](/reports/VMESNO.md)
- [`PR2025-26_VMESNA_08.pptx`](/reports/PR2025-26_VMESNA_08.pptx)
- [`KONČNO.md`](/reports/KONČNO.md)

## Jupyter Notebook

Za zagon Jupyter Notebook ([`rezultati.ipynb`](./src/notebook/rezultati.ipynb)) si naloži [
`uv`](https://docs.astral.sh/uv/getting-started/installation/) in poženi:

```bash
cd src
uv sync
uv run --with jupyter jupyter lab
```

## Scraper

Scraper teče na GitHub Actions vsak dan ob 18:39 UTC prek workflowa [
`scraper.yml`](./.github/workflows/scraper.yml), ki zažene scraper ter commita in pusha nove podatke. Workflow je mogoče
tudi ročno sprožiti prek `workflow_dispatch`.

### Navodila za zagon

Za zagon potrebuješ nameščen [`uv`](https://docs.astral.sh/uv/) ter datoteko `.env` v mapi `src` s poverilnico (
`STUDENTSKI_SERVIS_EMAIL` in `STUDENTSKI_SERVIS_PASSWORD`) ali veljavnim `STUDENTSKI_SERVIS_COOKIE`. Scraper se zaganja
iz mape `src`.

```bash
cd src
uv sync
uv run python main.py
```

Ob zagonu se trenutni oglasi preberejo s portala, nato pa se podatki shranijo oziroma posodobijo v `data/data.csv` in
`data/changes.csv`.

Pred začetkom scrapanja scraper preveri veljavnost piškotka na prvi strani. Če je potekel, se samodejno prijavi z
email/geslom in nov cookie shrani v `.env`. Če pri vseh uspešno razbranih oglasih manjka `company`, se zagon prekine in
v CSV datoteke ne zapisuje ničesar.

