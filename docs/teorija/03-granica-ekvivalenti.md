# 3. Granica sustava i ekvivalenti

Mrežni model koji je dostavljen od strane HOPS-a sadrži samo hrvatski prijenosni sustav. 
Međutim, Hrvatska je s 35 prekograničnih vodova u pogonu spojena s četiri susjedna sustava
i tok snage kroz hrvatsku mrežu ovisi i o tome što se događa s druge strane. U ovom dijelu
ćemo pregledati kako je modeliran sustav, granice i granični ekvivalenti. 

## 3.1. Kako je granica opisana u modelu i što nam sve govori

### 3.1.1. X-čvorišta

Prekogranični vod spaja hrvatsku trafostanicu sa trafostanicom u sjednom sustavu. U 
modelu je takav vod podijeljen na dvije polovice fiktivnom sabirnicom na mjestu granice
koja se zove X-sabirnica (engl. boundary node)

```
  hrvatska sabirnica          X-sabirnica            sabirnica susjeda
  60032 HERNES11  ────────────  99993 XER_PE12  ────────────  311080 (Pécs)
                  hrvatska polovica              vanjska polovica
                  (u modelu)                     (vod postoji, čvorište ne postoji)
```

Ovakva podjela dolazi iz načina na koji ENTSO-E spaja modele - svaki operator modelira 
svoju mrežu do X-sabirnica na granici, a zajednički model nastaje spajanjem pojedinačnih
modela na tim X-sabirnicama. Dvije polovice voda imaju R,X,B parametre razmjerne duljini
svakog dijela. 

### 3.1.2. Što imamo, što ne?

| Podatak | Zapisan? | Napomena |
|---|---|---|
| X-sabirnica, s naponom (VM, VA) | da | napon iz spremljenog rješenja |
| hrvatska polovica voda (R, X, B, RATE, STAT) | da | |
| vanjska polovica voda (R, X, B, RATE, STAT) | da | zapis postoji u bloku grana |
| sabirnica susjeda na kraju vanjske polovice | **ne** | broj sabirnice se pojavljuje samo u zapisu grane |
| mreža susjeda (vodovi, transformatori, elektrane, tereti) | **ne** | |
| teret, generator ili shunt na X-sabirnici | **ne** | specificirana injekcija na X-sabirnici je nula |
| razmjena po vodu (MW, Mvar) | **ne** | izvodi se iz napona — t. 3.1.3 |

Vanjska polovica voda navedena je kao grana, ali ne postoji joj drugi kraj! Takvih grana s
nepostojećim krajem ima 40, a nepostojećih sabirnica 31. 

> [!NOTE]
> Najvažnija stvar je zapravo to da razmjena preko granice nigdje nije zapisana kao
> injekcija. Na X-sabirnicama ne postoje ni teret ni generator koji bi predstavljali snagu 
> koja odlazi/dolazi.

### 3.1.3. Razmjena kao izvedena veličina

Dostavljena .raw datoteka uz topologiju i parametre sadrži i spremljeno rješenje tj. iznos
i kut napona sabirnica, onakve kakvi su bili kada je model izvezen. Ti su naponi izračunati
u punom modelu, u kojem postoje susjedni sustavi (ili je izvezen iz Network Managera koji 
ima područje osmotrivosti i vidi i vanjske sustave do neke mjere).

**Primjer: sabirnica 99993 (DV Ernestinovo - Pecs 2)**

> 60032,'HERNES11    ', 400.0000,1,  16,   4, 404,1.02853,  96.0714,...
> 99993,'XER_PE12    ', 400.0000,1,1631,  99,  11,1.02836,  94.0024,...
> 60032, 99993,'2 ', 8.26000E-04, 8.85700E-03,0.24556, ...
> 99993,311080,'2 ', 7.94000E-04, 8.51500E-03,0.23607, ...

Hrvatska polovica (60032-99993) ima poznate napone na oba kraja. Struja koja s X-čvorišta
ulazi u tu granu, po pi-modelu voda (uzdužna admitancija $\underline{y} = 1/(R + jX)$, a
polovica poprečne susceptancije $B/2$ na svakom kraju), iznosi
 
