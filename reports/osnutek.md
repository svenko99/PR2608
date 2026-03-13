# Analiza ponudbe študentskega dela v Sloveniji na podlagi oglasov e-Študentskega servisa

## Opis problema

e-Študentski servis predstavlja velik in ažuren vir podatkov o ponudbi študentskega dela v Sloveniji. Na portalu so javno objavljeni oglasi, ki vsebujejo informacije o delodajalcu, lokaciji, plačilu, delovniku, trajanju dela, začetku dela in besedilnem opisu nalog. Ti podatki so pri posameznem oglasu dostopni, niso pa pripravljeni v obliki, ki bi omogočala sistematično analizo celotne ponudbe.

Problem našega projekta je pomanjkanje strukturiranega vpogleda v trg študentskega dela, kot se kaže skozi javno objavljene oglase. Iz same spletne aplikacije je težko odgovoriti na vprašanja, kot so: kje je ponudbe največ, katera dela so bolje plačana, katere lastnosti se pojavljajo pri bolje plačanih oglasih in kako dolgo oglasi ostanejo aktivni. Uporabnik lahko pregleduje posamezne oglase in filtrira rezultate, ne more pa enostavno opazovati splošnih vzorcev v večji množici podatkov.

Z vidika podatkovnega rudarjenja je problem zanimiv zato, ker vsebuje kombinacijo strukturiranih in nestrukturiranih podatkov. Del atributov je že neposredno zapisan v strukturirani obliki, na primer urna postavka, lokacija ali delovnik, del informacij pa je skrit v prostem besedilu opisa oglasa. To omogoča povezovanje klasične analize atributov z analizo besedila.

Pomembna lastnost teh podatkov je tudi njihova časovna omejenost. Portal prikazuje le trenutno aktivne oglase, zato brez sprotnega zajema ni mogoče ugotoviti, kako dolgo je bil posamezen oglas prisoten. Če oglase zbiramo več tednov, dobimo dodatno informacijo o dinamiki ponudbe: kateri tipi oglasov se pojavljajo pogosto, kateri izginejo hitro in kateri ostanejo prisotni dlje časa.

Projekt bo zato obravnaval javno objavljene oglase za študentsko delo kot vir podatkov za analizo značilnosti ponudbe. Osredotočili se bomo na opis vzorcev v podatkih, primerjavo med oglasi in iskanje povezav med lastnostmi oglasa ter višino plačila.

## Kaj bomo raziskovali

Našo raziskavo bomo usmerili v tri sklope.

Prvi sklop bo opisna analiza ponudbe. Zanimalo nas bo, kako je ponudba porazdeljena po lokacijah, kako pogosto se pojavljajo posamezni delovniki, kakšne so razlike med kratkotrajnimi in dolgoročnejšimi deli ter kako se porazdeljuje plačilo med oglasi.

Drugi sklop bo analiza povezanosti med atributi oglasa in višino plačila. Raziskovali bomo, ali so bolje plačani oglasi povezani z določenimi lokacijami, določenimi tipi delovnika, določenimi opisi dela ali določenimi vsebinskimi značilnostmi oglasa.

Tretji sklop bo osnovna časovna analiza. Ker bodo podatki zbrani v omejenem obdobju, raziskava ne bo usmerjena v dolgoročne trende, ampak v kratkoročno dinamiko. Zanimalo nas bo, koliko časa oglasi praviloma ostanejo vidni, ali so bolje plačani oglasi prisotni krajši ali daljši čas in ali se v obdobju opazovanja spreminja skupna količina ponudbe.

## Cilj projekta

Cilj projekta je zgraditi podatkovno zbirko javno objavljenih oglasov z e-Študentskega servisa in na njej izvesti analizo ponudbe študentskega dela v Sloveniji.

Praktični cilj je pretvoriti razpršene spletne podatke v obliko, ki omogoča nadaljnjo obdelavo, čiščenje, agregiranje in analizo. Raziskovalni cilj pa je iz teh podatkov izluščiti uporabne in preverljive ugotovitve o lastnostih oglasov, razporeditvi ponudbe in dejavnikih, ki so povezani z višino plačila.

V projektu želimo odgovoriti predvsem na naslednja vprašanja:

- Kje se pojavlja največ ponudbe študentskega dela?
- Kje so oglasi za študentsko delo v povprečju najbolje plačani?
- Katere lastnosti imajo bolje plačani oglasi?
- Katere besede, izrazi ali veščine se najpogosteje pojavljajo v bolje plačanih oglasih?
- Kako dolgo oglasi praviloma ostanejo prisotni na portalu?
- Ali je trajanje prisotnosti oglasa povezano z njegovo vrsto, plačilom ali delovnikom?

