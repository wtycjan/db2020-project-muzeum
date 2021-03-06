import os
import pymysql
from . import polaczenie
## dodatkowe
import datetime

def wyszukiwarka_aktywnych_wystaw(dzis):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            # wykonujemy zapytanie do bazy i wyświetlamy
            sql = (
                f"SELECT wystawa.nazwa, wystawa.koniec FROM wystawa "
                f"WHERE wystawa.koniec > DATE '{dzis}' AND wystawa.poczatek < DATE '{dzis}';"
            )
            cursor.execute(sql)
            result = cursor.fetchall()

        connection.close()
        return result
    except:
        raise Exception("Błąd bazy")



def najczesciej_odwiedzane_wystawy(wybor, dzis):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            # konstruujemy odpowiednie zapytania
            if(wybor == "nie"):
                sql2 = (
                    "SELECT wystawa.nazwa, wystawa.koniec, wystawa.poczatek, COUNT(bilet.biletID) "
                    "AS ilosc FROM wystawa JOIN bilet ON wystawa.wystawaID = bilet.wystawaID "
                    "GROUP BY wystawa.wystawaID HAVING ilosc > 7 "
                    "ORDER BY ilosc DESC LIMIT 5;"
                )

            elif(wybor == "tak"):
                sql2 = (
                    f"SELECT wystawa.nazwa, wystawa.koniec, wystawa.poczatek, COUNT(bilet.biletID) AS ilosc "
                    f"FROM wystawa JOIN bilet ON wystawa.wystawaID = bilet.wystawaID "
                    f"WHERE DATE '{dzis}' BETWEEN wystawa.poczatek AND wystawa.koniec "
                    f"GROUP BY wystawa.wystawaID ORDER BY ilosc DESC LIMIT 5;"
                )

            else:
                raise Exception("Niepoprawnie wpisany tekst")

            cursor.execute(sql2)
            result = cursor.fetchall()

        connection.close()
        return result
    except:
        raise Exception("Błąd bazy")


def dodaj_wystawe(nazwa, poczatek, zakonczenie, pracownik, lista_sal, budynekID, vip):
    connection = polaczenie()
    try:
        with connection.cursor() as cursor:
            # dodajemy do tablicy Wystawa

            sql = (
                f"INSERT INTO wystawa (nazwa, poczatek, koniec, pracownikID) " 
                f" VALUES('{nazwa}', '{poczatek}' ,'{zakonczenie}', {pracownik});"
            )
            cursor.execute(sql)

            sql2 = (
                f"SELECT wystawa.wystawaID FROM wystawa WHERE wystawa.nazwa = '{nazwa}';"
            )

            cursor.execute(sql2)
            result = ((cursor.fetchall())[0])["wystawaID"]

            for sala_numer in lista_sal:
                sql3 =  (
                    f"SELECT sala.salaID FROM sala WHERE sala.numer = {sala_numer} AND sala.budynekID = {budynekID};"
                )
                cursor.execute(sql3)
                salaID = ((cursor.fetchall())[0])['salaID']

                sql3_1 = (
                    f"INSERT INTO wystawa_sala(salaID, wystawaID) VALUES ({salaID}, {result});"
                )
                cursor.execute(sql3_1)


            if (vip == "tak"):
                # 3 i 4 to vip
                sql4 = f"INSERT INTO cena_wystawa(cenaID, wystawaID) VALUES (1, {result}), (2,  {result}), (3, {result}), (4,  {result});"
            else:
                # 1 i 2  to  tylko zwykle
                sql4 = f"INSERT INTO cena_wystawa(cenaID, wystawaID) VALUES (1, {result}), (2,  {result});"
            cursor.execute(sql4)
            connection.commit()
            w = 1

    except Exception as błąd:
        w = 0
        connection.rollback()
        raise Exception(błąd)
    finally:
        connection.close()
        return w

def dodaj_bilet(cena, data,wystawa,  nazwa):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            # dodajemy do tablicy Bilet
            sql = (
                f"INSERT INTO bilet (cena, data_zakupu, wystawaID, nazwa_uzytkownika) " 
                f" VALUES({cena}, '{data}' , (SELECT wystawaID FROM wystawa WHERE nazwa = '{wystawa}') , '{nazwa}' );"
            )
            cursor.execute(sql)
            connection.commit()
            connection.close()
        return 1
    except:
        raise Exception("Błąd bazy")