$$
\underline{I}_X = (\underline{U}_X - \underline{U}_H)\,\underline{y} + \underline{U}_X\,\frac{jB}{2},
$$
 
a snaga
 
$$ 
\underline{S}_X = \underline{U}_X\,\underline{I}_X^{*}\cdot S_{baza} = -426{,}89 - j\,32{,}64\ \text{MVA}
\qquad (S_{baza} = 100\ \text{MVA}). 
$$

Negativan predznak znači da snaga **ulazi** u X-čvorište tj. izlazi iz hrvatskog sustava.

Vanjskom polovicom tok se ne može izraćunati, jer napon sabirnica 311080 nije poznat. 
A kako na X-čvorištima nema generatora ni tereta, imamo snagu razmjene koja nigdje ne ide.

### 3.1.4. Gdje se razmjena mjeri?

Iz drugog načina provjere slijedi da je **Prilog 5 mjeren na hrvatskom kraju voda**, a ne na
granici. Razlika između dvaju mjesta mjerenja su gubici na hrvatskoj polovici voda; na primjeru
iz §3.1.3 to je 428,33 − 426,89 = 1,44 MW.
 
| Granica | Na hrvatskom kraju [MW] | Na X-sabirnici [MW] |
|---|---:|---:|
| HR – SI | 2677,6 | 2658,2 |
| HR – HU | 1057,4 | 1053,7 |
| HR – BA | 353,7 | 338,6 |
| HR – RS | −419,4 | −422,6 |
| HR – IT | 0 | 0 |
| **Ukupno** | **3669,3** | **3628,0** |
 
(Pozitivno = izvoz iz Hrvatske; model ScA_2029, scenarij A.)
 
Za ovaj naš alat je mjerodavna vrijednost **na X-sabirnici**, jer se granica u modelu zatvara upravo tamo (t.3.2). Za usporedbu s Prilogom 5 koristi se vrijednost na hrvatskom kraju.
 
> [!NOTE]
> Zbroj redaka Priloga 5 za granicu HR – BA iznosi 353,8 MW, a redak "Ukupno (HR – BA)" u
> Prilogu navodi 342,4 MW. Model se slaže sa zbrojem redaka; razlika od 11,4 MW je u samom
> zbroju u Prilogu.

### 3.1.5. Sažetak

- Model sadrži (isključene) sabirnice koje su rezervirane za planirane vodove
- Model sadrži (isključene) sabirnice za spoj HVDC prema Italiji
- DV 400 kV Žerjavinec - Heviz 1 - postoji samo vanjska polovica voda?
- DV 220 kV Trebinje - Plat 1 - nema čvorišta za Trebinje i nema čvorišta za HE Dubrovnik B 4(koji je u vlasništvu Republike Srpske u BiH), iako samo X-čvorište postoji.
- Područje HR ima zadanu razmjenu PDES = 2512 MW, za koju je bilančni generator stavljen u
TE Plomin, gdje je generator isključen, a iznos ne odgovara stvarnim razmjenama

**Plat - Trebinje 1** - oba kraja X-čvorišta 99974 su nepostojeće sabirnice: 130215 (Trebinje) 
i 62056 (HE Dubrovnik B). Paralelni pogon HE Dubrovnik A je u modelu i uključen je. 

## 3.2. Kako ovaj model opisuje granična čvorišta?

### 3.2.1. Stalna PQ injekcija na X-čvorištu

Kako smo vidjeli iz prethodnog poglavlja, model se bez dodatne pretpostavke za granična
čvorišta ne može do kraja modelirati - na svakoj X-sabirnici nedostaje element kako bi se 
osnovna bilanca ispunila. 

Najjednostavniji način da se taj nedostatak pokrpa je **stalna injekcija P i Q jednaka razmjeni iz spremljenog rješenja**. 

- vanjska polovica interkonekcije se izostavlja (tak i tak nemamo drugi kraj voda)
- na X-sabirnicu se postavlja **teret** iznosa P,Q jednakim snazi razmjene
- teret dobiva oznaku `granica=True` da ga se u pandapower modelu razlikuje od ostalih tereta
- predznak slijedi konvenciju tereta - pozitivan teret = izvoz iz Hrvatske.

