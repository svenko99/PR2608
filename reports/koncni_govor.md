## Del 1 — Problem in podatkovna zbirka *(član 1)*

Pozdravljeni. V okviru našega projekta smo analizirali trg študentskega dela v Sloveniji z analizo oglasov na
e-Študentskem servisu.

E-Študentski servis je največji portal za študentsko delo pri nas, ki pa ima eno precej veliko omejitev: prikazuje samo
trenutno aktivne
oglase. Ko oglas izgine, izginejo z njim tudi vsi njegovi podatki — API-ja pa portal nima. Iz takega pogleda tako nimamo
pregleda nad analizo ponudbe (npr. kje so postavke najvišje)
ali nad tem kako se ponudba spreminja skozi čas.

Zato smo to zgodovino zgradili sami, in to je naš glavni prispevek: lastna podatkovna zbirka. Od 12. marca scraper vsak
večer samodejno teče preko GitHub Actions in pobere oglase iz portala. Do 30. maja smo zbrali **8.574 unikatnih oglasov
** od
**4.080 različnih delodajalcev**, ključne ugotovitve iz teh podatkov bomo predstavili v nadaljevanju; na aplikaciji pa
imamo najnovejše podatke.

Podatke hranimo v dveh datotekah — prva beleži vse navedene podatke o posameznem oglasu, druga pa beleži vsako spremembo
na obstoječem oglasu, na
primer če delodajalec dvigne postavko. Lokacije smo normalizirali v regije, vrsto dela pa določili s klasifikatorjem na
ključnih besedah v naslovu, ki oglase razvrsti v 17 kategorij.

---

## Del 2 — Kaj določa plačo in kdaj iskati *(član 2)*

Prva in morda najbolj presenetljiva ugotovitev: **kje** delaš, skoraj nič ne vpliva na plačo. Mediana neto postavke se
po vseh dvanajstih regijah giblje le med **8,00 € v večini regij** in **8,50 € v Gorenjski** — cel razpon torej komaj 50
centov. Tudi Ljubljana ni izjema. 

Pravo razliko prinese **vrsta dela**. Poučevanje in inštrukcije imajo mediano **12 € na uro**, promocije skoraj 10,
gostinstvo dobrih 8, na dnu pa je trgovina in prodaja s **7,80 €**. Razpon med vrsto dela je več kot **4 €** — torej
osemkrat večji kot med regijami. Iz tega lahko pridemo do ugotovitve, da je bolj važno VRSTA dela, koker KRAJ dela.

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
en sam oglas**. Največji, Mercator z 420 oglasi, pokriva komaj **4,9 %** trga, deset največjih skupaj pa **dobrih 11 %
**.
Geografsko je slika ravno obratna — skoraj **polovica vseh oglasov** je v osrednjeslovenski regiji.

---

## Del 4 — Napovedovanje plače in metoda *(član 4)*

Najbolj nas je zanimalo ali lahko plačo napovemo vnaprej, zato smo plače smo razdelili v tri razrede — nizka, srednja, visoka — in primerjali tri modele.
Nizka plača je do 8,00 €/h, srednja od 8,00 do 8,61 €/h, visoka pa nad 8,61 €/h.

Začeli smo s baseline modelom, ki vedno ugiba najpogostejši razred. Ta zadane v 37% primerov, kar smo vzeli za izhodišče. Model na strukturiranih atributih (torej vrsta dela, regija, urnika in trajanje), zadane v skoraj 50 %, najboljši pa je model, ki prebere kar celoten opis oglasa in doseže dobrih 53 %. To nam pove, da prosto besedilo opisa nosi najvec informacij o plači samega dela.

Za napoved smo primerjali logistično regresijo in naivni Bayes, besedilo pa vektorizirali s TF-IDF. Trenirali smo na 80 % podatkov, testirali na 20 %, evalvirali pa po posameznih razredih — ne le s skupno točnostjo. Rezultati potrdijo, da pri visoki plači izstopajo besede *poučevanje*, *trženje*, *promocija*, pri nizki pa *prodaja* in *dostava*.

---

## Del 5 — Aplikacija, omejitve in nadaljnje delo *(član 5)*

Vse skupaj smo zapakirali v interaktivno **Streamlit aplikacijo** s petimi stranmi, ki smo vam jo kazali tekom
predstavitve.

Seveda imama naša seminarska naloga par omejitev. Dva meseca in pol je za nekatere časovne hipoteze prekratko — recimo,
ali se bolje plačani oglasi hitreje zapolnijo, ne moremo zanesljivo odgovoriti, ker je ob koncu zbiranja še **43 %
oglasov aktivnih**.

In morda najpomembnejše: **scraper pustimo teči naprej**. Pri približno 113 novih oglasih na dan bi v enem letu nastala
zbirka okoli **41.000 oglasov**. To zbirko nameravamo **predati naslednji generaciji** študentov, da bodo lahko delali
analize, ki jih mi v dveh mesecih še ne moremo — sezonska nihanja in dolgoročne trende plač.

Hvala za pozornost.