def sprawdz_ceny(nazwa_wystawy):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            sql = (
                f"SELECT DISTINCT wystawa.nazwa, cena.typ, cena.koszt "
                f"FROM wystawa JOIN cena_wystawa ON wystawa.wystawaID = cena_wystawa.wystawaID "
                f"JOIN cena ON cena.cenaID = cena_wystawa.cenaID "
                f"WHERE wystawa.nazwa = '{nazwa_wystawy}';"
            )
            cursor.execute(sql)
            result = cursor.fetchall()
        connection.close()
        return result
    except Exception as bład:
        raise Exception(bład)


def sprawdz_bilety(uzytkownik):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            dzisiejsza_data = datetime.datetime.now()
            dzis = dzisiejsza_data.strftime("%Y-%m-%d")

            # wykonujemy zapytanie do bazy i wyświetlamy
            sql = f"SELECT bilet.data_zakupu, wystawa.nazwa " \
                  f"FROM wystawa JOIN bilet ON wystawa.wystawaID = bilet.wystawaID " \
                  f"WHERE wystawa.koniec > DATE '{dzis}' AND nazwa_uzytkownika='{uzytkownik}';"

            cursor.execute(sql)
            result = cursor.fetchall()

        connection.close()
        return result
    except Exception as błąd:
        raise Exception(błąd)

def usun_bilet(nazwa,data,uzytkownik):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            # dodajemy do tablicy Bilet
            sql = (
                f"DELETE bilet FROM bilet INNER JOIN wystawa on wystawa.wystawaID=bilet.wystawaID "
                f"WHERE bilet.data_zakupu='{data}' AND wystawa.nazwa='{nazwa}' AND nazwa_uzytkownika='{uzytkownik}';"
            )
            cursor.execute(sql)
            connection.commit()
            connection.close()
        return 1
    except Exception as błąd:
        raise Exception(błąd)


def statystyki(budynekID):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            sql = (
                f"SELECT COUNT(bilet.biletID) as ilosc, wystawa.nazwa "
                f"FROM bilet "
                f"JOIN wystawa ON wystawa.wystawaID = bilet.wystawaID "
                f"JOIN pracownik ON pracownik.pracownikID = wystawa.pracownikID "
                f"JOIN budynek ON budynek.budynekID = pracownik.budynekID "
                f"WHERE budynek.budynekID = {budynekID} "
                f"GROUP BY wystawa.nazwa "
                f"ORDER BY ilosc;"
            )
            cursor.execute(sql)
            result = cursor.fetchall()
        connection.close()
        return result
    except Exception as błąd:
        raise Exception(błąd)


def eksponaty_z_wystawy(nazwa):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            sql = (
                f"SELECT eksponat.tytul, eksponat.rok_powstania, eksponat.opis, autor.imie, autor.nazwisko, autor.pseudonim "
                f"FROM eksponat "
                f"JOIN eksponat_autor ON eksponat_autor.eksponatID = eksponat.eksponatID "
                f"JOIN autor ON autor.autorID = eksponat_autor.autorID "
                f"LEFT JOIN wystawa ON eksponat.wystawaID = wystawa.wystawaID "
                f"WHERE wystawa.nazwa = '{nazwa}';"
            )
            cursor.execute(sql)
            result = cursor.fetchall()
        connection.close()
        return result
    except Exception as błąd:
        raise Exception(błąd)

def statystyki_dzienne(dzien):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            sql = (
                f"SELECT COUNT(bilet.biletID) as ilosc, SUM(bilet.cena) as zarobki, wystawa.nazwa, "
                f"budynek.nazwa as budynek, budynek.budynekID "
                f"FROM bilet LEFT "
                f"JOIN wystawa ON wystawa.wystawaID = bilet.wystawaID "
                f"LEFT JOIN pracownik ON pracownik.pracownikID = wystawa.pracownikID "
                f"LEFT JOIN budynek ON budynek.budynekID = pracownik.budynekID "
                f"WHERE bilet.data_zakupu = DATE '{dzien}' "
                f"GROUP BY budynek.nazwa, wystawa.nazwa"
            )
            cursor.execute(sql)
            result = cursor.fetchall()
        connection.close()
        return result
    except Exception as błąd:
        raise Exception(błąd)