```
  60032 HERNES11  ────────────  99993 XER_PE12
                  hrvatska polovica      │
                  (u modelu)             ▼  teret  P = 426,89 MW,  Q = 32,64 Mvar
                                            (granica=True)
```

### 3.2.2. Slack bus

Za proračun tokova snaga nužno je da imamo jedan referentni čvor sa zadanim modulom i kutom napona
čiji bi generator pokrivao razliku između ukupne proizvodnje i zbroja potrošnje i gubitaka. U 
isporučenim modelima nema sabirnice tipa 3 te se odabir slack generatora ostavlja izrađivaču. Za
potrebe izrade ovog modela odabrana je RHE Velebit kao reverzibilna hidroelektrana koja može 
pokrivati neravnotežu u oba smjera. 

U spremljenom stanju koje je dostavljeno, slack bus ne bi trebao raditi ništa, što je i okej. 
Problem nastaje kada se stanje promjeni, što se upravo događa u N-1 analizi i proračunima za
operativna ograničenja. 

### 3.2.3. Što to fizikalno znači?

Tokovi snaga na svakoj sabirnici rezultat su rješavanja dviju jednadžbi za radnu i jalovu snagu:

$$
P_k^{spec} - P_k(\mathbf{U}, \boldsymbol{\theta}) = 0, \qquad
Q_k^{spec} - Q_k(\mathbf{U}, \boldsymbol{\theta}) = 0
$$

gdje je $P_k^{spec}$ zadana injekcija (generatori minus tereti), a $P_k(\mathbf{U},\boldsymbol{\theta})$ snaga koja sa sabirnice odlazi granama, izračunata iz napona.

**U stvarnosti**, tj. u punom modelu, na X-sabirnici je zadana injekcija nula, a vanjska polovica
voda je grana kao i svaka druga. Snaga koju ona odnosi ovisi o naponima na oba svoja kraja - za 
vod s reaktancijom $x$, uz zanemaren otpor vrijedi:

$$
P_{van} \approx \frac{U_X\,U_{susj}}{x}\,\sin(\theta_X - \theta_{susj}).
$$

Kada se nakon ispada u Hrvatskoj promijeni kut X-sabirnice $\Theta_X$, mijenja se i $P_{van}$. A
jer je sabirnica susjeda spojena s ostatkom njegove mreže, mijenjaju se i $U_{susj}$, $\Theta_{susj}$ te tokovi na ostalim prekograničnim vodovima.

U ovakvom modelu, vanjska polovica interkonekcije je zamijenjena teretom, a teret u ovom slučaju ne ovisi o naponu. Vanjski sustav bismo za ovaj slučaj zamijenili s 35 neovisnih idealnih 
potrošača stalne snage. Iz toga onda slijede dva svojstva:

> [!IMPORTANT]
> 
> 1. Nema grana između X-čvorišta. X-sabirnice su međusobno povezane samo kroz Hrvatsku mrežu. 
> Svaki put koji u stvarnosti vodi preko susjednog sustava ne postoji.
> 2. Nema odziva. Snaga na svakom prekograničnom vodu ostaje ista bez obzira na to što se 
> dogodilo u našoj mreži. Napon X-sabirnice izvana ništa ne podupire, nego je u cjelosti 
> određeno hrvatskom mrežom.

### 3.2.4. Druga opcija - X-sabirnica kao kruta mreža

Stalna injekcija P,Q kao teret nije jedini način za jednostavno modeliranje uvjeta na granici. 
Druga mogućnost je i da se na svaku X-sabirnicu stavi model krute mreže (`ext_grid` u pandapoweru), sa stalnim iznosom i kutom napona iz spremljenog rješenja. 

U osnovnom stanju to će točno reproducirati dobiveni model i tokove snaga, ali ima svoje 
probleme:

| | Stalna PQ injekcija | Kruta mreža na X-sabirnici |
|---|---|---|
| zadano na X-sabirnici | $P$, $Q$ | $U$, $\theta$ |
| što se mijenja nakon ispada | $U_X$, $\theta_X$ | $P$, $Q$ na X-sabirnici |
| ukupna razmjena Hrvatske | ostaje ista | mijenja se |
| broj referentnih čvorova | jedan (Velebit) | 36 |
| napon X-sabirnice | slobodan, bez potpore izvana | nepomičan, beskonačna potpora |

