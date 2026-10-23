# Nedostaci smjernica i isporučenih podataka

Ova stranica popisuje mjesta na kojima *Smjernice za izvođenje mrežnih analiza* (HOPS,
lipanj 2026.) ili uz njih isporučeni modeli **nisu dovoljni ili nisu međusobno usklađeni** za
proračun koji traže. Za svaku stavku navedeno je što alat radi dok HOPS to ne razriješi.
Stavke se odnose na ovu iteraciju smjernica i modela.

> [!CAUTION]
> **N1 — PST-ovi: smjernice traže naponsku regulaciju i podešavanje kuta istodobno, a za to ne
> postoje ni fizikalna mogućnost ni podaci.**
>
> Smjernice (§3.1.1): *"transformatori s mogućnosti zakreta kuta (engl. PST) se postavljaju u
> naponsku regulaciju, dok se kutevi transformatora podešavaju na način da se koriste položaji uz
> koje postoje najmanji broj preopterećenja …; podešavanje kuteva PST-a se provodi jednom za svaki
> scenarij"*.
>
> Kod PST-a s **dijagonalnom (kosom) regulacijom** kut i napon dolaze iz **istog položaja iste
> preklopke** — ne mogu se zadavati neovisno. Smjernice to ne uzimaju u obzir, iako Prilog 4 istih
> smjernica za PST 220/110 kV, 150 MVA, ±9° izričito navodi *"kosa regulacija"*.
>
> Isporučeni modeli to ne mogu ni opisati:
>
> - `.raw` za svaki PST sadrži samo kut (ANG1), omjer (WINDV1), broj položaja (NTP1), granice
>   (RMA/RMI, VMA/VMI), reguliranu sabirnicu (CONT1) i tablicu korekcije impedancije **po kutu**.
>   **Napon namota po položaju preklopke nigdje nije zadan.**
> - Konjsko, Melina i Žerjavinec kodirani su kao kutni regulatori (COD1 = −3), ali su polja
>   RMA/RMI (kV) i VMA/VMI (p.u.) popunjena za naponsku regulaciju — zapis je unutar sebe
>   nekonzistentan.
> - Konjsko i Melina imaju NTP1 = 33 položaja, a tablicu korekcije s 25 točaka.
> - Tablica 1 (Gračac) nema točku +22,5°, a ima −22,5°; NTP1 = 33, a tablica ima 32 točke.
> - Senj: RMA1 = 10,0° umjesto +10,54° iz Tablice 3, a RMI1 = −6,3° je izvan tablice korekcije
>   (koja počinje na −6,00°).
> - U modelima je `PHSHFT=0` i `ACTAPS=0`: PSS/E ni kut ni omjer ne regulira, oba su zaključana.
>
> Pregled svih PST-ova iz modela s tablicama korekcije: [Prilog A](teorija/prilog-pst-zapisi.md).
>
> **Što alat radi:** samo kutni model (kut + korekcija impedancije, omjer ostaje iz modela), uz
> upozorenje u svakom ispisu ([pogl. 2](teorija/02-pst-korekcija-impedancije.md)). Kad budu
> dostupne tablice po položajima (napon, kut, impedancija za svaki položaj), alat ih koristi umjesto
> kutnog modela i bira **položaj**, a ne kut.
>
> **Potrebno od HOPS-a:** koji PST-ovi imaju dijagonalnu regulaciju, tablice po položajima za njih
> i tumačenje zahtjeva "naponska regulacija + podešavanje kuta" za takve PST-ove.

## Ostali nedostaci smjernica

| # | Nedostatak | Posljedica | Što alat radi |
|---|---|---|---|
| N2 | Nije propisano kako se uravnotežuje snaga pri isključenju i ograničenju korisnika | doprinosi, $\Delta P_{max}$ i energija ovise o izboru | tri varijante, uvijek usporedno ([pogl. 6](teorija/06-uravnotezenje.md)) |
| N3 | Nazivna vrijednost HTLS vodiča nije dana — Prilog 4 daje samo cijenu po km za razrede postojećih vodova (110 kV 90 i 115 MVA, 220 kV 300 MVA) | ne može se izravno provjeriti uklanja li HTLS preopterećenje | izračunata iz kataloga ACCC vodiča uz uvjete kalibrirane na Tablicu 4 ([pogl. 7](teorija/07-mjere.md), §7.2) |
| N4 | Nije propisano kako se kombinira više preopterećenja (više elemenata, više N-1 stanja) u jedan $\Delta P_{max,s}$ | rezultat ovisi o tumačenju | maksimum po parovima + zajednička provjera ([pogl. 5](teorija/05-operativna-ogranicenja.md), §5.7) |
| N5 | Hibridna postrojenja: traži se "uzeti u obzir baterijski spremnik za odgođenu isporuku", ali nije zadano kako, niti se traže podaci o spremniku (snaga, kapacitet) | energija ograničenja hibridnih postrojenja nije jednoznačna | podaci po projektu, dvije granice procjene (§5.11) |
| N6 | Formula za $E_{oo,raz}$ zbraja $P_{oo,god}$ umjesto $E_{oo,god}$ | tipfeler | zbraja se $E_{oo,god}$ |
| N7 | "Zbroj $\Delta P_i$ bi trebao biti usporedivog reda veličine s preopterećenjem" — iz same formule [1] slijedi $\sum \Delta P_i \ge$ višak, obično nekoliko puta veći | nije upotrebljiv kao provjera | omjer se ispisuje, ne koristi se kao kriterij |
| N8 | Nije propisana mjera opterećenja (struja ili MVA); Tablice 5–7 traže I i %In, a nazivne vrijednosti su u MVA | broj preopterećenja može se razlikovati | vodovi strujno, transformatori MVA; obje mjere se računaju ([pogl. 4](teorija/04-n-1-opterecenje.md)) |

## Nedostaci isporučenih modela

| # | Nedostatak | Što alat radi |
|---|---|---|
| M1 | Nema sabirnice tipa 3 (swing); "area swing" 60158 nema jedinicu u pogonu | referentni čvor RHE Velebit (60132) |
| M2 | PST Divača ne postoji u modelu, a Tablica 3 traži 30° | nije primjenjivo; razmjena prema Sloveniji zadana je na X-čvorištima |
| M3 | Vod 62056–99974 (Plat – Trebinje 2): sabirnica 62056 ne postoji | vod izostavljen |
| M4 | Zapis Melina T1 nepotpun u odnosu na istovjetni T2: NOMV1/2/3 = 0, RATE1-1 = 0, RATE3-1 = 0, WINDV3 = 30 kV (T2: 31,5 kV) | za opterećenje namota 1 SBASE para namota, uz zastavicu; tercijar se ne nadzire |
| M6 | Konjsko T3 razlikuje se od istovjetnih T1 i T2: WINDV2 = 230,999 kV, tercijar WINDV3 = 30 kV / NOMV3 = 0 (T1, T2: 31,5 / 30 kV) | preuzeto kako je zapisano |
| M5 | Generator 80002 'HE': skraćeni zapis (24 polja) | polja vlasnika nepotpuna, zapisano u nalazima |
