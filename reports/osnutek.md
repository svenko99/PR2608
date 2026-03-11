# Identifikacija vzorcev uspešnosti in tveganja stečaja pri slovenskih podjetjih

## Opis problema
TODO
<!-- V našem projektu se bomo ukvarjali z identifikacijo ključnih lastnosti in vzorcev, ki ločujejo uspešna slovenska podjetja od tistih, ki končajo v stečaju. Na podlagi finančnih, kadrovskih, poslovnih ter drugih podatkov želimo odkriti, kateri dejavniki (npr. velikost podjetja, panoga, lokacija, prisotnost tujih investitorjev ipd.) pomembno prispevajo k dolgoročni uspešnosti podjetja oziroma vodijo v njegov stečaj.

S tem želimo ponuditi čimbolj uporabne vpoglede za podjetnike in investitorje, tako da imajo vpogled na katere lastnosti morajo biti ob poslovanju pozorni, tudi takšne, ki morda na prvi pogled niso tako očitne.

Za podatke smo vzeli prva in zadnja 3 leta delujočih podjetij (za tista, ki imajo tako dolg čas obstoja), kot tudi podjetij, ki so šla v stečaj. Menimo, da se ključni podatki, ki prikazujejo ali bo podjetje uspešno nahajajo v prvih letih delovanja, tako bomo lahko tudi predvidevali, kako bodo novejša podjetja lahko končala. Zadnja 3 leta podatkov, bo pa namenjeno iskanju korelacij (ne)uspešnih podjetij. -->

## Cilj projekta

Pri projektu želimo odgovoriti na:
<!-- - Katere korelacije in vzorci obstajajo med značilnostmi (ne)uspešnih podjetij?
- Obstajajo kakšne ponavljajoče se napake podjetij, ki peljejo v veliko tveganje stečaja?
- Kako vpliva lokacija podjetja, ali moramo biti v različnih regijah pozorni na specifične stvari?
- Ali lahko predvidimo, kako bo podjetje končalo, glede na začetna 3 leta poslovanja? -->

## Vir in oblika podatkov

Podatke za projekt bomo črpali iz [e-Študntskega servisa](https://studentski-servis.com/studenti). Ker ne ponujajo brezplačnega javno dostopnega API-ja bomo podatke scrapali iz njihove spletne aplikacije. Iz datotetke [`robots.txt`](https://studentski-servis.com/robots.txt) ugotovimo, da je scrapanje podatkov dovoljeno, saj vsebuje `User-agent: *` in `Allow: /`.

### Pridobivanje podatkov
Za pridobivanje podatkov iz spletne aplikacije e-Študentski servis bomo uporabil Python knjižnico [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).

Znotraj aplikacije lahko vidimo zgolj trenutne objave dela. Pred seboj imamo 2 opciji:
- Podatke scrapamo enkrat, in nad njimi izvajamo analizo
- Podatke scrapamo par mescov, vsak dan ob isit uri. Tako bomo lahko sledili spremembam objav...

Preden začnemo pisati `scraper.py`, najprej izvedemo analizo same aplikacije, in se odoločimo, katere podatke bomo zbirali. Vsaka objava na strani ima sledeče podatke:

| Podatek          | Tip podatka | Obvezno | Primer vrednosti                        | Opombe                                                                |
|------------------|-------------|---------|-----------------------------------------|-----------------------------------------------------------------------|
| `id`             | `TEXT`      | ✅      | `475748`                                                  | Enolični identifikator objave                       |
| `title`          | `TEXT`      | ✅      | `POMOČ V TRGOVINI`                                        | Glavna kategorija dela                              |
| `subtitle`       | `TEXT`      | ❌      | `POLNJENJE POLIC`                                         | Podkategorija, ni vedno prisotna                    |
| `company`        | `TEXT`      | ✅      | `MERCATOR D.O.O.`                                         |                                                     |
| `location`       | `TEXT`      | ✅      | `LJUBLJANA , NOVE FUŽINE 33`                              | Mesto ali regija                                    |
| `sublocation`    | `TEXT`      | ❌      | `HIPERMARKET KRANJ PRIMSKOVO`                             | Naslov ali ime objekta (npr. `Pekarna`, `ZD Kranj`) |
| `rate_neto`      | `REAL`      | ❌      | `7.73`                                                    | `NULL` če je plačilo po dogovoru                    |
| `rate_bruto`     | `REAL`      | ❌      | `8.98`                                                    | `NULL` če je plačilo po dogovoru                    |
| `description`    | `TEXT`      | ✅      | `Iščejo študenta/ki za delo v ...`                        | Besedilo opisa dela                                 |
| `open_positions` | `INTEGER`   | ❌      | `2`                                                       | `NULL` če ni navedeno                               |
| `duration`       | `TEXT`      | ✅      | `Dlje časa (zač. in obč. delo)`, `PO DOGOVORU`...         |                                                     |
| `work_schedule`  | `TEXT`      | ✅      | `IZMENSKO`                                                | Dopoldan / popoldan / izmensko / po dogovoru        |
| `start_date`     | `TEXT`      | ❌      | `25.3.2026`                                               | `NULL` če ni navedeno                               |
| `contact_name`   | `TEXT`      | ✅      | `Janez Primer`                                            |                                                     |
| `contact_phone`  | `TEXT`      | ❌      | `031123456`                                               | `NULL` če ni navedeno                               |
| `contact_email`  | `TEXT`      | ❌      | `email@domain.com`                                        | `NULL` če ni navedeno                               |
| `scraped_at`     | `TEXT`      | ✅      | `2026-03-11T08:00:00+00:00`                               | Čas pridobitve podatka (ISO 8601, UTC)              |

Objave del nimajo svojih URL-jev, vendar so združena v eno HTML stran.

### Oblika podatkov
TODO