Kruta mreža čvrsto drži kut tamo gdje je zadana. Kada bi se nakon ispada nekog elementa 
kutovi u Hrvatskoj pomaknuli, svaka kruta mreža bi preuzela ili predala dio snage kako bi 
zadržala kut napona koji joj je zadan. Tehnički na taj način svaka od tih sabirnica postaje novi
referentni čvor što bi uzrokovalo promjenu snage razmjene bez da za to uopće postoji fizikalni
razlog. Između dviju krutih mreža snaga može teći i "preko slack čvorišta", putem koji u 
stvarnosti zapravo ne postoji.

> [!NOTE]
> Stvarni vanjski sustav je **između** tih dviju krajnosti. Ima konačne impedancije (pa
> X-sabirnica nije kruta), ima mrežu koja X-sabirnice povezuje (pa nisu neovisne) i ima
> elektrane koje reguliraju napon i snagu (pa se ne ponaša kao stalni teret). Sve vrste
> ekvivalenata iz §3.5 pokušavaju opisati upravo to "između".

### 3.2.5. Sažetak

Stalna PQ injekcija točno reproducira zadano stanje, čuva ukupnu razmjenu i ima jedan
slack bus, onaj koji mi odlučimo. Ali vanjski sustav se u tom slučaju ne ponaša kao u stvarnosti.
Dok god se stanje ne mijenja, to nije ni važno - ali s obzirom da imamo obvezu analize N-1, 
to nam zapravo ne odgovara. 

## 3.3. Posljedice za N-1 i operativna ograničenja

### 3.3.1. Zašto nam je bitan odziv vanjske mreže?

Osnovno stanje modela nikada se ne koristi samostalno bez promjene (osim recimo za potvrdu osnovnih tokova snaga i konvergencije modela).
Ali, i N-1 analiza i proračuni operativnih ograničenja sastoje se od promjena osnovnog stanja. 
- Ispad elemenata (N-1) mijenja topologiju i preraspodjeljuje tokove
- Priključenje novih elektrana mijenja bilancu, pa netko mora preuzeti njenu snagu
- Ograničenje proizvodnje elektrane opet mijenja bilancu, ali u suprotnom stanju 

Nakon svake takve promjene, **vanjski sustav se odziva na promjenu** - tokovi na prekograničnim vodovima se mijenjaju, a dio preraspodjele ide kroz susjedne mreže. U modelu koji drži konstantne injekcije P i Q tih promjena ne može imati. Ova sekcija se bavi time što to znači za modele za EOTRP u nekoliko različitih situacija. 

Početno stanje - Model ScA_2029, s referentnim čvorom RHE Velebit. U baznom scenariju gubitci u prijenosnoj mreži iznose 342,9 MW, a proizvodne jedinice RHE Velebit proizvode 179,4 MW. 

### 3.3.2. Ispad prekograničnog voda 

Kada ispadne hrvatska polovica prekograničnog voda, X-sabirnica ostaje bez veze s hrvatskim sustavom. Njezin teret/razmjena time nestaje iz bilance, a razliku preuzima referentno čvorište. 

**Primjer 1:  Ispad prekograničnog voda DV 400 kV Melina - Divača** (X-sabirnica 99986, izvoz 1002,5 MW)

| | Model sa stalnim PQ | Stvarnost (kvalitativno) |
|---|---|---|
| izvoz Hrvatske | pada za 1002,5 MW | ostaje isti |
| promjena snage referentnog čvora (Velebit) | **−1123,4 MW** | — |
| tokovi na ostalim prekograničnim vodovima | nepromijenjeni (svi unutar 0,5 MW) | preuzimaju 1002,5 MW, većinom vodovi prema Sloveniji i Mađarskoj |

