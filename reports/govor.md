Vir naših podatkov je aplikacija e-Študentskega servisa iz katere vsak dan avtomatsko zajemamo javno dostopne oglase za študentsko delo. Podatke hranimo v dveh tabelah: v tabeli data, ki beleži podatke o oglasih, in v tabeli changes, ki beleži zaznane spremembe pri posameznem oglasu.

Glavni namen našega zbiranja je analiza trga študentskega dela v Sloveniji, odkrivanje povezav med lastnostmi oglasov ter tako podpora študentom pri izbiri študentskega dela. 

Večina podatkov o oglasih, ki jih hranimo je tipa je tekstovnih (tipa text; to so naslov, podjetje, lokacija, tip plačila, opis, čas trajanja, delovnik, datum pričetka, čas prvega in zadnjega opažanja, podatki o spremembi oglasa). Urno postavko hranimo kot decimalno število (tipa real), id oglasa in število prostih mest pa kot celo število (integer).  Imamo tako strukturirane podatke (npr. opis) kot tudi nestrukturirane (npr. urna postavka).

Trenutno imamo shranjenih več kot 4400 oglasov, kot pa smo že povedali, se oglasi z vsakodnevnim zajemom dodajo, tako da jih do konca raziskovanja pričakujemo še več in bodo tudi analize lahko natančnejše. Obvezni podatki pri vsakem oglasu so id, naslov, podjetje, čas prvega in zadnjega opažanja oglasa ter podatki o morebitni spremembi posameznega oglasa. Ostali podatki so lahko tudi manjkajoči, na kar moramo biti pozorni pri raziskovanju.

Da so nekateri podatki postali uporabnejši za analize smo se lotili tudi nekaj predprocesiranja – Lokacijo smo iz surove oblike normalizirali v ime naselja in statistične regije, kjer se bo študentsko delo izvajalo. Normalizirali smo s pomočjo ustvarjene tabele, ki povezuje naselja, občine in regije[slika]. Ti podatki bodo tako uporabnejši pri analiziranju oglasov glede na njihovo lokacijo. Iz surove oblike smo normalizirali tudi zapis plačila na oglasu, tako da smo dobili normaliziran tip plačila (na uro, na projekt, na izlet, na dogodek,  po dogovoru).

V okviru analize želimo odgovoriti na naslednja vprašanja:
•	Ali delodajalci dvigujejo plače, ko oglasa ne morejo zapolniti?
•	Katere lastnosti imajo bolje plačani oglasi?
•	Kje so dela najbolj plačana?

Raziskave z namenom pridobivanja odgovorov na vprašanja, ki nas zanimajo izvajamo v jupyter labu v skupnem zvezku. Najprej smo naredili osnovne statistike, ki prikažejo ključne lastnosti podatkovne zbirke nato pa smo se lotili vprašanj. Pri vsakem vprašanju poleg analize naredimo tudi vizualizacijo, tako da so rezultati jasno vidni. 

Pri raziskovanju vprašanja dvigovanja plač smo proučili spremembe neto urne postavke ter čas ko so se zgodile. Po dozdajšnji analizi je pri čisto vseh spremembah prišlo do zvišanja, najpogosteje po okoli 15 dneh od objave oglasa za okoli 1€. Iz tega lahko sklepamo, da delodajalci dvigujejo plače, ko oglasa ne morejo zapolniti, za natančnejšo analizo potrebujemo še dodatne podatke. 

Pri iskanju lastnosti bolje plačanih oglasov smo primerjali povprečno neto urno postavko  glede na različne atribute oglasa, uporabili smo oglase ki imajo tip plačila hourly. Glede na kategorijo dela smo ugotovili da so najvišje postavke v promociji, najnižje pa v proizvodnji. Zanimivo je tudi, da dela z manj prostimi mesti ne ponujajo višje postavke. Glede na regijo imajo najvišjo postavko osrednjeslovenska, gorenjska in goriška, razlike med njimi pa niso zelo izrazite.

Ostale zanimive ugotovitve, ki smo jih odkrili so, da se oglasi ne objavljajo ob vikendih, najvišja urna postavka ki smo jo zaznali je 60€ in sicer za igranje. Največ oglasov je objavil Mercator (188), sledita mu Lidl(101) in Alpe-Panon(71). Izrazito največ oglasov je objavljenih v osrednjeslovenski regiji (1915), sledita ji Gorenska (481) in Podravska (455).