# 6. Uravnoteženje snage — tri varijante

> [!IMPORTANT]
> **Ono što metoda ne propisuje, a mijenja rezultat.**
>
> Kad se novi korisnik isključi (korak "doprinos", §5.4) ili ograniči (formula [1], §5.6),
> u sustavu nedostaje snaga koju netko mora nadomjestiti. Smjernice ne kažu tko. O tome
> izravno ovise:
>
> - **doprinosi korisnika** $C_{k,c,i}$ — pa i to tko se uopće smatra odgovornim za preopterećenje,
> - **rasterećenje** koje ograničenje donosi, dakle broj iteracija $f$ i iznos $\Delta P_{max}$,
> - **energija ograničenja** $E_{oo,god}$ i $E_{oo,raz}$.
>
> Alat zato svaki proračun radi u **tri varijante uravnoteženja** i rezultate uvijek
> prikazuje usporedno. Razlika između varijanti je **metodološka nesigurnost** rezultata i mora
> biti navedena u svakom izvještaju — tekst za izvještaje je u
> [obveznoj napomeni](../izvjestaji/napomena-uravnotezenje.md).

## 6.1 Zašto uravnoteženje mijenja rezultat

Neka se injekcija na mjestu korisnika $i$ smanji za $\Delta P$, a ista snaga nadomjesti na skupu
jedinica $\mathcal{B}$ s udjelima $w_b$ ($\sum_b w_b = 1$). Promjena toka na elementu $k$:

$$\Delta F_k = -\left(\mathrm{PTDF}_{k,i} - \sum_{b\in\mathcal{B}} w_b\,\mathrm{PTDF}_{k,b}\right)\Delta P
= -\,\mathrm{PTDF}_{k,i\to\mathcal{B}}\;\Delta P,$$

gdje su PTDF-ovi izraženi prema bilo kojem zajedničkom referentnom čvoru. Mjerodavna osjetljivost
je dakle **prijenosni PTDF od korisnika prema skupu uravnoteženja**, a ne svojstvo korisnika samog.
Za isti korisnik i isti element:

- ako je skup uravnoteženja "iza" elementa gledano od korisnika, prijenosni PTDF je malen i
  korisnik malo pridonosi;
- ako je skup uravnoteženja "s iste strane" kao korisnik, a element na putu prema ostatku sustava,
  prijenosni PTDF je velik;
- predznak se može i promijeniti — korisnik koji u jednoj varijanti pridonosi preopterećenju u
  drugoj može biti izuzet.

## 6.2 Tri varijante

| | V1 — referentni čvor | V2 — raspodijeljeno unutar HR | V3 — prekogranično |
|---|---|---|---|
| Tko nadomješta snagu | RHE Velebit (sabirnica 60132) | upravljive elektrane u HR | razmjene na X-čvorištima |
| Sudionici | jedan čvor | jedinice u pogonu s Owner 1 ∈ {27, 28, 30} (akumulacijske, reverzibilne, protočne s bazenom) i termoelektrane; **ne** novi korisnici, **ne** OIE | sva X-čvorišta u pogonu |
| Udjeli $w_b$ | 1 | razmjerni raspoloživoj rezervi u smjeru promjene: $P_T - P_G$ za povećanje, $P_G - P_B$ za smanjenje | razmjerni apsolutnoj razmjeni u osnovnom stanju $\lvert P_x \rvert$ |
| Granice | turbinski rad: $P_B \le P \le P_T$; crpni rad nije u modelu | jedinica koja dosegne granicu ispada iz raspodjele, ostatak se raspodjeljuje ponovno | nema fizikalne granice; zastavica ako se razmjena na vodu promijeni predznak ili za više od 30 % |
| Što predstavlja | PSS/E način s jednim swing čvorom | redispečing unutar hrvatskog sustava | smanjenje izvoza / povećanje uvoza (tržišni odziv, countertrading) |
| Zastavica | neravnoteža izvan +96,6 / −99,4 MW (A-2029) | iscrpljena rezerva sudionika | velika promjena razmjene |

Gubici se u svim varijantama i dalje zatvaraju na referentnom čvoru (RHE Velebit); to je mala
razlika (reda MW) i ista je u svim varijantama.

### Izvedba

pandapower podržava raspodijeljeni referentni čvor (`distributed_slack=True`) samo za elemente
`ext_grid`, `gen` i `xward`, a proizvodne jedinice su u modelu `sgen` (pogl. 1, §1.3). Varijante V2
i V3 zato se izvode **eksplicitnim redispečingom**: neravnoteža $\Delta P$ raspodijeli se na
sudionike prema udjelima $w_b$ (promjena `p_mw` jedinica, odnosno tereta na X-čvorištima),
rješava se load flow, a preostala promjena gubitaka ide na referentni čvor. To je transparentnije
od ugrađene opcije i ne ovisi o vrsti elementa.

### Pravilo dosljednosti

Unutar jednog proračuna **ista varijanta** primjenjuje se na:

1. isključenje korisnika pri određivanju doprinosa (§5.4),
2. ograničenje snage u iteracijama formule [1] (§5.6),
3. završnu provjeru N i N-1 (§5.7),
4. proizvodnju i potrošnju izgubljene u otocima kod radijalnih ispada (pogl. 4, oznaka G4).

Varijante se nikada ne miješaju. Osnovno stanje (stanje 0) isto je u sve tri varijante — razlikuju
se samo stanja nakon isključenja ili ograničenja.

## 6.3 Prikaz rezultata

Svaka veličina iz pogl. 5, §5.12 iskazuje se u tri stupca (V1, V2, V3), uz:

- **raspon** $[\min, \max]$ preko varijanti,
- **oznaku** ako se korisnik smatra odgovornim samo u nekim varijantama,
- **oznaku** ako je preopterećenje nerješivo ograničenjem samo u nekim varijantama.

Za korisnika za kojeg se izrađuje EOTRP navodi se $E_{oo,raz}$ u sve tri varijante. Smjernice ne
daju osnovu za odabir jedne varijante, pa alat ni jednu ne proglašava mjerodavnom.

## 6.4 Što koja varijanta znači u stvarnosti

- **V1** je najbliža načinu na koji se proračun radi u PSS/E-u s jednim swing čvorom. Rezultat jako
  ovisi o položaju tog čvora: RHE Velebit je u Lici, pa se snaga nadomješta kroz mrežu južne
  Hrvatske. Na tom području je i Obrovac–Velebit 110 kV, preopterećen već u osnovnom stanju modela
  A-2029 (133 %).
- **V2** odgovara redispečingu: operator ograničava OIE i povećava upravljive elektrane u HR.
  Rezultat ovisi o tome koje su elektrane u pogonu i koliko rezerve imaju u scenariju.
- **V3** odgovara tržišnom odzivu: manje proizvodnje u HR znači manji izvoz. To je najrealističnije
  za dulja razdoblja, ali je u suprotnosti s razmjenama koje scenarij propisuje (Prilog 5) i ovisi
  o pretpostavljenoj raspodjeli po granicama. S REI ekvivalentom susjednih sustava (pogl. 3, §3.7)
  raspodjela bi imala fizikalnu podlogu.
