# TODO <!--Identifikacija vzorcev uspešnosti in tveganja stečaja pri slovenskih podjetjih -->

## Opis problema
e-Študentski servis je priljubljena platforma, katero uporabljajo dijaki in študenti na območju celotne Slovenije za iskanje raznovrstnih študentskih del, delodajalci pa za objavo le teh. 
Problem, ki ga obravnavamo, je pomanjkanje celovitejšega vpogleda v vzorce in trende teh podatkov. To otežuje učinkovito povezovanje študentov z delodajalci, vodi do neučinkovitega zaposlovanja in neizkoriščenih priložnosti na obeh straneh. 

Študenti pri iskanju dela pogosto upoštevajo številne dejavnike, ki vplivajo na njihovo odločitev. Med najpogostejše sodijo višina plače, delovni čas, vrsta dela, zahtevane veščine ter tudi lokacija delovnega mesta. Vendar pa se pogosto zgodi, da se medtem, ko študent razmišlja o določeni priložnosti ali išče druge možnosti, delovno mesto že zapolni in ni več na voljo.

Poleg tega trenutno nimamo enotnega pregleda podatkov, ki bi študentom omogočal hitrejšo in bolj učinkovito odločitev pri izbiri dela. Takšne informacije bi lahko pomembno pripomogle k boljšemu razumevanju trga študentskega dela.

Podjetjem, ki ponujajo študentsko delo ali prakso, bi prav tako koristilo, če bi imela vpogled v to, katere dejavnike študenti najpogosteje upoštevajo pri izbiri dela, še posebej v posameznih regijah. Na podlagi takšnih podatkov bi lahko podjetja svoje ponudbe oziroma oglase prilagodila interesom in pričakovanjem študentov ter tako povečala zanimanje za ponujena delovna mesta.

## Cilj projekta
Naš cilj je analizirati ponudbe del na e-Študentskem servisu in iz njih pridobiti nekaj uporabne statistike. S tem želimo pridobiti koristne informacije tako za študente, kot tudi za delodajalce.<br>
Pri projektu želimo odgovoriti na maslednja vprašanja:
- V katerih regijah je največja in najbolj plačana ponudba študentkih del?
- Katera so najbolj iskana dela se v posameznih regijah?
- Kakšne lastnosti imajo oglasi za delo, ki plačajo najbolje - tip dela, delovnik (dopoldan/popoldan/med vikendi), trajanje dela...?
- Katere veščine zahtevajo najbolje plačana dela?
- Koliko dolgo so oglasi objavljeni, gledena vrsto dela (ali obstaja povezava z vrsto, urno postavko, delovnikom...)?
- Kakšna dela so najpopularnejša med študenti - so najhitreje odstranjena iz oglasov?

## Vir in oblika podatkov