Dakle, u slučaju ispada 400 kV voda kao što je Melina - Divača (što jest naravno ekstreman slučaj, ali kad već se u svim scenarijima modeliraju i ekstremni slučajevi proizvodnje, onda zašto bismo ignorirali ekstreman slučaj u slučaju N-1?), RHE Velebit bi trebao smanjiti snagu sa 179,4 MW na -944 MW kako bi pokrio nastalu razliku.  Razlika između 1002 i 1123 MW je zbog smanjenja gubitaka na zapadnom dijelu prijenosne mreže (S obzirom na visoko opterećenje zapadnog dijela mreže, normalno je da su manji gubitci kad je i manje opterećenje).

> [!NOTE]
> Ispad prekograničnog voda u modelu sa stalnim PQ nije valjan N-1 slučaj. Iz tog razloga isključujemo interkonekcijske vodove iz
> N-1 analize, iako Smjernice traže N-1 analizu za sve utjecajne okolne elemente. Sve dok ne postoji drugačiji način raspodjele tokova sa granice (ili se oni ne smiju preraspodijeliti prema Uputama), ovakav način je nužan. 

### 3.3.3. Ispad unutarnjeg elementa - fiksirane razmjene

Kad ispadne unutarnji vod, X-sabirnice ostaju spojene, a teret na njima ostaje isti. Tok na hrvatskom kraju prekograničnog voda tada se može promijeniti samo za promjenu gubitaka na hrvatskoj polovici voda (do te promjene nema kako doći ako cijelo vrijeme njime ide fiksna P,Q). 

Provjera na 409 ispada za scenarij A 2029:

| Ishod ispada | Broj | Promjena razmjene na hrvatskom kraju |
|---|---:|---|
| sve X-sabirnice ostaju spojene | 376 | **najviše 1,9 MW** (gubici na hrvatskoj polovici) |
| neka X-sabirnica ostaje u otoku | 27 | v. §3.3.4 |
| tok snaga nema rješenja | 6 | v. §3.3.5 |

U stvarnosti dio tokova ide kroz susjedne sustave. Primjer - kad u Slavoniji ispadne vod kojim snaga ide
prema Mađarskoj, dio tog toka stvarno ide okolo, npr preko Ernestinova u Pecs i preko Žerjavinca u Heviz, a unutar 
Mađarske između ta dva mjesta. Isto tako se može raspodijeliti na bilokoji drugi 110 kV ili 220 kV dalekovod. 
Kod nas se to ne može dogoditi jer nemamo konekciju između čvorišta.

Koliko to utječe na rezultate je teško reći, pogotovo jer ovisi o lokaciji ispada, toku koji ide tim 
vodom i slično. 

### 3.3.4. Fake otoci u N-1 analizi

U 27 od 409 ispada unutarnjeg voda, dio hrvatske mreže ostaje spojen sa susjednim sustavom samo preko X-sabirnica. U modelu je to naravno otok i ispada iz proračuna, zajedno sa svojom proizvodnjom, potrošnjom i razmjenom. U stvarnosti taj dio mreže može i dalje biti napajan preko susjednog sustava. 

Najviše takvih situacija je u južnoj Dalmaciji (Plat, Komolac, Ston, Srđ, Rudine, Ponikve) - 13 različitih ispada odvaja je od ostatka hrvatske mreže, a ona je tehnički i dalje spojena na mrežu BiH (DV 220 kV Plat - Trebinje, DV 110 kV Komolac - Trebinje, DV 110 kV Ston - Neum). 

| Ispad (unutarnji vod) | X-sabirnice u otoku | Razmjena u otoku [MW] | Promjena snage Velebita [MW] |
|---|---|---:|---:|
| 60049–60245 Konjsko – Cetina | 99985 Mostar | 630,2 | −526,3 |
| 60118–60195 Ston – Ponikve | 99962, 99975, 99981 | 146,2 | −39,5 |
| 60048–60196 Komolac – Rudine | 99962, 99975 | 120,0 | −75,4 |
| 60064–80099 Međurić – `HSEHRV21` | 99977 Prijedor | −67,9 | +156,1 |

Rezultati za takve ispade jednako su nevaljani kao i za ispade prekograničnih vodova. 

### 3.3.5. Ispadi za koje tokovi snaga ne daju rješenja koja konvergiraju

Za 6 od 409 ispada unutarnjih vodova ne možemo naći rješenje tokova snaga. (80XXX sabirnice su budući priključci Korisnika Mreže).

