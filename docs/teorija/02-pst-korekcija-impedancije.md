# 2. PST i korekcija impedancije

> [!WARNING]
> **Modeliranje PST-ova u alatu je zasad samo kutno i nije točno.**
> Stvarni PST-ovi u sustavu — barem dio njih; koji, tek treba provjeriti — imaju
> **dijagonalnu (kosu) regulaciju**: jedna preklopka istodobno mijenja i kut i modul
> napona. Model, kao i isporučeni `.raw`, kut i omjer prijenosa zadaje kao dvije neovisne
> veličine. Zato su rezultati koji ovise o promjeni kuta PST-a (optimizacija kutova po
> scenariju, §2.7) **samo približni**. Model treba revidirati čim budu dostupne tablice po
> položajima preklopke (modul napona, kut i impedancija za svaki položaj) — alat za to već ima
> predviđenu opciju (§2.8).
>
> Zahtjev smjernica da se PST-ovi istodobno drže u naponskoj regulaciji i podešavaju po kutu
> kod dijagonalne regulacije nije ostvariv, a isporučeni modeli za to nemaju podatke —
> vidi [Nedostaci smjernica, N1](../nedostaci-smjernica.md).

Osnovni podaci i tablice korekcije svih PST-ova u modelu: [Prilog A](prilog-pst-zapisi.md).

## 2.1 Što PST radi

Transformator s mogućnošću zakreta kuta (PST) u seriju s mrežom dodaje napon koji pomiče fazni
kut između svojih priključaka za $\alpha$. Za element reaktancije $X$ između sabirnica s
naponima $U_1\angle\delta_1$ i $U_2\angle\delta_2$:

$$P_{12} \approx \frac{U_1 U_2}{X}\,\sin(\delta_1 - \delta_2 + \alpha).$$

Promjenom $\alpha$ PST preusmjerava djelatnu snagu između paralelnih putova — zato je prva mjera
u postupku smjernica (Slika 2) promjena postavki raspoloživih PST-ova.

## 2.2 Tablice korekcije impedancije u PSS/E-u

Serijska impedancija PST-a ovisi o položaju preklopke. PSS/E to opisuje **tablicom korekcije
impedancije** (Impedance Correction Table): za namot s kontrolom kuta (|COD| = 3) tablica daje
faktor $F$ kao funkciju kuta u stupnjevima, a PSS/E linearno interpolira:

$$Z(\alpha) = F(\alpha)\cdot Z_{nom},\qquad
F(\alpha) = F_j + (F_{j+1} - F_j)\,\frac{\alpha - \alpha_j}{\alpha_{j+1} - \alpha_j},
\quad \alpha_j \le \alpha \le \alpha_{j+1}.$$

Izvan raspona tablice uzima se rubna vrijednost. U isporučenim modelima imaginarni dio faktora
je nula, pa se $R$ i $X$ skaliraju istim faktorom.

**Impedancija zapisana u `.raw`-u je ona uz $F = 1$** — to je kut na rubu tablice, a ne nulti
položaj.

| Tablica | Transformator | Raspon kuta | $F$ na rubovima | $F(0°)$ |
|---|---|---|---|---|
| 1 | Gračac (2 × PST 110/110 kV) | −30° … +30° | 1 / 1 | 0,0001 |
| 2 | Žerjavinec T1 400/220 kV | −4,48° … +6,76° | 1 / 0,7761 | 0,8349 |
| 3 | Senj T1 220/110 kV | −6,0° … +10,54° | 1 / 0,7413 | 0,7334 |
| 4 | Konjsko T1–T3, Melina T1–T2 400/220 kV | −5,4° … +9,0° | 1 / 0,7667 | 0,8333 |

Tablica 1 opisuje simetrični PST s poprečnom regulacijom: serijska impedancija u nultom položaju
praktički nestaje, a raste s kutom (pri $\alpha = 9°$, $F = 0{,}0925$). Tablice 2–4 opisuju
autotransformatore kod kojih se impedancija mijenja umjereno, ali nesimetrično oko nule.

