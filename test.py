from flask import Flask
import unicodedata
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from tabulate import tabulate

app = Flask(__name__)
session = requests.Session()

def log_in_sol(user: str, password: str) -> bool:
    url = 'https://aplikace.skolaonline.cz/SOL/Prihlaseni.aspx'
    data = {
        "__EVENTTARGET": "dnn$ctr994$SOLLogin$btnODeslat",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": "",
        "__VIEWSTATEGENERATOR": "",
        "__VIEWSTATEENCRYPTED": "",
        "__PREVIOUSPAGE": "",
        "__EVENTVALIDATION": "",
        "dnn$dnnSearch$txtSearch": "",
        "JmenoUzivatele": user,
        "HesloUzivatele": password,
        "ScrollTop": "",
        "__dnnVariable": "",
        "__RequestVerificationToken": ""
    }
    postLogin = session.post(url, data=data)
    return postLogin.status_code == 200

def scrape_data(username: str, password: str):
    if not log_in_sol(username, password):
        return []

    url = "https://aplikace.skolaonline.cz/SOL/App/Hodnoceni/KZH003_PrubezneHodnoceni.aspx"
    response = session.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="G_ctl00xmainxgridHodnoceni")
    if not table:
        return []

    grades = []

    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        datum = cells[3].get_text(strip=True)
        predmet = cells[4].get_text(strip=True)
        tema = cells[5].get_text(strip=True)
        vaha = cells[6].get_text(strip=True)
        vysledek = cells[7].get_text(strip=True)
        slovni = cells[8].get_text(strip=True) if len(cells) > 6 else ""

        predmet = unicodedata.normalize("NFKD", predmet).encode("ascii", "ignore").decode("utf-8")

        grades.append({
            "Datum": datum,
            "Predmet": predmet,
            "Tema": tema,
            "Vaha": vaha,
            "Vysledek": vysledek,
            "Slovni_hodnoceni": slovni
        })

    return grades

def display_grades_table(grades):
    grouped = defaultdict(list)
    for grade in grades:
        grouped[grade["Predmet"]].append(grade)

    for subject, items in grouped.items():
        print(f"\n=== {subject} ===")
        table_data = []
        for g in items:
            table_data.append([
                g["Datum"],
                g["Tema"],
                g["Vaha"],
                g["Vysledek"],
                g["Slovni_hodnoceni"]
            ])
        print(tabulate(table_data, headers=["Datum", "Tema", "Vaha", "Výsledek", "Slovní hodnocení"], tablefmt="grid"))

if __name__ == "__main__":
    SOL_username = "KenV"
    SOL_password = "KenPorg2010"
    data = scrape_data(SOL_username, SOL_password)
    if data:
        display_grades_table(data)
    else:
        print("No data found or login failed.")
