# Rent-A-Lab

Projekat za iznajmljivanje laboratorijske opreme na Fakultetu elektrotehnike u Tuzli.

## Informacije o timu

- Ime tima: **LabSquad**
- Članovi tima: Džana Dugonjić, Faris Alić, Adnan Hasić, Tarik Vehab, Ensar Ćehajić, Edin Ahmetbegovic
- Vođa tima: **Ensar Ćehajić**

## Komunikacija

- **Messenger**
- **Google Meet**

**TRENUTNO SE APLIKAICJA NALAZI U full_stack_testing BRANCHU!**

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

4. Pokreni aplikaciju:
```bash
python app.py
```

## Funkcionalnosti

-  **Login sistem** s ulogama:  (trenutno se validacija vrši u samom pythonu i samo username: admin password: admin mogu ući, autentifikacija preko baze je u izradi)
  - **Student**: može pregledati i zatražiti opremu  
  - **Laborant**: vidjeti zahtjeve i detalje o korisnicima

- **Baza podataka** (PostgreSQL) sa tabelom `users`  
- **Zahtjevi za inajmljivanje** sa vremenskim ograničenjem (u planu)
- **Admin dashboard** (u planu)


## Status implementacije

| Funkcionalnost               | Status      |
|-----------------------------|-------------|
| Login sistem                | ✅ Završeno |
| Frontend dizajn             | ✅ Završeno |
| Razvoj baze za login        | ✅ Završeno |
| Autentifikacija iz baze     | ⏳ U razvoju |
| Prikaz dostupne opreme      | 🔜 Planirano |
| Rezervacija opreme          | 🔜 Planirano |
| Admin panel za laboranta    | 🔜 Planirano |



