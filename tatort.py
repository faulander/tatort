import requests
from bs4 import BeautifulSoup
from loguru import logger
import sys
import json

linkKommissare = "https://www.daserste.de/unterhaltung/krimi/tatort/kommissare/tatort-filter-aktuelle-kommissare-100.html"
linkFolgenFirstPage = "https://www.daserste.de/unterhaltung/krimi/tatort/sendung/index.html"
lstKommissare = {}
lstTatorte = {}
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")


def splitStadt(Kommissar):
    posOpenBrace = Kommissar.find("(")
    posClosingBrace = Kommissar.find(")")
    lstKommissare[Kommissar[:posOpenBrace-1]] = Kommissar[posOpenBrace+1:posClosingBrace]


def splitTatorte(Tatort):
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
        lstTatorte[titel] = kommissar, stadt, datum


def getKommissare():
    r = requests.get(linkKommissare)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, features="html.parser")
        Kommissare = soup.find_all("h4", class_ = "headline")
        for Kommissar in Kommissare:
            splitStadt(Kommissar.get_text())
        logger.info("Seite der Kommissare aktualisiert.")
    else:
        logger.critical("Seite der Kommissare konnte nicht geladen werden.")


def getTatorte(page=None):
    r = requests.get(linkFolgenFirstPage)
    statuscode = r.status_code
    if statuscode == 200:
        soup = BeautifulSoup(r.content, features="html.parser")
        mx = soup.find("h3", class_ = "ressort paging").string
        mx = mx.split("|")
        if page:
            maxpage = page
        else:
            maxpage = int(mx[1].strip())
        logger.info("Seiten zu verarbeiten: {}", str(maxpage))
        table = soup.find("ul", class_ = "list")
        lines = table.find_all("li")
        for line in lines:
            link = line.find("a").text
            splitTatorte(link)
    currPage = 1
    while currPage < maxpage:   
        logger.info("Lade Seite: {}", currPage)
        linkFolgenFollowPages = "https://www.daserste.de/unterhaltung/krimi/tatort/sendung/tatort-alle-faelle-100~_seite-" + str(currPage) + ".html"
        r = requests.get(linkFolgenFollowPages)
        statuscode = r.status_code
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



if __name__ == "__main__":
    # getKommissare()
    # kommissare = json.dumps(lstKommissare, ensure_ascii=False)
    # print(kommissare)
    getTatorte(1)
    tatorte = json.dumps(lstTatorte, ensure_ascii=False)
    print(tatorte)
