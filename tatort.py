import requests
from bs4 import BeautifulSoup
from loguru import logger
import sys


def openPage(link):
    r = requests.get(link)
    statuscode = r.status_code
    return r, statuscode


def splitTatorte(Tatort):
    # print(repr(Tatort))
    tatort = Tatort.replace("\n\n", "\n")
    tatort = tatort.replace("\n", "|")
    tmp = tatort.split("|")
    for t in range(0, len(tmp)):
        tmp[t].strip()
    if len(tmp) > 2:
        titel = tmp[0]
        kommissar = tmp[1]
        if kommissar.startswith("(") and kommissar.endswith(")"):
            kommissar = kommissar[1:-1]
        posOpenBrace = kommissar.find("(")
        posCloseBrace = kommissar.find(")")
        if len(kommissar) > 3:
            stadt = kommissar[posOpenBrace+1:posCloseBrace]
            kommissar = kommissar[:posOpenBrace-1]
            datum = tmp[2]
        else:
            stadt = ""
            kommissar = ""
            datum = tmp[1]
        return titel, kommissar, stadt, datum


def getTatorte(page=None):
    r, statuscode = openPage("https://www.daserste.de/unterhaltung/krimi/tatort/sendung/index.html")
    lstTatorte = {}
    if statuscode == 200:
        soup = BeautifulSoup(r.content, features="html.parser")
        if page:
            maxpage = page
        else:
            mx = soup.find("h3", class_ = "ressort paging").string
            mx = mx.split("|")
            maxpage = int(mx[1].strip())
        logger.info("Seiten zu verarbeiten: {}", str(maxpage))
        table = soup.find("ul", class_ = "list")
        lines = table.find_all("li")
        for line in lines:
            link = line.find("a").text
            titel, kommissar, stadt, datum = splitTatorte(link)
            lstTatorte[titel] = kommissar, stadt, datum
    currPage = 1
    while currPage < maxpage:
        logger.info("Lade Seite: {}", currPage)
        r, statuscode = openPage("https://www.daserste.de/unterhaltung/krimi/tatort/sendung/tatort-alle-faelle-100~_seite-" + str(currPage) + ".html")
        if statuscode == 200:
            soup = BeautifulSoup(r.content, features="html.parser")
            table = soup.find("ul", class_ = "list")
            lines = table.find_all("li")
            for line in lines:
                link = line.find("a").text
                splitTatorte(link)
        else:
            logger.error("Problem auf Seite {}", currPage)
        currPage += 1
    return lstTatorte


if __name__ == "__main__":
    logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
    print(getTatorte(1))
