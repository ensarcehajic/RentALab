# Rent-A-Lab

Projekat za iznajmljivanje laboratorijske opreme na Fakultetu elektrotehnike u Tuzli.

## Informacije o timu

- Ime tima: **LabSquad**
- Članovi tima: Džana Dugonjić, Faris Alić, Adnan Hasić, Tarik Vehab, Ensar Ćehajić, Edin Ahmetbegovic
- Vođa tima: **Ensar Ćehajić**

## Komunikacija

- **Messenger**
- **Google Meet**


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

-  **Login sistem** s ulogama:
  - **Student**: može pregledati i zatražiti opremu  
  - **Laborant**: vidjeti zahtjeve, odobriti iste i detalje o korisnicima (u planu)
- **Baza podataka** (PostgreSQL) sa tabelom `users` i `oprema`
- **Zahtjevi za iznajmljivanje** sa vremenskim ograničenjem (u planu)
- **Admin dashboard** 


## Status implementacije

| Funkcionalnost               | Status      |
|-----------------------------|-------------|
| Login sistem                | ✅ Završeno |
| Register sistem             | ✅ Završeno |
| Frontend dizajn             | ✅ Završeno |
| Razvoj baze za login        | ✅ Završeno |
| Autentifikacija iz baze     | ✅ Završeno |
| Prikaz dostupne opreme      | ✅ Završeno |
| Filtriranje dostupne opreme | ✅ Završeno |
| Preuzimanje .csv opreme     | ✅ Završeno |
| Rezervacija opreme          | 🔜 Planirano |
| Admin panel za laboranta    | 🔜 Planirano |