| Ispad | Napon | Tok prije ispada [MW] | Opterećenje prije ispada |
|---|---|---:|---:|
| 60008–80111 Brinje – VE Ljut 3 | 220 kV | 261,7 | 44 % |
| 60067–60109 Melina – Senj | 220 kV | 492,3 | 86 % |
| 60032–80088 Ernestinovo – FNE Končanica | 400 kV | 409,2 | 30 % |
| 60150–80088 Žerjavinec – FNE Končanica | 400 kV | 637,4 | 48 % |
| 60066–80157 Melina – PE THC | 400 kV | 1191,6 | 101 % |
| 60132–80157 Velebit – PE THC | 400 kV | 1121,0 | 89 % |

Kako je već spomenuto u prvom poglavlju, ispadi 400 kV i 220 kV dalekovoda koji
čine osnovne pravce prijenosa energije na potezima jug-sjever i istok-zapad ne 
daju konvergirana rješenja. Ispad dionice 400 kV dalekovoda Velebit - Melina, 
koji su visoko opterećeni i u početnom slučaju, nema rješenje jer jednostavno
nema puta na 400 kV i 220 kV mreži kojim bi se toliki tokovi mogli zatvoriti.

Tokovi snaga su provedeni s nekoliko različitih opcija za slučajeve ovih ispada:

| Pokušaj | Ishod |
|---|---|
| Newton-Raphson bez Q-granica (svi regulatori PV) | 4 slučaja konvergiraju, ali uz nemoguću jalovu snagu (npr. oko 4400 Mvar na regulatoru 110 kV sabirnice 60031 `HELTO 51`); Melina/Velebit – 80157 ne konvergiraju ni tako |
| VARLIM s početkom iz osnovnog stanja (PV/PQ stanje i naponi osnovnog slučaja) | ne konvergira ni jedan |
| VARLIM s Iwamotovim Newton-Raphsonom (prigušeni korak) | ne konvergira ni jedan |
| smanjenje izvoza (svi tereti na X-sabirnicama × λ, proizvodnja smanjena razmjerno) | konvergira tek ispod određenog izvoza — v. dolje |

Rješenje postoji samo kada se zanemare granice jalove snage ili kada se smanji prijenos, što je 
obilježje prekoračenja prijenosne moći dalekovoda (a i naponske nestabilnosti) - sa stvarnim
granicama Q i ostalim elementima u mreži nije moguće prenijeti zadanu snagu s juga na sjever ili istoka na zapad.

**Uloga granica prijenosnog sustava** - isti problematični ispadi proračunati su na 
još dva načina: 

1. **Smanjeni izvoz** - granica ostaje stalna PQ injekcija, ali se svi tereti na X-čvorištima
pomnože faktorom $\lambda<1$, a proizvodnja u Hrvatskoj se smanji za isti iznos (skaliranjem). Traži se 
najveći $\lambda$ uz koji ispad ima rješenje.
2. **Kruta mreža na X-sabirnicama** - na **svakoj** od 35 X-sabirnica s razmjenom teret se uklanja, a na 
njegovo mjesto se stavlja `ext_grid` s modulom i kutom napona iz spremljenog rješenja. Velebit ostaje slack bus, 
pa model zapravo ima 36 krutih izvora. U osnovnom stanju to daje isto rješenje kao spremljene PQ injekcije.

| Ispad | Najveći izvoz uz stalne PQ injekcije | Kruta mreža na X-sabirnicama (§3.2.4) |
|---|---|---|
| Brinje – VE Ljut 3 | 3600 MW (99 % osnovnog) | rješenje; ukupni izvoz 3588 MW |
| Melina – Senj | 3515 MW (97 %) | rješenje; ukupni izvoz 3588 MW |
| Ernestinovo – FNE Končanica | 3061 MW (84 %) | rješenje; ukupni izvoz 3643 MW |
| Žerjavinec – FNE Končanica | 2182 MW (60 %) | rješenje; ukupni izvoz 3643 MW |
| Melina – PE THC | nema rješenja ni bez izvoza | rješenje, ali izvoz pada na 2449 MW, a Velebit na −1259 MW |
| Velebit – PE THC | 28 MW (≈ 0 %) | rješenje, ali izvoz pada na 2591 MW, a Velebit na −1115 MW |

