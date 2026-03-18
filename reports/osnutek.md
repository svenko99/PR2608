# Analiza ponudbe študentskega dela v Sloveniji na podlagi oglasov e-Študentskega servisa

## Opis problema
e-Študentski servis predstavlja velik in ažuren vir podatkov o ponudbi študentskega dela v Sloveniji. Na portalu so javno objavljeni oglasi, ki vsebujejo informacije o delodajalcu, lokaciji, plačilu, delovniku, trajanju dela, začetku dela in besedilnem opisu nalog. Ti podatki so pri posameznem oglasu dostopni, niso pa pripravljeni v obliki, ki bi omogočala sistematično analizo celotne ponudbe.

V sklopu našega projekta bomo analizirali podatke iz servisa, in iz njih izračunali uporabno statistiko ter našli trenutne trende študentskega dela.
Iz same spletne aplikacije je težko odgovoriti na vprašanja, kot so: kje je ponudbe največ, katera dela so bolje plačana, katere lastnosti se pojavljajo pri bolje plačanih oglasih in kako dolgo oglasi ostanejo aktivni. Uporabnik lahko pregleduje posamezne oglase in filtrira rezultate, ne more pa enostavno opazovati vzorcev v večji množici podatkov.

Iz vidika podatkovnega rudarjenja je problem zanimiv, ker vsebuje kombinacijo strukturiranih in nestrukturiranih podatkov. Del atributov je že neposredno zapisan v strukturirani obliki (urna postavka, lokacija ali delovnik), del informacij pa je skrit opisu oglasa.

Pomembna lastnost teh podatkov je tudi njihova časovna omejenost. Portal prikazuje le trenutno aktivne oglase, zato brez sprotnega zajema ni mogoče ugotoviti, kako dolgo je bil posamezen oglas prisoten. Če oglase zbiramo več tednov, dobimo dodatno informacijo o dinamiki ponudbe: kateri tipi oglasov se pojavljajo pogosto, kateri izginejo hitro in kateri ostanejo prisotni dlje časa.

Projekt bo obravnaval javno objavljene oglase za študentsko delo kot vir podatkov za analizo ponudbe. Osredotočili se bomo na opis vzorcev v podatkih, primerjavo med oglasi in iskanje povezav med lastnostmi oglasa ter višino plačila.

## Cilj projekta
Cilj projekta je zgraditi podatkovno zbirko objavljenih oglasov iz e-Študentskega servisa in iz nje pridobiti nekaj uporabne statistike. S tem želimo pridobiti koristne informacije tako za študente, kot tudi za delodajalce.

Praktični cilj je pretvoriti razpršene podatke v obliko, ki omogoča nadaljnjo obdelavo, čiščenje, agregiranje in analizo. Raziskovalni cilj pa je iz teh podatkov izluščiti uporabne ugotovitve o lastnostih oglasov, razporeditvi ponudbe in dejavnikih, ki so povezani z višino plačila.

Pri projektu želimo odgovoriti na naslednja vprašanja:
- Kje so oglasi za študentsko delo v povprečju najbolje plačani?
- Katere lastnosti imajo bolje plačani oglasi?
- Katere veščine zahtevajo najbolje plačana dela?
- Kako dolgo oglasi praviloma ostanejo prisotni na portalu?
- Ali je trajanje prisotnosti oglasa povezano z njegovo vrsto, plačilom ali delovnikom?
- Kakšna dela so najpopularnejša med študenti - so najhitreje odstranjena iz oglasov?