Podatke za projekt bomo črpali iz [e-Študentskega servisa](https://studentski-servis.com/studenti). Ker ne ponujajo brezplačnega javno dostopnega API-ja bomo podatke scrapali iz njihove spletne aplikacije. Iz datotetke [`robots.txt`](https://studentski-servis.com/robots.txt) ugotovimo, da je scrapanje podatkov dovoljeno, saj vsebuje `User-agent: *` in `Allow: /`.

### Pridobivanje podatkov
Za pridobivanje podatkov iz spletne aplikacije e-Študentski servis bomo uporabili Pythonovo knjižnico [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).

Pridobljene podatke bomo shranjevali v [data.csv](/data/data.csv). Če bo podatkov preveč, jih bomo shranjevali v relacijsko podatkovno bazo v oblaku (npr. [PostgreSQL na Azure](https://azure.microsoft.com/en-us/products/postgresql/)).<br>
Pričakujemo največ 5000 unikatnih oglasov. V času pisanja tega dokumenta (11.3.2026) je na študentskem servisu 2457 aktivnih oglasov.

Ker je v aplikaciji v danem času mogoče videti le trenutno objavljene oglase, želimo pa spremljati tudi njihovo dodajanje in odstranjevanje, bomo podatke zajemali vsak dan ob isti uri. Tako bomo v nekaj mesecih zgradili časovno zbirko oglasov s študentskega servisa.<br>
Vsak dan bomo zajeli celoten e-Študentski servis. Pri oglasih, ki smo jih že videli, bomo posodobili atribut `last_seen`, nove oglase pa bomo dodali v zbirko.



Podatke bomo pridobili iz preko URL-ja, ki je sestavlejn iz večih query parametrov, ki predstavljajo filtre. Primer:
```
https://studentski-servis.com/studenti/prosta-dela?
page=1&
isci=1&
sort=&
dd1=1&
do1=1&
dm1s=1&
regija%5B%5D=ljubljana-z-okolico&
regija%5B%5D=kranj-z-okolico&
skD%5B%5D=A104&
skD%5B%5D=A078&
skD%5B%5D=A047&
tdd1=1&
tdv1=1&
hourlyratefrom=7.77&
hourlyrateto=8.88&
hourly_rate=7.8%3B8.9
```
Obisk/HTTP klic zgornjega URL-ja nam vrne HTML stran, kateri je generiran na strežniku. To je HTML, ki vsebuje podatke, ki nas zanimajo.<br>
Da smo dobili zgornji URL, smo preko uporabniškega vmesnika izbrali filtre:
- *Danes objavlejna* in *Daljša od 10 dni*
- Znotraj regije *Ljubljana z okolico* in *Kranj z okolico*
- Vrsta dela *Programiranje*, *Marketing*  ali *Strežba*
- Delovni čas *Dopoldan* ali *Med vikendi*
- Neto urna postavka med *7.77* in *8.88* €/h

Ker bomo scrapali, bi radi dobili vse možne ključe in njihove vrednosti, ki jih lahko pošljemo v HTTP zahtevi. Te podatke dobimo tako, da analiziramo HTML formo:

<details>
<summary><b>Filttiranje podatkov</b></summary>

| Query parameter | Vrednost oz. tip | Primer | Opis |
|----------------|---------------|--------|------|
| `page` | `INTEGER` | `1` | Številka strani |
| `isci` | `1` | `1` | Podatek mora biti obvezno prisoten za iskanje |
| `sort` | `""` \| `urna-postavka` \| `vrsta-dela` \| `prosta-mesta` | `urna-postavka` | Razvrščanje rezultatov |
| `dd1` | `1` | `1` | Filter: danes objavljena |
| `dk1` | `1` | `1` | Filter: kratkotrajna dela |
| `do1` | `1` | `1` | Filter: daljša od 10 dni |
| `dm1` | `1` | `1` | Filter: za mlajše od 18 let |
| `dm1s` | `1` | `1` | Skrito polje, vedno `1` ob izbiri `dm1` |
| `notifications` | `1` | `1` | Filter: dela za katera si obveščen |
| `regija[]` | `TEXT` | `ljubljana-z-okolico` | Regija (možnih več vrednosti, glej spodaj) |
| `skD[]` | `TEXT` | `A078` | Vrsta dela (možnih več vrednosti, glej spodaj) |
| `tdd1` | `1` | `1` | Delovnik: dopoldan |
| `tdp1` | `1` | `1` | Delovnik: popoldan |
| `tdv1` | `1` | `1` | Delovnik: med vikendi |
| `tdi1` | `1` | `1` | Delovnik: izmensko |
| `hourlyratefrom` | `REAL` | `7.77` | Minimalna neto urna postavka (€/h) |
| `hourlyrateto` | `REAL` | `8.88` | Maksimalna neto urna postavka (€/h) |
| `hourly_rate` | `REAL;REAL` | `7.8;8.9` | Razpon urne postavke (redundantno z zgornjima dvema vhodoma) |

#### Filtriranje po regiji `regija[]`

| Vrednost | Opis |
|----------|------|
| `osrednjeslovenska` | Osrednjeslovenska (nadskupina) |
| `ljubljana-z-okolico` | Ljubljana z okolico |
| `domzale-kamnik` | Domžale–Kamnik |
| `grosuplje-z-okolico` | Grosuplje z okolico |
| `vrhnika-z-okolico` | Vrhnika z okolico |
| `podravska` | Podravska (nadskupina) |
| `maribor-z-okolico` | Maribor z okolico |
| `ptuj-z-okolico` | Ptuj z okolico |
| `koroska` | Koroška |
| `pomurska` | Pomurska |
| `savinjska` | Savinjska |
| `zasavska` | Zasavska |
| `gorenjska` | Gorenjska (nadskupina) |
| `kranj-z-okolico` | Kranj z okolico |
| `skofja-loka-z-okolico` | Škofja Loka z okolico |
| `radovljica-z-okolico` | Radovljica z okolico |
| `jesenice-z-okolico` | Jesenice z okolico |
| `goriska` | Goriška |
| `primorsko-notranjska` | Primorsko-notranjska |
| `obalno-kraska` | Obalno-kraška (nadskupina) |
| `koper-z-okolico` | Koper z okolico |
| `izola-z-okolico` | Izola z okolico |
| `piran-z-okolico` | Piran z okolico |
| `kras` | Kras |
| `posavska` | Posavska |
| `dolenjska` | Dolenjska |

#### Filtriranje po vrsti dela: `skD[]`

| Vrednost | Opis | Nadskupina |
|----------|------|------------|
| `014` | strežba | — |
| `A821` | pomoč v strežbi | strežba |
| `A104` | strežba | strežba |
| `A164` | strežba hrane in pijače | strežba |
| `010` | prodaja | — |
| `A022` | blagajnik | prodaja |
| `A014` | delo na bencinskem servisu | prodaja |
| `A841` | delo na stojnici | prodaja |
| `A064` | pobiranje cestnine | prodaja |
| `A065` | pobiranje vstopnine | prodaja |
| `A083` | pomoč pri prodaji | prodaja |
| `A116` | pomoč v trgovini | prodaja |
| `A076` | prodaja | prodaja |
| `002` | fizična dela | — |
| `A006` | arheološka izkopavanja | fizična dela |
| `A010` | čiščenje | fizična dela |
| `A009` | delo v delavnici | fizična dela |
| `A023` | delo v proizvodnji | fizična dela |
| `A024` | delo v skladišču | fizična dela |
| `A036` | delo v tiskarni | fizična dela |
| `A028` | fizična dela | fizična dela |
| `A033` | gradbena dela | fizična dela |
| `A158` | kidanje snega | fizična dela |
| `A142` | mizarska dela | fizična dela |
| `A051` | montaža | fizična dela |
| `A067` | nakladanje / razkladanje | fizična dela |
| `A842` | pastir/-ica | fizična dela |
| `A094` | selitve | fizična dela |
| `A098` | slikopleskarska dela | fizična dela |
| `A110` | težja fizična dela | fizična dela |
| `A126` | vrtnarska dela | fizična dela |
| `A836` | vulkanizerska dela | fizična dela |
| `006` | delo na terenu | — |
| `A018` | delo na terenu | delo na terenu |
| `A043` | kurir/ka | delo na terenu |
| `A062` | pismonoša | delo na terenu |
| `A063` | plakatiranje | delo na terenu |
| `A084` | raznašanje | delo na terenu |
| `A085` | raznašanje časopisov | delo na terenu |
| `A086` | raznašanje reklamnih letakov | delo na terenu |
| `A159` | razvoz | delo na terenu |
| `004` | računalništvo in programiranje | — |
| `A832` | informatika | računalništvo in programiranje |
| `A210` | izdelava in urejanje spletne strani | računalništvo in programiranje |
| `A055` | obdelava podatkov | računalništvo in programiranje |
| `A078` | programiranje | računalništvo in programiranje |
| `A090` | računalniške storitve | računalništvo in programiranje |
| `A095` | servisiranje računalniške opreme | računalništvo in programiranje |
| `013` | gostinstvo in turizem | — |
| `A822` | delo v igralnici | gostinstvo in turizem |
| `A032` | delo v kuhinji | gostinstvo in turizem |
| `A130` | delo v turizmu | gostinstvo in turizem |
| `A075` | krupje/krupjejka | gostinstvo in turizem |
| `A118` | pomoč v kuhinji | gostinstvo in turizem |
| `A161` | portir/ka | gostinstvo in turizem |
| `A160` | sobar/ica | gostinstvo in turizem |
| `A070` | valej/valejka | gostinstvo in turizem |
| `005` | strokovna dela | — |
| `A826` | arheološka dela | strokovna dela |
| `A008` | asistent/ka | strokovna dela |
| `A019` | delo v knjižnici | strokovna dela |
| `A835` | delo v logistiki | strokovna dela |
| `A852` | delo z umetno inteligenco | strokovna dela |
| `A834` | digitalni marketing | strokovna dela |
| `A133` | elektrotehnična dela | strokovna dela |
| `A027` | figurant | strokovna dela |
| `A833` | informacijsko komunikacijska dela | strokovna dela |
| `A824` | inštalacije | strokovna dela |
| `A837` | kontrola kakovosti | strokovna dela |
| `A045` | lektoriranje | strokovna dela |
| `A047` | marketing | strokovna dela |
| `A139` | meritve | strokovna dela |
| `A052` | nastop | strokovna dela |
| `A054` | novinarska dela | strokovna dela |
| `A143` | pomoč na področju marketinga | strokovna dela |
| `A136` | pravne storitve | strokovna dela |
| `A073` | prevajanje | strokovna dela |
| `A079` | projektiranje | strokovna dela |
| `A152` | projektno delo | strokovna dela |
| `A082` | raziskovalno delo | strokovna dela |
| `A088` | restavriranje | strokovna dela |
| `A074` | reševalec/ka iz vode | strokovna dela |
| `A099` | snemanje | strokovna dela |
| `A851` | snemanje in urejanje kratkih videov | strokovna dela |
| `A831` | sojenje tekme | strokovna dela |
| `A103` | stevard/esa | strokovna dela |
| `A844` | strojna dela | strokovna dela |
| `A846` | strojniška dela | strokovna dela |
| `A105` | strokovno delo | strokovna dela |
| `A106` | svetovalec/ka | strokovna dela |
| `A114` | urednik | strokovna dela |
| `A156` | urednik spletnih vsebin | strokovna dela |
| `A155` | urejanje druž. omrežij (fb, in, x, tik tok) | strokovna dela |
| `A124` | vodenje | strokovna dela |
| `008` | promocija | — |
| `A011` | degustacije | promocija |
| `A013` | deljenje letakov | promocija |
| `A017` | delo na sejmu | promocija |
| `A829` | hostes/a | promocija |
| `A080` | promocija | promocija |
| `016` | delo s strankami | — |
| `A003` | animator/ka | delo s strankami |
| `A096` | delo na recepciji | delo s strankami |
| `A150` | delo s strankami | delo s strankami |
| `A839` | delo v loteriji | delo s strankami |
| `A838` | delo v rent a car agenciji | delo s strankami |
| `A015` | helpdesk | delo s strankami |
| `A037` | informator/ka | delo s strankami |
| `A163` | maskota | delo s strankami |
| `A119` | pomoč uporabnikom | delo s strankami |
| `A092` | tehnična pomoč | delo s strankami |
| `A108` | telefonist/ka | delo s strankami |
| `007` | trženje in anketiranje | — |
| `A002` | akviziterska dela | trženje in anketiranje |
| `A004` | anketiranje | trženje in anketiranje |
| `A005` | anketiranje po telefonu | trženje in anketiranje |
| `A042` | klicni center | trženje in anketiranje |
| `A041` | komercialna dela | trženje in anketiranje |
| `A071` | pospeševanje prodaje | trženje in anketiranje |
| `A109` | telefonski marketing | trženje in anketiranje |
| `A113` | trženje | trženje in anketiranje |
| `009` | poučevanje | — |
| `A115` | delo v fitnesu | poučevanje |
| `A825` | delo z otroki | poučevanje |
| `A025` | demonstrator/ka | poučevanje |
| `A038` | inštrukcije | poučevanje |
| `A049` | mentor/ica | poučevanje |
| `A068` | pomočnik vzgojitelja/vzgojiteljice | poučevanje |
| `A072` | poučevanje | poučevanje |
| `A125` | predavanje | poučevanje |
| `A112` | trener/ka | poučevanje |
| `A121` | učitelj/ica plavanja | poučevanje |
| `A077` | učitelj/ica smučanja | poučevanje |
| `A120` | vaditelj/ica | poučevanje |
| `A122` | varstvo | poučevanje |
| `001` | lažja dela | — |
| `A061` | aranžiranje | lažja dela |
| `A012` | deklariranje | lažja dela |
| `A149` | delo v avtopralnici | lažja dela |
| `A840` | delo v pekarni | lažja dela |
| `A029` | dežurstvo | lažja dela |
| `A026` | etiketiranje | lažja dela |
| `A650` | inventura | lažja dela |
| `A100` | kuvertiranje | lažja dela |
| `A044` | lažja fizična dela | lažja dela |
| `A046` | lepljenje | lažja dela |
| `A060` | maska | lažja dela |
| `A050` | model | lažja dela |
| `A059` | pakiranje | lažja dela |
| `A827` | parkiranje vozil | lažja dela |
| `A066` | polnjenje polic | lažja dela |
| `A144` | pomoč v skladišču in prod. centrih | lažja dela |
| `A678` | reditelj | lažja dela |
| `A093` | ročna dela | lažja dela |
| `A097` | sestavljanje | lažja dela |
| `A101` | sortiranje | lažja dela |
| `A141` | statist | lažja dela |
| `A107` | štetje prometa | lažja dela |
| `A151` | urejanje okolice | lažja dela |
| `A134` | vlaganje | lažja dela |
| `A127` | vzdrževanje | lažja dela |
| `A132` | zlaganje | lažja dela |
| `003` | administrativna dela | — |
| `A001` | administrativna dela | administrativna dela |
| `A007` | arhivsko delo | administrativna dela |
| `A853` | asistent/ka v kadrovski službi | administrativna dela |
| `A016` | delo na računalniku | administrativna dela |
| `A031` | fotokopiranje | administrativna dela |
| `A830` | klasifikacija ključnih besed | administrativna dela |
| `A040` | knjigovodska dela | administrativna dela |
| `A849` | obdelava in odprema spletnih naročil | administrativna dela |
| `A058` | organizacijska dela | administrativna dela |
| `A135` | popis podatkov | administrativna dela |
| `A081` | računovodska dela | administrativna dela |
| `A154` | špedicijska dela | administrativna dela |
| `A138` | tajniška dela | administrativna dela |
| `A117` | urejanje besedil | administrativna dela |
| `A123` | vnos podatkov v računalnik | administrativna dela |
| `A140` | zahtevna administrativna dela | administrativna dela |
| `015` | oblikovanje | — |
| `A030` | fotografiranje | oblikovanje |
| `A034` | grafična dela | oblikovanje |
| `A153` | grafična priprava za tisk | oblikovanje |
| `A069` | grafično oblikovanje | oblikovanje |
| `A056` | oblikovanje | oblikovanje |
| `A091` | risanje | oblikovanje |
| `012` | zdravstvo in farmacija | — |
| `A147` | delo v farmaciji | zdravstvo in farmacija |
| `A020` | delo v laboratoriju | zdravstvo in farmacija |
| `A021` | delo v lekarni | zdravstvo in farmacija |
| `A148` | delo v ordinaciji | zdravstvo in farmacija |
| `A157` | delo v velnesu | zdravstvo in farmacija |
| `A146` | delo v zdravstvu | zdravstvo in farmacija |
| `A039` | fizioterapija | zdravstvo in farmacija |
| `A848` | jemanje brisov | zdravstvo in farmacija |
| `A850` | kineziolog/inja | zdravstvo in farmacija |
| `A145` | kozmetične storitve | zdravstvo in farmacija |
| `A162` | maser/ka | zdravstvo in farmacija |
| `A048` | medicinska sestra | zdravstvo in farmacija |
| `A053` | negovanje | zdravstvo in farmacija |
| `A847` | pomoč pri oskrbi stanovalcev | zdravstvo in farmacija |
| `A843` | pomoč pri triaži | zdravstvo in farmacija |
| `A102` | spremljevalec/spremljevalka | zdravstvo in farmacija |
| `A087` | zdravstvena nega | zdravstvo in farmacija |
| `A131` | zdravstveni tehnik | zdravstvo in farmacija |
</details>


### Oblika podatkov
Objave oglasov so v spletni aplikaciji združene v več HTML strani, strani od 1 do n. Stran rezultatov nam doloca `page` (glej zgoraj). Podatki posameznih objav so zapisani v spodnji tabeli:

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
| `first_seen`     | `TEXT`      | ✅      | `2026-03-11T08:00:00+00:00`                               | Čas ob katerem je biu oglas prvič viden na servisu (~dodan)              |
| `last_seen`      | `TEXT`      | ✅      | `2026-03-20T08:00:00+00:00`                               | Čas ob katerem je biu oglas zadnjič viden na servisu              |

