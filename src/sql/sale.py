import os
import pymysql
from . import polaczenie
import pandas as pd

def pokaz_dostepne_sale(budynekID, poczatek, koniec):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            # wykonujemy zapytanie do bazy
            sql = (
                f"SELECT sala.numer, sala.wielkosc, sala.salaID FROM sala "
                f"WHERE sala.salaID NOT IN "
                f"( SELECT sala.salaID FROM budynek "
                f"INNER JOIN sala ON budynek.budynekID = sala.budynekID "
                f"LEFT JOIN wystawa_sala ON sala.salaID = wystawa_sala.salaID "
                f"LEFT JOIN wystawa ON wystawa_sala.wystawaID = wystawa.wystawaID "
                f"WHERE (budynek.budynekID = {budynekID} AND "
                f"((DATE '{poczatek}' BETWEEN wystawa.poczatek AND wystawa.koniec) OR "
                f"(DATE '{koniec}' BETWEEN wystawa.poczatek AND wystawa.koniec))) OR "
                f"( budynek.budynekID != {budynekID}));"
            )

            #sql = f"SELECT sala.numer FROM sala " \
            #f"WHERE sala.budynekID = {budynek} AND sala.wystawaID IS NULL"

            cursor.execute(sql)
            result = cursor.fetchall()
        connection.close()
        return result
    except Exception as błąd:
        raise Exception(f"Błąd bazy \n Swojemu programiście powiedz: {błąd}")


def dodaj_wystawe(wystawa, sala, budynek):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            sql = f"INSERT INTO wystawa_sala(salaID, wystawaID) VALUES ({sala}, {wystawa})"
            cursor.execute(sql)
            connection.commit()
        connection.close()
        return 1
    except Exception as błąd:
        raise Exception(błąd)


def wielkosc_wystawy(cos):
    try:
        connection = polaczenie()
        with connection.cursor() as cursor:
            sql2 = (
                f"SELECT COUNT(eksponat.eksponatID) as ilosc_eksponatow, wystawa.nazwa FROM eksponat "
                f"LEFT JOIN wystawa ON wystawa.wystawaID = eksponat.wystawaID GROUP BY wystawa.wystawaID;"
            )

            sql3 = (
                f"SELECT SUM(sala.wielkosc) as wielkosc_wystawy, wystawa.nazwa FROM wystawa "
                f"LEFT JOIN wystawa_sala ON wystawa_sala.wystawaID = wystawa.wystawaID "
                f"LEFT JOIN sala ON sala.salaID = wystawa_sala.salaID "
                f"GROUP BY wystawa.wystawaID;"
            )
            cursor.execute(sql2)
            result2 = pd.DataFrame(cursor.fetchall())

            cursor.execute(sql3)
            result3 = pd.DataFrame(cursor.fetchall())

            result = pd.merge(result3, result2, on="nazwa", how='outer')

        connection.close()
        return result

    except Exception as błąd:
        raise Exception(błąd)