**Kako kruta mreža preraspodjeljuje tokove?** 

Uz stalnu PQ injekciju zadana je snaga na X-čvorištima, a napon i kut se mijenjaju. Uz krutu mrežu je
obrnuto, zadani su napon i kut, a snaga na X-sabirnici je rezultat proračuna. Tok hrvatskom polovicom 
prekograničnog voda je približno:

$$
P \approx \frac{U_H U_X}{x}\sin{\theta_H-\theta_X}
$$

gdje je $\theta_X$ nepromjenjiv. Kad nakon ispada kut hrvatske sabirnice $\theta_H$ poraste ili padne, tok
na tom vodu raste ili pada. Nitko tu raspodjelu ne zadaje, ona slijedi iz toga kako se nakon ispada pomaknu
kutovi napona na sabirnicama. 

Ukupni izvoz pri tom **nije niti zadan niti sačuvan**. Za prva četiri ispada iz tablice gore ukupni izvoz se
promijenio za manje od 40 MW jer su se ta povećanja i smanjenja na različitim vodovima uglavnom poništila. S 
druge strane, za slučaj ispada Velebit - Melina, ukupni izvoz pada za više od 1 GW! Ali, promijenila se i 
raspodjela po vodovima i to je dovoljno da imamo rješenje koje konvergira.

Kod ispada u slavonskom koridoru preraspodjela je ona o kojoj smo razgovarali u teoriji - kad je put 
Ernestinovo - Žerjavinec prekinut, kut u Ernestinovu raste, a u Žerjavincu pada, pa izvoz prema Pecsu
raste (ukupno +214 MW na oba voda), a izvoz prema Hevizu pada (-105 MW). Ostatak se raspodijeli na ostale
prekogranične vodove. U stvarnosti taj tok ide kroz mađarsku mrežu od Pecsa do Heviza (iako mi nemamo 
modeliranu mrežu između njih).

Zaključak za ova četiri ispada: uz stalne PQ injekcije svaki prekogranični vod mora i dalje nositi točno svoju razmjenu, pa sav tranzit mora proći preostalim hrvatskim elementima. Uz vanjski sustav koji može preraspodijeliti tokove (ovdje u krajnjem obliku krute mreže) rješenje postoji. Koliko je točno preraspodjela stvarna, ne može se reći bez vanjske mreže — kruta mreža je druga krajnost i vjerojatno griješi u preraspodjeli (bilo u iznosu, bilo u omjerima). 

Ispadi voda Velebit – Melina (obje dionice preko 80157 PE THC) su drukčiji. Ni uz izvoz smanjen na nulu nema rješenja, a kruta mreža daje rješenje samo tako da izvoz padne za više od 1 GW i da Velebit preuzme isto toliko, što nije legitimno
rješenje.

> [!WARNING] 
> Ispad bez rješenja nije ispad bez posljedica. 
> Kako tretirati ovakve slučajeve u samim analizama? Za proračun operativnih ograničenja ovakav slučaj bi trebao biti 
> dosta kritičan, ali s druge strane, trenutne analize nam govore da puno toga ovisi o modeliranju granice. 
> Pitanje i na koji način primijeniti Formulu [1] iz Smjernica na takve slučajeve, kad nema opterećenja iz kojeg bi se 
> računao faktor. 

> [!NOTE] 
> S kutovima PST-ova odabranima prema Smjernicama (najmanji broj preopterećenja 400/220 kV u osnovnom stanju) rješenja 
> nemaju i ispadi 400 kV Melina – Tumbri i Tumbri – Žerjavinec, ukupno 8. Ako bi se uzeo neki drugi kriterij za postavljanje kuteva PST-a, bi li se dobio bolji rezultat? [Ovaj dio je procesu planiranja i izrade]

### 3.3.6. Napon na granici

