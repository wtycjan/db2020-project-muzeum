# do bazy
import sql.wystawy as zapytania_wystawy
import sql.logowania as zapytania_logowania
import sql.sale as zapytania_sale

## do innych app
import app.wystawy as wystawy_app
import app.eksponaty as eksponaty_app

## dodatkowe
import datetime


class Uzytkownik(wystawy_app.niezalogowany):
    def __init__(self):
        super().__init__()
        bufor = self.logowanie()
        self.nazwa = bufor['nazwa']
        self.email = bufor['email']

    def logowanie(self):
        print("Oto nasz panel logowania")
        log = 1
        while (log):
            login = input("Login: ")
            haslo = input("Hasło: ")

            try:
                dane = zapytania_logowania.zaloguj(login, haslo)
                log = 0
                return dane[0]
            except Exception as wiadomosc:
                raise Exception(wiadomosc)

                if (log < 4):
                    ponownie = (input("Czy chcesz spróbować ponownie? Napisz 'tak' jeśli chcesz.")).lower()

                    if (ponownie == "tak"):
                        log += 1
                        print(f"Próba numer {log}")
                    else:
                        raise Exception("Niezgodność danych")
                        return 0
                else:
                    raise Exception("Za dużo prób")



class Pracownik(Uzytkownik):
    def __init__(self):
        super().__init__()
        bufor = self.dane()
        self.imie = bufor['imie']
        self.nazwisko = bufor['nazwisko']
        self.pracownikID = int(bufor['pracownikID'])
        self.budynekID = int(bufor['budynekID'])

    def dane(self):
        return zapytania_logowania.dane_pracownika(self.nazwa)[0]

    def dodaj_wystawe(self):
        try:
            nazwa = input("Podaj nazwę wystawy: ")
            startR = input("Będzie trwać od: \nRok:")
            startM = input("Miesiąc:")
            startD = input("Dzień:")
            start = datetime.datetime(int(startR), int(startM), int(startD))
            koniecR = input("Kończy się: \nRok:")
            koniecM = input("Miesiąc:")
            koniecD = input("Dzień:")
            koniec = datetime.datetime(int(koniecR), int(koniecM), int(koniecD))
            poczatek = start.strftime('%Y-%m-%d')
            zakonczenie = koniec.strftime('%Y-%m-%d')
            print('Wolne sale w twoim budynku: ')
            sale = zapytania_sale.pokaz_sale(self.budynekID)
            for iter, sala in enumerate(sale):
                print(f"{iter + 1}. Sala nr {sala['numer']}")
            #print(sale)
            sala = input("Podaj numer sali: ")

            wybor = input(
                f"Czy dane są poprawne? \n\t {nazwa} \n\t Od {poczatek} do {zakonczenie}\n\t Sala nr {sala}\n")
            wybor = wybor.lower()

            if (wybor == "tak"):
                # dodanie wystawy do bazy danych
                result = zapytania_wystawy.dodaj_wystawe(nazwa, poczatek, zakonczenie, self.pracownikID)
                # przypisanie ID wystawy do odpowiadajacej jej sali
                result2 = zapytania_sale.dodaj_wystawe(nazwa, sala, self.budynekID)

            if result & result2 == 1:
                print("Wystawa dodana")

        except Exception as wiadomosc:
            if wiadomosc == "Błąd bazy":
                print("Niestety baza nie może Cię obsłużyć. To jej wina")
            else:
                print(wiadomosc)
            return 0
        finally:
            return 1


def sciezka_uzytkownika():
    try:
        uzytkownik = Uzytkownik()
    except Exception as wiadomosc:
        if (str(wiadomosc) == "tuple index out of range"):
            print("Niepoprawne hasło")
        else:
            print(f"Tutaj przyda się programista bo {wiadomosc}")

    wyloguj = False


def sciezka_pracownika():
    try:
        pracownik = Pracownik()
    except Exception as wiadomosc:
        if (str(wiadomosc) == "tuple index out of range"):
            print("Niepoprawne hasło")
        else:
            print(f"Tutaj przyda się programista bo {wiadomosc}")

    wyloguj = False

    while (wyloguj == False):
        print("1. Dodaj wystawę\n"
              "2. Dodaj eksponat\n"
              "3. Wyloguj")
        funkcjonalnosc = input("Podaj numer, który Cię interesuje: ")

        if (funkcjonalnosc == "1"):
            print("\n \t ################### \n")
            pracownik.dodaj_wystawe()

        elif (funkcjonalnosc == "2"):
            print("\n \t ################### \n")
            pracownik.dodaj_eksponat()

        elif (funkcjonalnosc == "3"):
            print("Wylogowano \n\n")
            wyloguj = True
        else:
            print("Błąd wpisu")

def rejestracja():
    try:
        mail = input("Podaj email: ")
        res1 = zapytania_logowania.powtorzenie("email",mail)
        if len(res1) == 1:
            print("Ten email ma już przypisane konto.")
            return 0
        else:
            nazwa = input("Podaj nazwę użytkownika: ")
            res2 = zapytania_logowania.powtorzenie("nazwa",nazwa)
            if len(res2) == 1:
                print("Nazwa użytkownika już zajęta. Spróbuj ponownie.")
                return 0
            else:
                haslo = input("Podaj haslo: ")
                wybor = input(
                    f"Czy dane są poprawne? \n\t Email: {mail} \n\t Login: {nazwa} \n\t Haslo: {haslo}\n")
                wybor = wybor.lower()

                if (wybor == "tak"):
                    # dodanie uzytkownika do bazy danych
                     result = zapytania_logowania.dodaj_uzytkownika(mail, nazwa, haslo)

                if result == 1:
                   print("Twoje konto zostalo utworzone pomyślnie!")

    except Exception as wiadomosc:
        if wiadomosc == "Błąd bazy":
            print("Niestety baza nie może Cię obsłużyć. To jej wina")
        else:
            print(wiadomosc)
        return 0
    finally:
        return 1
