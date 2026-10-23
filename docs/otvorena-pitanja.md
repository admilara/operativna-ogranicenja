# Otvorena pitanja

Nedostatke samih smjernica i modela vidi na stranici [Nedostaci smjernica i podataka](nedostaci-smjernica.md).

| # | Pitanje | Utječe na | Privremeno rješenje |
|---|---|---|---|
| 1 | Tablice po položajima preklopke za PST-ove s dijagonalnom regulacijom i tumačenje zahtjeva "naponska regulacija + podešavanje kuta" ([N1](nedostaci-smjernica.md)) | optimizacija kutova PST-ova, naponi, tokovi 400/220 kV | samo kutni model uz upozorenje (pogl. 2) |
| 2 | Mjera opterećenja u ispisu HOPS-a: struja ili MVA | Tablice 5–7, broj preopterećenja | vodovi strujno, transformatori MVA; računaju se obje (pogl. 4) |
| 3 | Koji HTLS vodič HOPS predviđa po razredu voda (alat pretpostavlja ACCC istog promjera: ROVINJ, LISBON, STOCKHOLM 2L) | nazivna vrijednost nakon zamjene | `config/htls_ratings.csv` (pogl. 7, §7.2) |
| 4 | Podaci o spremnicima hibridnih postrojenja ($P_{BS}$, $E_{BS}$, $\eta$, $T_{ev}$) — **po projektu** | $E_{oo}$ za SE + BS | `config/hybrid_storage.csv`; dvije granice procjene (pogl. 5, §5.11) |
| 5 | RHE Velebit u crpnom radu (nema zapisa u modelu) | granice varijante V1 | samo turbinski raspon |
| 6 | Model susjednih sustava (za REI ekvivalent) | ispadi prekograničnih vodova, zastavice G1–G3, varijanta V3 | stalne PQ injekcije (pogl. 3) |
| 7 | Granice jalove snage jedinice pri ograničenju djelatne snage: preračunati na novu $P_G$ (cos φ 0,95, kao u modelu) ili zadržati (prema $P_{\max}$, NC RfG) | naponi, jalova snaga i struja vodova uz korisnike | još nije odlučeno (pogl. 1, §1.3) |

## Riješeno

| Pitanje | Odluka |
|---|---|
| Jedinični troškovi mjera | Prilog 4 smjernica → `config/unit_costs.csv` (pogl. 7, §7.4) |
| Ograničenje spremnika u režimu punjenja (scenariji D, E) | smanjenje snage punjenja, uz zastavicu (pogl. 5, §5.7) |
| Melina T1: RATE1 namota 1 = 0 | SBASE para namota, uz zastavicu ([M4](nedostaci-smjernica.md)) |