## Vir in oblika podatkov
Podatke za projekt bomo črpali iz [e-Študentskega servisa](https://studentski-servis.com/studenti). Ker ne ponujajo javno dostopnega API-ja bomo podatke scrapali iz njihove spletne aplikacije. Iz datotetke [`robots.txt`](https://studentski-servis.com/robots.txt) ugotovimo, da je scrapanje podatkov dovoljeno, saj vsebuje `User-agent: *` in `Allow: /`.

### Pridobivanje podatkov
Za pridobivanje podatkov iz spletne aplikacije e-Študentski servis bomo uporabili Pythonovo knjižnico [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).<br>
Rezultati iskanja na portalu so razdeljeni na več strani, pri čemer posamezno stran določa URL parameter `page`. Ob vsakem zagonu bomo zato prebrali vse strani rezultatov.

### Shranjenvanje podatkov
Ker je v aplikaciji v danem času mogoče videti le trenutno objavljene oglase, želimo pa spremljati tudi njihovo dodajanje in odstranjevanje, bomo podatke zajemali vsak dan ob isti uri (20:00). Tako bomo v nekaj mesecih zgradili časovno zbirko oglasov s študentskega servisa.<br>
Podatke bomo shranjevali v dve CSV datoteki. Datoteka `data.csv` bo vsebovala vse oglase in kdaj je bil posamezen oglas zadnjič viden na platformi (atribut `last_seen`). Datoteka `changes.csv` bo vsako posodobitev posamzenega oglasa.

### Datoteka `data.csv`
Datoteka `data.csv` vsebuje eno vrstico na unikatni oglas. Namenjena je shranjevanju zadnjega stanja posameznega oglasa preko atributa `last_seen`. Če isti oglas opazimo večkrat, v tej datoteki posodobimo njegove podatke, ne pa dodamo nove vrstice.

| Atribut             | Tip podatka | Obvezno | Primer vrednosti                  | Opis                                                 |
|---------------------|-------------|---------|-----------------------------------|------------------------------------------------------|
| `id`                | `INTEGER`   | da      | `475748`                          | Enolični identifikator oglasa na portalu             |
| `title`             | `TEXT`      | da      | `POMOČ V TRGOVINI`               | Glavni naslov oglasa                                 |
| `subtitle`          | `TEXT`      | ne      | `POLNJENJE POLIC`                 | Dodatni naslov oglasa                                |
| `company`           | `TEXT`      | da      | `MERCATOR D.O.O.`                | Naziv delodajalca                                    |
| `location`          | `TEXT`      | ne      | `LJUBLJANA, NOVE FUŽINE 33`      | Lokacija oglasa v obliki, kot je zapisana na portalu |
| `sublocation`       | `TEXT`      | ne      | `HIPERMARKET KRANJ PRIMSKOVO`    | Dodatna lokacija ali ime objekta                     |
| `hourly_rate_neto`  | `REAL`      | ne      | `7.73`                            | Neto urna postavka, če je navedena                   |
| `hourly_rate_bruto` | `REAL`      | ne      | `8.98`                            | Bruto urna postavka, če je navedena                  |
| `hourly_rate_from`  | `TEXT`      | ne      | `7.73 €/h neto (8.98 €/h bruto)` | Surov zapis plačila iz oglasa                        |
| `payment_type`      | `TEXT`      | ne      | `HOURLY`                          | Normaliziran tip plačila (`HOURLY`, `NEGOTIABLE`, `PROJECT`, `PER_EVENT`, `PER_TRIP`, `OTHER`) |
| `description`       | `TEXT`      | ne      | `Iščejo študenta/ko za delo ...`  | Opis dela                                  |
| `open_positions`    | `INTEGER`   | ne      | `2`                               | Število prostih mest, če je navedeno                 |
| `duration`          | `TEXT`      | ne      | `DLJE ČASA (ZAČ. IN OBČ. DELO)`  | Trajanje dela v obliki, kot je zapisano v oglasu     |
| `work_schedule`     | `TEXT`      | ne      | `IZMENSKO`                        | Delovnik oglasa (`PO DOGOVORU`, `DOPOLDAN`, `IZMENSKO`, `POPOLDAN`, `MED VIKENDI`) |
| `start_date`        | `TEXT`      | ne      | `2026-03-25`                      | Datum začetka dela v formatu ISO 8601, če je naveden |
| `first_seen`        | `TEXT`      | da      | `2026-03-11T08:00:00+00:00`       | Čas prvega opažanja oglasa v formatu ISO 8601        |
| `last_seen`         | `TEXT`      | da      | `2026-03-20T08:00:00+00:00`       | Čas zadnjega opažanja oglasa v formatu ISO 8601      |

Datoteka `data.csv` nam omogoča odgovor na vprašanja, kateri oglasi so bili opaženi, kakšne lastnosti imajo in koliko časa je bil določen oglas prisoten v obdobju opazovanja.

### Datoteka `changes.csv`

Datoteka `changes.csv` beleži spremembe posameznih polj med zaporednimi zajemi. Vsaka vrstica predstavlja zaznano spremembo enega polja pri enem oglasu. Če se pri nekem oglasu med dvema zajemoma spremenita lokacija in urna postavka, se v datoteko zapišeta dve vrstici.

| Atribut      | Tip podatka | Obvezno | Primer vrednosti             | Opis                                                             |
|--------------|-------------|---------|------------------------------|------------------------------------------------------------------|
| `listing_id` | `INTEGER`   | da      | `475748`                     | Identifikator oglasa, ki povezuje vrstico z oglasom v `data.csv` |
| `changed_at` | `TEXT`      | da      | `2026-03-20T08:00:00+00:00`  | Čas zajema, pri katerem je bila sprememba zaznana                |
| `field`      | `TEXT`      | da      | `hourly_rate_neto`           | Atribut, ki se je spremenil                                   |
| `old_value`  | `TEXT`      | da      | `7.73`                       | Prejšnja vrednost atributa                                          |
| `new_value`  | `TEXT`      | da      | `8.50`                       | Nova vrednost atributa                                              |

Datoteka `changes.csv` nam omogoča analizo spreminjanja oglasov skozi čas. Iz nje lahko ugotovimo, kdaj in kako se je spremenila posamezna lastnost oglasa — na primer dvig urne postavke ali sprememba lokacije.