Končni rezultat projekta bo urejen podatkovni nabor ter analiza, ki bo pokazala, da je mogoče tudi iz javno dostopnih spletnih oglasov s pomočjo podatkovnega rudarjenja pridobiti smiselne informacije o strukturi in kratkoročni dinamiki ponudbe študentskega dela.

## Vir in oblika podatkov

Podatke za projekt bomo pridobili s portala [e-Študentski servis](https://studentski-servis.com/studenti). Portal ne ponuja brezplačnega javnega API-ja za sistematičen dostop do oglasov, zato bomo podatke pridobivali iz HTML vsebine spletne aplikacije.

Pri tem je pomembno, da datoteka [`robots.txt`](https://studentski-servis.com/robots.txt) za domeno `studentski-servis.com` vsebuje `User-agent: *` in `Allow: /`, kar pomeni, da je dostop do poti na strani splošno dovoljen.

Za zajem podatkov bomo uporabili Python in knjižnico BeautifulSoup, s katero bomo iz HTML dokumentov izluščili podatke o posameznih oglasih. Rezultati iskanja na portalu so razdeljeni na več strani, pri čemer posamezno stran določa URL parameter `page`. Ob vsakem zagonu bomo zato prebrali vse strani rezultatov.

Podatke bomo shranjevali v dve CSV datoteki. Datoteka `data/data.csv` bo vsebovala zadnje znano stanje vsakega unikatnega oglasa. Datoteka `data/history.csv` bo vsebovala zgodovino opažanj, torej eno vrstico za vsak oglas ob vsakem zajemu. Takšna zasnova omogoča analizo trenutnega stanja in osnovno časovno analizo v omejenem obdobju zbiranja.

## Podroben opis podatkov

Osnovna enota opazovanja je en oglas za študentsko delo. Iz vsakega oglasa bomo izluščili strukturirane podatke, ki jih bomo nato shranili v dve ločeni datoteki.

### Datoteka `data/data.csv`

Datoteka `data.csv` vsebuje eno vrstico na unikatni oglas. Namenjena je shranjevanju zadnjega znanega stanja posameznega oglasa. Če isti oglas opazimo večkrat, v tej datoteki posodobimo njegove podatke, ne pa dodamo nove vrstice.

| Atribut             | Tip podatka | Obvezno | Primer vrednosti                 | Opis                                                 |
|---------------------|-------------|---------|----------------------------------|------------------------------------------------------|
| `id`                | `TEXT`      | da      | `475748`                         | Enolični identifikator oglasa na portalu             |
| `title`             | `TEXT`      | da      | `POMOČ V TRGOVINI`               | Glavni naslov oglasa                                 |
| `subtitle`          | `TEXT`      | ne      | `POLNJENJE POLIC`                | Dodatni naslov oglasa                                |
| `company`           | `TEXT`      | da      | `MERCATOR D.O.O.`                | Naziv delodajalca                                    |
| `location`          | `TEXT`      | da      | `LJUBLJANA, NOVE FUŽINE 33`      | Lokacija oglasa v obliki, kot je zapisana na portalu |
| `sublocation`       | `TEXT`      | ne      | `HIPERMARKET KRANJ PRIMSKOVO`    | Dodatna lokacija ali ime objekta                     |
| `hourly_rate_neto`  | `REAL`      | ne      | `7.73`                           | Neto urna postavka, če je navedena                   |
| `hourly_rate_bruto` | `REAL`      | ne      | `8.98`                           | Bruto urna postavka, če je navedena                  |
| `hourly_rate_from`  | `TEXT`      | da      | `7.73 €/h neto (8.98 €/h bruto)` | Surov zapis plačila iz oglasa                        |
| `payment_type`      | `TEXT`      | da      | `HOURLY`                         | Normaliziran tip plačila                             |
| `description`       | `TEXT`      | da      | `Iščejo študenta/ko za delo ...` | Besedilni opis dela                                  |
| `open_positions`    | `INTEGER`   | ne      | `2`                              | Število prostih mest, če je navedeno                 |
| `duration`          | `TEXT`      | da      | `DLJE ČASA (ZAČ. IN OBČ. DELO)`  | Trajanje dela v obliki, kot je zapisano v oglasu     |
| `work_schedule`     | `TEXT`      | da      | `IZMENSKO`                       | Delovnik oglasa                                      |
| `start_date`        | `TEXT`      | ne      | `2026-03-25`                     | Datum začetka dela, če je naveden                    |
| `contact_name`      | `TEXT`      | da      | `Janez Primer`                   | Ime kontaktne osebe                                  |
| `contact_phone`     | `TEXT`      | ne      | `031123456`                      | Telefonska številka                                  |
| `contact_email`     | `TEXT`      | ne      | `email@domain.com`               | Elektronski naslov                                   |
| `contact_webpage`   | `TEXT`      | ne      | `https://podjetje.si`            | Spletna povezava, če obstaja                         |
| `first_seen`        | `TEXT`      | da      | `2026-03-11T08:00:00+00:00`      | Čas prvega opažanja oglasa                           |
| `last_seen`         | `TEXT`      | da      | `2026-03-20T08:00:00+00:00`      | Čas zadnjega opažanja oglasa                         |
| `currently_visible` | `BOOLEAN`   | da      | `1`                              | Ali je bil oglas prisoten pri zadnjem zajemu         |

Datoteka `data.csv` nam omogoča odgovor na vprašanja, kateri oglasi so trenutno aktivni, kakšne lastnosti imajo aktivni oglasi in koliko časa je bil določen oglas prisoten v obdobju opazovanja.

### Datoteka `data/history.csv`

Datoteka `history.csv` vsebuje eno vrstico za vsak opažen oglas ob vsakem zajemu. Če je isti oglas prisoten deset dni zapored, bo v tej datoteki zapisan desetkrat. Namen te datoteke je ohraniti zgodovino opažanj in omogočiti časovno analizo.

| Atribut             | Tip podatka | Obvezno | Primer vrednosti                 | Opis                                                             |
|---------------------|-------------|---------|----------------------------------|------------------------------------------------------------------|
| `listing_id`        | `TEXT`      | da      | `475748`                         | Identifikator oglasa, ki povezuje vrstico z oglasom v `data.csv` |
| `seen_at`           | `TEXT`      | da      | `2026-03-20T08:00:00+00:00`      | Čas konkretnega zajema, pri katerem je bil oglas opažen          |
| `title`             | `TEXT`      | da      | `POMOČ V TRGOVINI`               | Naslov oglasa v trenutku zajema                                  |
| `subtitle`          | `TEXT`      | ne      | `POLNJENJE POLIC`                | Dodatni naslov oglasa v trenutku zajema                          |
| `company`           | `TEXT`      | da      | `MERCATOR D.O.O.`                | Naziv delodajalca                                                |
| `location`          | `TEXT`      | da      | `LJUBLJANA, NOVE FUŽINE 33`      | Lokacija oglasa                                                  |
| `sublocation`       | `TEXT`      | ne      | `HIPERMARKET KRANJ PRIMSKOVO`    | Dodatna lokacija ali objekt                                      |
| `hourly_rate_neto`  | `REAL`      | ne      | `7.73`                           | Neto urna postavka                                               |
| `hourly_rate_bruto` | `REAL`      | ne      | `8.98`                           | Bruto urna postavka                                              |
| `hourly_rate_from`  | `TEXT`      | da      | `7.73 €/h neto (8.98 €/h bruto)` | Surov zapis plačila                                              |
| `payment_type`      | `TEXT`      | da      | `HOURLY`                         | Normaliziran tip plačila                                         |
| `description`       | `TEXT`      | da      | `Iščejo študenta/ko za delo ...` | Opis dela                                                        |
| `open_positions`    | `INTEGER`   | ne      | `2`                              | Število prostih mest                                             |
| `duration`          | `TEXT`      | da      | `DLJE ČASA (ZAČ. IN OBČ. DELO)`  | Trajanje dela                                                    |
| `work_schedule`     | `TEXT`      | da      | `IZMENSKO`                       | Delovnik                                                         |
| `start_date`        | `TEXT`      | ne      | `2026-03-25`                     | Datum začetka dela                                               |
| `contact_name`      | `TEXT`      | da      | `Janez Primer`                   | Ime kontaktne osebe                                              |
| `contact_phone`     | `TEXT`      | ne      | `031123456`                      | Telefonska številka                                              |
| `contact_email`     | `TEXT`      | ne      | `email@domain.com`               | Elektronski naslov                                               |
| `contact_webpage`   | `TEXT`      | ne      | `https://podjetje.si`            | Spletna povezava                                                 |

Datoteka `history.csv` nam omogoča analizo spreminjanja ponudbe skozi čas. Iz nje lahko ugotovimo, kdaj se je določen oglas pojavil, koliko dni je ostal prisoten in kako se je skupna količina oglasov spreminjala med posameznimi zajemi.
