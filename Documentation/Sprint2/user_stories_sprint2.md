# User Stories 

Ovdje su definisane ključne korisničke priče (user stories) za Sprint 2, napisane u skladu sa INVEST modelom.

---

## User Story 1: Registracija korisnika

**Opis:**  
*Kao novi korisnik, želim da mogu kreirati novi nalog unosom svojih podataka, kako bih mogao pristupiti funkcijama aplikacije.*

### Prihvatni kriteriji:
- Prikazuje se forma za registraciju sa neophodnim poljima (ime, email, šifra, potvrda šifre)
- Sva obavezna polja moraju biti popunjena
- Lozinka mora zadovoljiti sigurnosne kriterije (dužina)
- Ako je registracija uspješna, korisnik se automatski prijavljuje ili dobija obavještenje o verifikaciji
- Ako email već postoji, prikazuje se odgovarajuća poruka
- Prikazuje se validacijska poruka ako šifre nisu identične

---

## User Story 2: Implementacija sistema za dodavanje opreme
**Opis:**  
*Kao administrator želim da mogu dodati novu laboratorijsku opremu ručno unošenjem potrebnih podataka ili učitavanjem .csv fajla kako bih jednostavno i brzo ažurirao listu trenutno dostupne opreme.*

### Prihvatni kriteriji:
- Korisnik može unijeti naziv opreme i broj komada putem forme
- Klikom na dugme "Dodaj", oprema se pohranjuje u bazu podataka
- Unos se može izvršiti i učitavanjem .csv fajla sa kolonama: 'Naziv' & 'Količina'
- Svi dodani podaci iz fajla se spremaju u bazu nakon potvrde korisnika

---

## User Story 3: Implementacija sistema za pregled dostupne opreme
**Opis:**  
*Kao korisnik sistema želim da mogu vidjeti listu dostupne laboratorijske opreme kako bih imao uvid u trenutno stanje i raspoloživost opreme.*

### Prihvatni kriteriji:
- Klikom na stavku "Pregled opreme" u dashboardu, korisnik se preusmjerava na stranicu s listom opreme
- Stranica prikazuje tabelu sa svom dostupnom opremom (naziv, količina).
- Postoji opcija koja generiše CSV fajl sa trenutnim prikazom tabele.

---

## User Story 4: Implementacija main dashboard-a
**Opis:**
*Kao korisnik sistema želim da imam jasan i funkcionalan glavni dashboard kako bih brzo pristupio svim ključnim funkcijama i imao pregled osnovnih informacija.*

### Prihvatni kriteriji:
- Dashboard prikazuje kartice ili dugmad za sve glavne funkcije (npr. Dodavanje opreme, Pregled opreme, Statistika)
- Svaka opcija vodi na odgovarajuću stranicu prilikom klika