> [!NOTE]
> Melina i Žerjavinec imaju kut 0°, ali i tablicu — pa se i na njih primjenjuje
> $F(0°) \approx 0{,}83$. Bez toga je impedancija za 17 % prevelika.

## 2.3 Dvonamotni PST

Za `trafo` se kut zadaje kao `shift_degree = +ANG1`, a impedancija kao
$u_k = 100\,z\,F(\alpha)$, $u_{kr} = 100\,r\,F(\alpha)$. Nazivne vrijednosti ($F = 1$) čuvaju se u
stupcima `psse_vk_nom`, `psse_vkr_nom`, a broj tablice u `psse_tab1` — iz toga se impedancija
može ponovno izračunati za bilo koji kut.

## 2.4 Tronamotni PST — korekcija u modelu zvijezde

### Model zvijezde

PSS/E tronamotni transformator opisuje trima impedancijama parova namota $Z_{12}$, $Z_{23}$,
$Z_{31}$ (svaka na svojoj nazivnoj snazi para), a računa s **ekvivalentnom zvijezdom**:

$$
Z_1 = \tfrac12\left(Z_{12} + Z_{31} - Z_{23}\right),\quad
Z_2 = \tfrac12\left(Z_{12} + Z_{23} - Z_{31}\right),\quad
Z_3 = \tfrac12\left(Z_{23} + Z_{31} - Z_{12}\right).
$$

Obrnuto, $Z_{12} = Z_1 + Z_2$, $Z_{23} = Z_2 + Z_3$, $Z_{31} = Z_3 + Z_1$.

### Gdje se primjenjuje faktor

Tablica korekcije je pridružena **namotu 1** (polje TAB1), pa PSS/E skalira **impedanciju
namota 1 u zvijezdi**, a ne impedanciju para:

$$Z_1' = F(\alpha)\,Z_1,\qquad Z_2' = Z_2,\qquad Z_3' = Z_3.$$

pandapower `trafo3w` prima impedancije parova, pa se korekcija prevodi natrag:

$$
Z_{12}' = Z_{12} + (F-1)\,Z_1,\qquad
Z_{31}' = Z_{31} + (F-1)\,Z_1,\qquad
Z_{23}' = Z_{23}.
$$

### Primjer: autotransformator 400/220/30 kV, 400 MVA (Konjsko T1)

**Korak 1 — impedancije parova (CZ = 3).** Za svaki par `.raw` daje gubitke u W i $|Z|$ u
p.u. na snazi para; $r = P_{Cu}/S_{par}$, $x = \sqrt{|Z|^2 - r^2}$. Preračunato na
$S_B = 100$ MVA:

| | $Z$ [p.u., 100 MVA] |
|---|---|
| $Z_{12}$ (400–220 kV) | $0{,}00036 + j\,0{,}02917$ |
| $Z_{23}$ (220–30 kV) | $0{,}00234 + j\,0{,}03993$ |
| $Z_{31}$ (30–400 kV) | $0{,}00237 + j\,0{,}13348$ |

**Korak 2 — zvijezda.**

| | $Z$ [p.u., 100 MVA] |
|---|---|
| $Z_1$ | $0{,}00020 + j\,0{,}06136$ |
| $Z_2$ | $0{,}00016 - j\,0{,}03219$ |
| $Z_3$ | $0{,}00217 + j\,0{,}07212$ |

Negativna reaktancija $Z_2$ uobičajena je kod autotransformatora — posljedica je zajedničkog
namota, a ne greška u podacima.

**Korak 3 — faktor.** Kut 5,5° leži između točaka tablice 4,91° ($F = 0{,}7944$) i 5,70°
($F = 0{,}7889$):

