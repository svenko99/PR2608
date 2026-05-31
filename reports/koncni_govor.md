## Del 1 — Problem in podatkovna zbirka *(član 1)*

Pozdravljeni. Analizirali smo trg študentskega dela v Sloveniji.

E-Študentski servis je največji portal za študentsko delo pri nas, ima pa veliko omejitev: pokaže samo trenutno aktivne
oglase. Ko oglas izgine, izgine z njim tudi podatek — API-ja pa portal nima. Iz takega pogleda ne moreš videti, kje so
plače najboljše ali kako se ponudba spreminja skozi čas.

Zato smo to zgodovino zgradili sami, in to je naš glavni prispevek: lastna podatkovna zbirka. Od 12. marca scraper vsak
večer samodejno teče na GitHub Actions in pobere cel portal. Do 30. maja smo tako zbrali **8.574 unikatnih oglasov** od
**4.080 različnih delodajalcev**; pri **94 %** je navedena neto urna postavka.

Podatke hranimo v dveh datotekah — prva ima vrstico na oglas, druga pa beleži vsako spremembo na obstoječem oglasu, na
primer če delodajalec dvigne postavko. Lokacije smo normalizirali v regije, vrsto dela pa določili s klasifikatorjem na
ključnih besedah v naslovu, ki oglase razvrsti v 17 kategorij.

---

## Del 2 — Kaj določa plačo in kdaj iskati *(član 2)*

Prva in morda najbolj presenetljiva ugotovitev: **kje** delaš, skoraj nič ne vpliva na plačo. Mediana neto postavke se
po vseh dvanajstih regijah giblje le med **8,00 € v večini regij** in **8,50 € v Gorenjski** — cel razpon torej komaj 50
centov. Tudi Ljubljana ni izjema. Razlog je sistemski: zakonski minimum okoli 7,73 € na uro deluje kot tla, ki jim
oglasi povsod sledijo.

Pravo razliko prinese **vrsta dela**. Poučevanje in inštrukcije imajo mediano **12 € na uro**, promocije skoraj 10,
gostinstvo dobrih 8, na dnu pa je trgovina in prodaja s **7,80 €**. Razpon med panogami je več kot **4 €** — torej
osemkrat večji kot med regijami. Sporočilo za študenta je preprosto: bolj kot *kje* delaš, šteje, *kaj* delaš.

In še en praktičen nasvet, kdaj sploh gledati portal: daleč največ novih oglasov pride v **ponedeljek**, okoli 120 na
dan, čez teden pade na sto, ob **nedeljah** pa nove ponudbe praktično ni. Splača se torej preveriti v ponedeljek.

---

## Del 3 — Dinamika trga: dvigi plač in razdrobljenost *(član 3)*

Ker beležimo tudi spremembe na oglasih, smo lahko pogledali, kako se postavke premikajo skozi čas. Rezultat je skoraj
enoznačen: med **405 zaznanimi spremembami** urne postavke je bilo **403 dvigov in le 2 znižanji** — plače gredo
praktično samo navzgor. Tipičen dvig je **50 centov**, največji v zbirki kar **7 €**. In dvigi ne pridejo takoj:
polovica se jih zgodi šele med 9. in 56. dnevom po objavi, mediana je pri **27 dneh**. Delodajalec torej počaka nekaj
tednov slabega odziva in šele nato zviša ponudbo — pri oglasu, ki dolgo visi, se včasih splača počakati.

Pogledali smo tudi, kdo sploh objavlja. Trg je izjemno **razdrobljen**: med 4.080 delodajalci jih ima skoraj **64 % le
en sam oglas**. Največji, Mercator z 420 oglasi, pokriva komaj **4,9 %** trga, deset največjih skupaj pa **dobrih 11 %**.
Geografsko je slika ravno obratna — skoraj **polovica vseh oglasov** je v osrednjeslovenski regiji.

---

## Del 4 — Napovedovanje plače in metoda *(član 4)*

Najbolj nas je zanimalo, ali lahko plačo napovemo vnaprej. Plače smo razvrstili v tri razrede — **nizka, srednja, visoka
** — in zgradili tri modele.

Osnovni "baseline", ki vedno ugiba najpogostejši razred, zadene **37 %**. Model na strukturiranih atributih — vrsta
dela, regija, urnik, trajanje — to dvigne na **skoraj 50 %**. Najbolje pa se odreže model, ki bere kar **celoten opis** oglasa:
doseže **dobrih 53 %**. Z drugimi besedami, prosto besedilo opisa nosi informacijo o plači, ki je suhi atributi ne ujamejo.

Glede metode, da boste vedeli, kaj smo uporabili: za napoved smo primerjali **logistično regresijo** in **naivni Bayes**,
besedilo pa predstavili z vektorizacijo **TF-IDF**. Modele smo trenirali na 80 % podatkov in jih preverili na preostalih 20 %,
kakovost pa merili po posameznih razredih, ne le s skupno točnostjo. Najmočnejše besede potrdijo intuicijo: pri visoki
plači izstopajo *poučevanje*, *trženje*, *promocija*, pri nizki pa *prodaja* in *dostava*.

---

## Del 5 — Aplikacija, omejitve in nadaljnje delo *(član 5)*

Vse skupaj smo zapakirali v interaktivno **Streamlit aplikacijo** s petimi stranmi: pregled zbirke na zemljevidu,
primerjava plač po atributih in besednih značkah, dinamika trga in napovedovalec plače, kjer vpišeš svoj opis dela in
dobiš napovedan razred postavke ter podobne oglase. Dostopna je na **pr2608.streamlit.app**.

Seveda imamo omejitve. Dva meseca in pol je za nekatere časovne hipoteze prekratko — recimo, ali se bolje plačani oglasi
hitreje zapolnijo, ne moremo zanesljivo odgovoriti, ker je ob koncu zbiranja še **43 % oglasov aktivnih**. Pri
napovednem modelu tudi sami priznamo blago obliko "label leakage", ki ga bomo v naslednji iteraciji odpravili.

In morda najpomembnejše: **scraper pustimo teči naprej**. Pri približno 113 novih oglasih na dan bi v enem letu nastala
zbirka okoli **41.000 oglasov**. To zbirko nameravamo **predati naslednji generaciji** študentov, da bodo lahko delali
analize, ki jih mi v dveh mesecih še ne moremo — sezonska nihanja, dolgoročne trende plač in dinamiko podjetij.

Hvala za pozornost.
