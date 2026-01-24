from bs4 import BeautifulSoup
from datetime import datetime

def parse_grades(html):
    soup = BeautifulSoup(html, "html.parser")
    grades = []

    rows = soup.select("table tr")[1:]  # skip header

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        subject = cols[0].text.strip()
        grade = int(cols[1].text.strip())
        weight = float(cols[2].text.strip())
        date = datetime.strptime(cols[3].text.strip(), "%d.%m.%Y").date()

        grades.append({
            "subject": subject,
            "grade": grade,
            "weight": weight,
            "date": date
        })

    return grades
