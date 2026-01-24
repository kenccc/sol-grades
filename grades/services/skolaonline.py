from bs4 import BeautifulSoup
import requests
import unicodedata

def log_in_sol(user: str, password: str) -> requests.Session | None:
    """
    Logs into SkolaOnline and returns a fresh session if successful.
    Does NOT reuse global sessions.
    """
    session = requests.Session()
    url = "https://aplikace.skolaonline.cz/SOL/Prihlaseni.aspx"
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
    response = session.post(url, data=data)
    if response.status_code == 200 and "Přihlášení" not in response.text:
        return session
    return None


def fetch_grades(user: str, password: str):
    """
    Fetch grades securely for the given user. Creates a fresh session
    each time. Returns a list of grades or None if login fails.
    """
    session = log_in_sol(user, password)
    if not session:
        return None

    grades_url = "https://aplikace.skolaonline.cz/SOL/App/Hodnoceni/KZH003_PrubezneHodnoceni.aspx"
    response = session.get(grades_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="G_ctl00xmainxgridHodnoceni")
    if not table:
        return None

    grades_list = []

    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 9:
            continue

        datum = cols[3].get_text(strip=True)
        predmet = cols[4].get_text(strip=True)
        tema = cols[5].get_text(strip=True)
        vaha = cols[6].get_text(strip=True)
        vysledek = cols[7].get_text(strip=True)
        slovni = cols[8].get_text(strip=True) if len(cols) > 8 else ""

        predmet = unicodedata.normalize("NFKD", predmet).encode("ascii", "ignore").decode("utf-8")

        grades_list.append({
            "Datum": datum,
            "Predmet": predmet,
            "Tema": tema,
            "Vaha": vaha,
            "Vysledek": vysledek,
            "Slovni_hodnoceni": slovni
        })

    return grades_list if grades_list else None