$$F(5{,}5°) = 0{,}7944 + (0{,}7889 - 0{,}7944)\,\frac{5{,}5 - 4{,}91}{5{,}70 - 4{,}91} = 0{,}79029.$$

**Korak 4 — natrag u parove.**

| | Nazivno ($F=1$) | Korigirano | Promjena |
|---|---|---|---|
| $Z_{12}$ | $0{,}00036 + j\,0{,}02917$ | $0{,}00032 + j\,0{,}01631$ | **−44 %** |
| $Z_{31}$ | $0{,}00237 + j\,0{,}13348$ | $0{,}00233 + j\,0{,}12061$ | −9,6 % |
| $Z_{23}$ | $0{,}00234 + j\,0{,}03993$ | nepromijenjeno | 0 |

Smanjenje $Z_1$ za 21 % daje smanjenje impedancije 400–220 kV za 44 %, jer je
$Z_{12} = Z_1 + Z_2$, a $Z_2$ je negativna. Zbog toga pogrešno postavljena korekcija ima
velik učinak na tokove kroz Konjsko.

### Provjera na podacima

Mjesto primjene faktora nije dokumentirano u isporučenim podacima pa je utvrđeno usporedbom sa
spremljenim PSS/E rješenjem (najveća neusklađenost snage na sabirnici, model A-2029; sve ostalo
nepromijenjeno, uključujući korekciju na dvonamotnim PST-ovima):

| Primjena faktora $F$ | Najveća neusklađenost |
|---|---|
| nigdje | 4794 MW |
| samo na $Z_{12}$ | 856 MW |
| na $Z_{12}$ i $Z_{31}$ (jednako) | 1741 MW |
| na sva tri para | 5823 MW |
| **na $Z_1$ zvijezde (primijenjeno)** | **0,71 MW** (razina zaokruživanja) |

## 2.5 Predznak kuta

Ni predznak kuta nije preuzet "po definiciji", nego provjeren:

| Element | pandapower | Neusklađenost uz suprotni predznak |
|---|---|---|
| `trafo` | `shift_degree = +ANG1` | — |
| `trafo3w` | `shift_mv_degree = shift_lv_degree = +ANG1` | reda veličine GW |

## 2.6 Kako su PST zapisi kodirani u isporučenim modelima

| Transformator | COD1 | RMA / RMI | VMA / VMI | CONT | Tumačenje |
|---|---|---|---|---|---|
| Gračac (2×) | −3 | +30 / −30 | +150 / −150 | vlastita sabirnica | pravi kutni zapis: granice kuta [°] i toka [MW] |
| Senj T1 | −3 | +10 / −6,3 | −190 / −195 | 60157 | pravi kutni zapis (raspon iz Tablice 3) |
| Konjsko T1–T3 | −3 | 416,738 / 367,701 | 1,1 / 0,9 | 60050 (220 kV) | **polja popunjena za regulaciju napona**: granice u kV, napon u p.u. |
| Melina T1–T2 | −3 | 416,74 / 367,7 | 1,1 / 0,9 | 60067 (220 kV) | isto |
| Žerjavinec T1 | −3 | 416,0 / 375,1 | 1,04 / 1,0 | 60151 (220 kV) | isto |

Kod autotransformatora 400/220 kV granice RMA/RMI su **naponi namota 400 kV**, jer se zbog
dijagonalne regulacije napon mijenja s kutom. U modelima je `PHSHFT=0` i `ACTAPS=0`, pa PSS/E
ta polja ionako ne koristi — kut i omjer su zaključani na vrijednostima iz zapisa.

## 2.7 Kutovi PST-ova po scenariju

Smjernice (§3.1.1) traže:

- PST-ovi se postavljaju u naponsku regulaciju, a kutevi se podešavaju tako da u mreži bude
  najmanje preopterećenja, s prednošću mreži 400 kV i 220 kV;
- kut se bira **jednom po scenariju** unutar raspona iz Tablice 3 i **ne mijenja** se između
  osnovnog stanja i N-1 slučajeva;
