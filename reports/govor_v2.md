Naš projekt analizira trg študentskega dela v Sloveniji na podlagi oglasov e-Študentskega servisa. Cilj je iz javno dostopnih podatkov izluščiti uporabne ugotovitve, ki bi študentom pomagale pri iskanju dela, hkrati pa pokazati, kaj se na tem trgu dejansko dogaja.



## Problem in motivacija



E-Študentski servis je največji portal za študentsko delo pri nas. Vsak dan so na njem objavljeni oglasi z informacijami o delodajalcu, lokaciji, plačilu, delovniku in opisu dela. Problem je, da portal prikazuje le posamezne oglase — uporabnik jih lahko brska in filtrira, ne more pa opazovati vzorcev v celotni ponudbi. Nihče ne ve, kje se najbolje plača, kako hitro se oglasi zapolnijo ali katere veščine so najbolj iskane.



Poleg tega portal prikazuje samo trenutno aktivne oglase. Ko oglas izgine, podatek o njem izgine z njim. Brez dnevnega zajemanja torej sploh ne moremo spremljati dinamike trga — ne vemo, koliko časa oglasi ostanejo aktivni, ali se njihove lastnosti spreminjajo, ali pa kako hitro se zapolnijo.



Zato smo se odločili, da bomo te podatke sistematično zbirali, čistili in analizirali. Iz vidika podatkovnega rudarjenja je problem zanimiv, ker vsebuje kombinacijo strukturiranih podatkov, kot so urna postavka ali lokacija, in nestrukturiranih, kot je prosti opis dela.



## Zbiranje podatkov



Od začetka marca avtomatsko, vsak dan ob osmih zvečer, scrapamo celoten portal s pomočjo Pythonove knjižnice BeautifulSoup. Scraper prebere vse strani rezultatov, izvleče podatke in jih shrani v dve CSV datoteki. Prva, `data.csv`, hrani vse unikatne oglase z njihovimi lastnostmi — naslov, podjetje, lokacija, urna postavka, opis, delovnik, trajanje in časi opažanja. Druga, `changes.csv`, beleži spremembe pri obstoječih oglasih med zaporednimi zajemi — na primer, če se pri nekem oglasu spremeni urna postavka, se to zabeleži kot ločena vrstica.



Do danes smo zbrali več kot 4400 unikatnih oglasov. Od teh ima 93 % navedeno neto urno postavko, preostali pa navajajo plačilo po dogovoru. Ugotovili smo tudi, da portal novih oglasov ne objavlja ob vikendih — med tednom se v povprečju pojavi 94 novih oglasov na dan, ob sobotah in nedeljah pa nič.



V okviru predprocesiranja smo surove lokacije normalizirali v imena naselij in dvanajst statističnih regij s pomočjo referenčne tabele, ki povezuje naselja, občine in regije. Zapise plačil smo normalizirali v standardizirane kategorije — urno, projektno, po dogovoru in druge. To predprocesiranje nam omogoča primerljive agregacije po regijah, mestih in kategorijah del.



## Ključne ugotovitve



Poglejmo, kaj smo iz teh podatkov ugotovili.



**Plače po regijah.** Mediana neto urne postavke med vsemi oglasi z urnim plačilom znaša 8 evrov, povprečje pa 8,69. Najvišja zabeležena postavka je kar 60 evrov. Razlika med povprečjem in mediano nakazuje, da porazdelitev vsebuje osamelce, ki dvigujejo povprečje navzgor. Zanimivo pa je, da so razlike med regijami presenetljivo majhne — razpon median je le 42 centov, od 7,73 v Zasavski do 8,15 v Osrednjeslovenski regiji. To je verjetno posledica zakonsko določenega minimuma za študentsko delo, ki zoži prostor za regionalne razlike. Če pričakujete, da se v Ljubljani bistveno bolje plača kot drugod — podatki tega ne potrjujejo.



**Vrsta dela pa šteje bistveno več.** Razpon median po kategorijah dela je 3,45 evra — to je osemkrat več kot razpon po regijah. Najvišjo mediano dosegajo poučevanje in inštrukcije z 11,19 evra, sledijo promocijske aktivnosti z 10 evri, najnižje pa so proizvodna dela s 7,74. Torej, če študent želi bolje plačano delo, je bolj kot lokacija pomembno, kakšno delo opravlja. Zanimivo je tudi, da število prostih mest na urno postavko ne vpliva — mediana znaša 8 evrov ne glede na to, ali ima oglas eno, do pet ali več kot pet prostih mest.



**Dvigovanje plač.** Iz datoteke sprememb smo proučili, ali delodajalci dvigujejo urne postavke, ko oglasa ne morejo zapolniti. Rezultat je bil jasen: med vsemi zaznanimi spremembami neto urne postavke ni bilo niti enega znižanja — vse so bili dvigi. Povprečen dvig znaša približno 1 evro, največji pa kar 6 evrov. Do dvigov praviloma pride po približno 14 dneh od objave, kar nakazuje, da delodajalci zvišajo ponudbo šele, ko začetna postavka ne pritegne dovolj kandidatov. Za študente je to uporabna informacija — pri nekaterih oglasih se dobesedno splača počakati na boljšo ponudbo.



**Struktura trga.** Na portalu objavlja skoraj 2600 različnih podjetij. Največ oglasov je objavil Mercator s 188 oglasi, sledita Lidl s 101 in Alpe-Panon z 71. Kljub temu vsa tri skupaj pokrijejo le 8 % celotne ponudbe, deset največjih pa le 12 %. Trg je izrazito fragmentiran — kar 73 % podjetij ima le en objavljen oglas. To je pričakovano, saj večina manjših podjetij študentsko delo potrebuje le občasno. Geografsko izrazito prevladuje Ljubljana s 1400 oglasi, sledita Maribor z 265 in Kranj s 127. Osrednjeslovenska regija sama zajema 43 % vseh oglasov, kar odraža koncentracijo gospodarskih dejavnosti v prestolnici in okolici.



**Programski jeziki.** Z regex analizo opisov smo preverili, kolikšen delež oglasov omenja kakšen programski jezik. Le okoli 1 % jih eksplicitno navaja programski jezik, kar kaže, da je povpraševanje po programerskih veščinah na trgu študentskega dela majhno. Med omenjenimi jeziki prevladuje Java s 23 oglasi, sledijo Python s 16, SQL z 9 in JavaScript z 8.



**Plačilo in hitrost zapolnjevanja.** Preverili smo tudi hipotezo, da se bolje plačani oglasi zapolnijo hitreje in zato na portalu ostanejo krajši čas. Korelacija med urno postavko in trajanjem prisotnosti oglasa je praktično nič, trendna črta pa je skoraj vodoravna. Višje plačilo torej ne vodi do hitrejšega zapolnjevanja — vsaj za zdaj. Ker ob času analize mnogi oglasi še ostajajo aktivni, bomo to hipotezo ponovno preverili, ko bo obdobje opazovanja daljše.



## Nadaljnje delo



Zbiranje podatkov se nadaljuje in bo trajalo do konca semestra. Daljše obdobje opazovanja bo izboljšalo zanesljivost časovnih analiz, zlasti o trajanju oglasov glede na vrsto dela. V končnem poročilu načrtujemo poglobljeno besedilno analizo opisov del, podrobnejšo primerjavo tipov del po regijah ter analizo plač glede na kombinacije več atributov hkrati.



Hvala za pozornost.

