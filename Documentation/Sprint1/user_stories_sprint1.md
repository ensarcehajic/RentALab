# User Stories – Login Sistem

Ovdje su definisane ključne korisničke priče (user stories) za login sistem, napisane u skladu sa INVEST modelom.

---

## User Story 1: Prijava (Login)

**Opis:**  
*Kao registrovani korisnik, želim da mogu unijeti svoje korisničko ime i šifru kako bih se prijavio u aplikaciju, kako bih pristupio svom nalogu i sadržaju.*

### Prihvatni kriteriji:
- Prikazuje se forma sa poljima za korisničko ime (ili email) i šifru
- Polja ne smiju biti prazna
- Ako su podaci tačni, korisnik se uspješno prijavljuje i preusmjerava na main dashboard
- Ako su podaci netačni, prikazuje se jasna poruka o grešci
- Lozinka se ne prikazuje (zamijenjena tačkicama)
- Postoji link "Forgot?" za recovery password-a

---

## User Story 2: Registracija korisnika

**Opis:**  
*Kao novi korisnik, želim da mogu kreirati novi nalog unosom svojih podataka, kako bih mogao pristupiti funkcijama aplikacije.*

### Prihvatni kriteriji:
- Prikazuje se forma za registraciju sa neophodnim poljima (ime, email, šifra, potvrda šifre)
- Sva obavezna polja moraju biti popunjena
- Lozinka mora zadovoljiti sigurnosne kriterije (dužina)
- Ako je registracija uspješna, korisnik se automatski prijavljuje ili dobija obavještenje o verifikaciji
- Ako email već postoji, prikazuje se odgovarajuća poruka
- Prikazuje se validacijska poruka ako šifre nisu identične
