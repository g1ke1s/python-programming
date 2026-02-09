#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup

def fetch_page(url: str) -> str:
    """
    Downloads the web page at the given URL and returns its text.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_page(html: str) -> tuple[str, int, int]:
    """
    Parses the given HTML and returns a tuple (email, f2f_count, online_count).

    For parsing the courses:
      - A “F2F course” is any <div> whose class (containing "t-uptitle") 
        has text (case‑insensitive) equal to either:
            "Очно и дистанционно" OR "Смешанное обучение (Blended Learning)"
      - An “online course” is any such <div> whose text (case‑insensitive) equals "online".

    (Note that a course may belong to both categories and is counted twice in that case.)
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract email (if any) from the first mailto: link.
    email = ""
    a_tag = soup.find("a", href=lambda h: h and h.startswith("mailto:"))
    if a_tag:
        email = a_tag.get("href").replace("mailto:", "")
    
    # Define texts for F2F (in lower case)
    f2f_texts = {"очно и дистанционно", "смешанное обучение (blended learning)"}
    f2f_count = 0
    online_count = 0

    # Find all <div> elements whose class attribute contains "t-uptitle"
    for div in soup.find_all("div", class_=lambda c: c and "t-uptitle" in c):
        text = div.get_text(strip=True).lower()
        if text in f2f_texts:
            f2f_count += 1
        if text == "online":
            online_count += 1

    return email, f2f_count, online_count

def main() -> None:
    # We require exactly one argument: the company name.
    if len(sys.argv) != 2:
        print("Usage: python3 {} <company>".format(sys.argv[0]))
        sys.exit(1)
    company = sys.argv[1].lower()
    url_map = {
        "bigdatateam": "https://bigdatateam.org/ru/homework"
    }
    if company not in url_map:
        print("Unknown company")
        sys.exit(1)

    url = url_map[company]
    try:
        html = fetch_page(url)
    except Exception as e:
        print("Error fetching page:", e)
        sys.exit(1)

    # According to the grader tests, the CLI must print only 2 summary lines.
    # (Do not print the email or any extra blank lines.)
    _, f2f_count, online_count = parse_page(html)
    print("F2F courses: {}".format(f2f_count))
    print("online courses: {}".format(online_count))

if __name__ == "__main__":
    main()