- Divača: 30° u referentnom modelu i bez promjene (u isporučenom izvatku Divača ne postoji).

Alat zasad radi **samo kutno**: mijenja kut i, preko tablice korekcije, impedanciju, a omjer
prijenosa (WINDV) ostavlja kakav je u modelu. Kod dijagonalne regulacije kut i modul napona
dolaze iz istog položaja preklopke, pa to nije fizikalno točno (v. upozorenje na vrhu).

### Dokaz da tablice odgovaraju dijagonalnoj regulaciji

Kod dijagonalnog regulatora svaki položaj $n$ dodaje napon stalnog iznosa $\delta$ pod stalnim
kutom $\theta$ prema glavnom naponu:

$$\underline{U}(n) = U_0\left(1 + n\,\delta\,e^{j\theta}\right),\qquad
\alpha(n) = \arg\left(1 + n\,\delta\,e^{j\theta}\right).$$

Kut se zato s položajem mijenja **nejednoliko**. Prilagodba ovog modela na točke tablica
(25 točaka, $n = -12 \dots +12$):

| Tablica | Korak kuta na početku → na kraju | RMS pogreška prilagodbe |
|---|---|---|
| 2 (Žerjavinec) | 0,29° → 0,64° | 0,04° |
| 3 (Senj) | 0,40° → 1,00° | 0,13° |
| 4 (Konjsko, Melina) | 0,35° → 0,85° | 0,10° |

Tablice su dakle konzistentne s dijagonalnom regulacijom. **Iz `.raw`-a se ipak ne može
rekonstruirati modul napona po položaju**: model s jednim dodatnim naponom daje promjenu modula
od ±20–25 % na krajnjim položajima, što se ne slaže s granicama 367,7–416,7 kV. Stvarna
izvedba (regulacijski namot na zvjezdištu autotransformatora) mijenja oba napona namota na
način koji iz ovih podataka nije vidljiv — za to trebaju tablice proizvođača.

## 2.8 Opcija točnijeg modeliranja: tablica po položajima

Kad budu dostupni podaci po položajima, zadaju se u CSV datoteci (postavka `PST_TAP_TABLE` u
`scripts/build_model.py`). Svaki redak opisuje **jedan položaj preklopke** — napon namota 1,
kut i impedanciju zajedno, što je upravo priroda dijagonalnog regulatora:

```
transformer,step,u_w1_kv,angle_deg,z_factor
T1 400 KONJS,-12,…,…,…
```

| Stupac | Značenje |
|---|---|
| `transformer` | ime transformatora kao u `.raw`-u |
| `step` | položaj preklopke (cijeli broj) |
| `u_w1_kv` | napon namota 1 u tom položaju [kV] |
| `angle_deg` | kut u tom položaju [°] |
| `z_factor` | faktor impedancije prema nazivnoj (`.raw`) impedanciji; kod tronamotnog transformatora primjenjuje se na $Z_1$ zvijezde kao u §2.4 |

Za odabrani položaj (postavka `PST_POSITIONS`) alat postavlja napon namota, kut i impedanciju
izravno (`oplimits.pst_tables`), umjesto kutnog modela. Upravljačka varijabla tada više nije
kut nego **položaj** $n$, a optimizacija po scenariju bira položaj. U nalazima se navodi koji su
transformatori modelirani tablično, a koji kutno; upozorenje o kutnom modelu ostaje samo za
one bez tablice.

> [!NOTE]
> pandapower ima i ugrađeni mehanizam za ovo (`net.trafo_characteristic_table`,
> `tap_changer_type="Tabular"`), koji vrijednosti uzima točnim podudaranjem po položaju.
> Alat ga zasad ne koristi: vlastita izvedba je jednostavnija, ista je za dvonamotne i
> tronamotne transformatore i provjerena je testom (tablica koja opisuje trenutno stanje ne
> mijenja nijedan parametar).
