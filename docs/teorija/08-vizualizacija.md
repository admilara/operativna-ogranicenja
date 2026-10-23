# 8. Vizualizacija rezultata

Rezultati za HOPS ostaju u obliku koji smjernice propisuju: Tablice 5–8 i Excel datoteka po
Tablici 7. Ostali prikazi služe za provjeru rezultata, razgovor s HOPS-om i slike u izvještaju.

## 8.1 Obvezni tablični prikazi

| Tablica smjernica | Sadržaj | Izlaz alata |
|---|---|---|
| Tablica 5 | osnovni proračun: P, Q, I, %In za preopterećene elemente, korisnici isključeni / uključeni, po scenariju | list u Excelu po godini |
| Tablica 6 | N-1: najnepovoljniji ispad, broj preopterećenja, P, Q, I, %In | list u Excelu po scenariju i godini |
| Tablica 7 | sva preopterećenja: ispad, element, termička moć, P/Q/S/% u N i N-1 | zasebna Excel datoteka |
| Tablica 8 | prijedlog STUM-a i troškovi | list u Excelu |

## 8.2 Dodatni prikazi

### Toplinska karta preopterećenja

Matrica **ispadi × elementi**, boja = opterećenje u %, jedna po scenariju i godini. Prikazuju se
samo ispadi i elementi s barem jednim preopterećenjem. Odmah se vidi koji su ispadi mjerodavni i
koji su elementi kritični u više ispada.

### Matrica doprinosa

Matrica **korisnici (Owner 3) × preopterećeni elementi**, boja = doprinos $C_{k,i}$ u MVA
(najnepovoljniji ispad). To je vizualni oblik formule [1]: tko uzrokuje koje preopterećenje.
Prikazuje se u tri varijante uravnoteženja jedna do druge — razlike među varijantama ovdje su
najočitije.

### Vremenski tijek ograničenja

Za svakog korisnika stepenasti graf $E_{oo,god}(y)$ za 2029.–2035., složen po scenarijima, s
oznakama godina u kojima počinju djelovati mjere. Stepenice padaju kako mjere ulaze u pogon — to
vremenski tijek STUM-a objašnjava bolje od tablice. Raspon između varijanti uravnoteženja
prikazuje se kao pojas.

### Karta mreže s opterećenjima

Mreža na zemljopisnoj karti, boja voda = opterećenje. `.raw` nema koordinate, pa trebaju vanjski
podaci (npr. INSPIRE/ATOM skupovi ili geopodaci HOPS-a). pandapower ima prikaz u plotlyju.

### Interaktivna HTML stranica

Jedna samostalna stranica s izbornikom scenarija, godine i varijante uravnoteženja i sa svim
gornjim prikazima. Prikladna za dijeljenje rezultata i razgovor s HOPS-om; Excel ostaje službeni
izlaz. Stranica se generira iz rezultata i **ne objavljuje se** na GitHub Pages jer sadrži
podatke o korisnicima u postupku priključenja.
