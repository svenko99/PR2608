# Identifikacija vzorcev uspešnosti in tveganja stečaja pri slovenskih podjetjih

## Opis problema
V našem projektu se bomo ukvarjali z identifikacijo ključnih lastnosti in vzorcev, ki ločujejo uspešna slovenska podjetja od tistih, ki končajo v stečaju. Na podlagi finančnih, kadrovskih, poslovnih ter drugih podatkov želimo odkriti, kateri dejavniki (npr. velikost podjetja, panoga, lokacija, prisotnost tujih investitorjev ipd.) pomembno prispevajo k dolgoročni uspešnosti podjetja oziroma vodijo v njegov stečaj.

S tem želimo ponuditi čimbolj uporabne vpoglede za podjetnike in investitorje, tako da imajo vpogled na katere lastnosti morajo biti ob poslovanju pozorni, tudi takšne, ki morda na prvi pogled niso tako očitne.

Za podatke smo vzeli prva in zadnja 3 leta delujočih podjetij (za tista, ki imajo tako dolg čas obstoja), kot tudi podjetij, ki so šla v stečaj. Menimo, da se ključni podatki, ki prikazujejo ali bo podjetje uspešno nahajajo v prvih letih delovanja, tako bomo lahko tudi predvidevali, kako bodo novejša podjetja lahko končala. Zadnja 3 leta podatkov, bo pa namenjeno iskanju korelacij (ne)uspešnih podjetij.

## Vir in oblika podatkov
Podatke za projekt bomo črpali iz podatkovne zbirke Poslovnega registra Slovenije (PRS), ki jo vodi [AJPES](https://www.ajpes.si/). V PRS so zabeleženi podatki o podjetjih, samostojnih podjetnikih, podružnicah tujih podjetij ter drugih organizacijah, ki opravljajo registrirano dejavnost v Sloveniji.

AJPES ima javno dostopen [REST API](https://www.ajpes.si/restPrsInfo/swagger/index.html), ki pa je tudi dobro dokumentiran v [navodilih za razvijalce](https://www.ajpes.si/Doc/AJPES/Za_razvijalce/restPrsInfo_Opis_servisa_za_razvijalce.pdf).

### Pridobivanje podatkov
Za uporabo API-ja je potrebno ustvariti račun na AJPES portalu. API nam bo podatke vračal v JSON formatu, za to poskrbimo tako, da nastavimo `xml=false` URL parametrih HTTP zahteveve.

Primer HTTP zahteve za pridobitev podatkov preko AJPES API-ja:
```sh
curl -X 'POST' \
  'https://www.ajpes.si/restPrsInfo/checkSredstva' \
  -H 'accept: text/plain' \
  -H 'Content-Type: application/json' \
  -d '{
  "uporabnik": "string",
  "geslo": "string"
}'
```

### Oblika podatkov
API vrača podatke v naprej definiranih shemah oziroma DTO-jih, katere najdemo [na dnu Swagger strani](https://www.ajpes.si/restPrsInfo/swagger/index.html#model-AktivnostType).




## Cilj projekta
Pri projektu želimo odgovoriti na:
- Katere korelacije in vzorci obstajajo med značilnostmi (ne)uspešnih podjetij?
- Obstajajo kakšne ponavljajoče se napake podjetij, ki peljejo v veliko tveganje stečaja?
- Kako vpliva lokacija podjetja, ali moramo biti v različnih regijah pozorni na specifične stvari?
- Ali lahko predvidimo, kako bo podjetje končalo, glede na začetna 3 leta poslovanja?