U modelu sa stalnim PQ injekcijama jalova snaga na X-sabirnici je stalna, pa promjena napona X-sabirnice ovisi
samo o hrvatskoj mreži tj. promjenama unutar nje. U stvarnosti vanjska mreža ima svoju naponsku potporu u vidu 
generatora i FACTS uređaja. Tehnički bi vanjski sustav trebao i dalje podupirati napon na granici kada se dogodi 
nešto što u Hrvatskom sustavu uzrokuje pad napona. 

Model sa stalnim PQ tako ima problema i naponske prirode:

- **precjenjuje promjene napona** na graničnim sabirnicama nakon ispada (u pravilu simulacijski napon 
padne više nego što bi se u stvarnosti desilo).
- **precjenjuje iznose jalove snage** koju moraju dati hrvatski generatori kako bi održali napon unutar granica.

To utječe i na strujna opterećenja, a samim time i na operativna ograničenja. Opterećenje se računa iz struje, a struja ovisi o jalovoj snazi i naponu:

$$
I = \frac{\sqrt{P^2 + Q^2}}{\sqrt{3}U}
$$

Postoje dva puta:

- **veći tok jalove snage** - ako jalovu snagu koju je dao susjedni sustav moraju dati sad hrvatski 
generatori, ona teče unutarnjim vodovima i povećava tok jalove po njima
- **niži naponi** - za istu prividnu snagu niži napon znači veću struju

### 3.3.7. Uravnoteženje novih proizvodnih jedinica

Kad se priključi nova elektrana ili se ograniči njena snaga, razliku mora netko preuzeti. Kasnija poglavlja ove 
dokumentacije opisuju varijante gdje to preuzima RHE Velebit (V1), upravljive elektrane u Hrvatskoj (V2) ili razmjene sa susjednim sustavima (V3). 

### 3.3.8. Zaključak


| Situacija | Model sa stalnim PQ | Posljedica |
|---|---|---|
| ispad prekograničnog voda | razmjena nestaje, preuzima Velebit | nevaljan slučaj; isključen iz N-1 |
| ispad unutarnjeg voda | razmjene nepromijenjene (≤ 1,9 MW) | preraspodjela samo kroz Hrvatsku; pogreška nepoznata, smjer nije zajamčen |
| ispad koji odvaja dio mreže spojen sa susjedom | otok ispada iz proračuna | nevaljan slučaj; zastavica G4 |
| ispad u opterećenom koridoru | nema rješenja toka snaga | rezultat izostaje; ne smije se ispustiti iz izvještaja |
| napon na granici | bez potpore izvana | promjene napona precijenjene; veća struja (više Q, niži napon) uz granicu |
| uravnoteženje V3 | raspodjela po X-sabirnicama proizvoljna | rezultat ovisi o pretpostavci |


## 3.4. Što mora imati dobar prikaz vanjskog sustava?

### 3.4.1. Posljedice i zahtjevi

U prethodnoj sekciji sagledali smo što se događa kad vanjski sustav nema ništa. U zaključku je dan popis
posljedica takvog pristupa i svaka od navedenih posljedica ukazuje što bi dobar ekvivalent zapravo trebao imati.

| Posljedica (§3.3) | Što bi se u stvarnosti dogodilo | Što prikaz vanjskog sustava za to treba |
|---|---|---|
| ispad prekograničnog voda: razmjena nestaje, preuzima je Velebit | razmjena prelazi na ostale prekogranične vodove, ukupna ostaje ista | putove između X-sabirnica kroz susjedne mreže; ukupna razmjena nepromijenjena |
| ispad unutarnjeg voda: razmjene zamrznute | dio preraspodjele ide kroz susjede | tok prekograničnog voda mora ovisiti o naponima i kutovima na granici |
| otoci koji u stvarnosti nisu otoci | dio mreže ostaje napajan preko susjeda | X-sabirnice moraju biti povezane i izvan Hrvatske |
| ispadi bez rješenja | tokovi se preraspodijele po prekograničnim vodovima | isto kao gore: putovi kroz susjede |
| napon na granici bez potpore | susjedni generatori daju jalovu snagu | izvori jalove snage iza X-sabirnica |
| uravnoteženje V3 proizvoljno | promjenu bilance preuzimaju elektrane u susjedstvu, prema mreži i dispečingu | izvori djelatne snage s fizikalnom raspodjelom (GSK) |





