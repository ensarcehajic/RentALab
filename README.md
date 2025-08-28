# Rent-A-Lab

Ovaj repozitorij predstavlja kulminaciju rada ovog tima na izradi praktičnog rješenja za sistem upravljanja iznajmljivanjem laboratorijske opreme na Fakultetu elektrotehnike Univerziteta u Tuzli. Projekat je razvijen s ciljem digitalizacije i unapređenja procesa rezervacije i praćenja korištenja opreme u i izvan prostora laboratorije, omogućavajući studentima i osoblju jednostavniji i transparentniji način upravljanja resursima.

## Informacije o timu

- Ime tima: **LabSquad**
- Članovi tima: Džana Dugonjić, Faris Alić, Adnan Hasić, Tarik Vehab, Ensar Ćehajić, Edin Ahmetbegovic
- Vođa tima: Ensar Ćehajić

## Komunikacija

- **Messenger**
- **Google Meet**


## Korištene tehnologije

- **Backend**  : Python, Flask, SQLAlchemy
- **Frontend** : HTML, CSS, Jinja2
- **Database** : PostgreSQL
- **Alati**    : VS Code, GitHub, Jira


## Set-up

1. Kloniraj repozitorij:
```bash
git clone git@github.com:ensarcehajic/RentALab.git
cd RentALab
```

2. Kreiraj i aktiviraj virtualno okruženje:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instaliraj zavisnosti:
```bash
pip install -r requirements.txt
```
4. Instaliraj PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
```
5. Pokreni PostgreSQL:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -i -u postgres
psql
```
6. Postavljanje podataka o bazi(ako se ne postave ovi isti podaci, potrebno je ažurirat link baze):
```bash
CREATE USER admin WITH PASSWORD '1234';
CREATE DATABASE rentalab OWNER admin;
GRANT ALL PRIVILEGES ON DATABASE rentalab TO admin;
```
7. Prebaci na rentalab bazu podatka:
```bash
\c rentalab
```

8. Pokreni aplikaciju:
```bash
python run.py
```

## Funkcionalnosti

-  **Register sistem** za studente
-  **Login sistem** s ulogama:
  - **Student**: može pregledati i zatražiti opremu  
  - **Laborant**: upravlja opremom,prati zahtjeve, izdaje opremu
  - **Profesor**: upravlja zahtjevima za iznajmljivanje
-  **Verifikacija email adrese**
-  **Obnova zaboravljene lozinke**
-  **Pregled opreme**
-  **Dodavanje opreme ručno ili uz pomoć CVS dokumenta**
-  **Izmjena podataka opreme**
-  **Admin panel za dodavanje nastavnog osoblja**
-  **Pregled i uređivanje profila korisnika**
-  **Podnošenje zahtjeva za iznajmljivanje opreme**
-  **Automatsko slanje maila zaduženom profesoru**
-  **Pregled zahtjeva i upravljanje istima**





