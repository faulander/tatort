import requests
from bs4 import BeautifulSoup
from loguru import logger
import sys
import json


def openPage(link):
    r = requests.get(link)
    statuscode = r.status_code
    return r, statuscode


def splitTatorte(Tatort):
    # print(repr(Tatort))
    tatort = Tatort.replace("\n\n", "\n")
    tatort = tatort.replace("\n", "|")
    tmp = tatort.split("|")
    # logger.debug(tmp)
    # logger.debug(str(len(tmp)))
    if len(tmp) > 2:
        titel = tmp[0]
        # logger.debug(titel)
        kommissar = tmp[1]
        # logger.debug(kommissar)
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
    else:
        titel = tmp[0]
        # logger.debug(titel)
        kommissar = ""
        stadt = ""
        datum = tmp[1]
    return titel, kommissar, stadt, datum


def getTatorte(page=0):
    r, statuscode = openPage("https://www.daserste.de/unterhaltung/krimi/tatort/sendung/index.html")
    lstTatorte = {}
    if statuscode == 200:
        soup = BeautifulSoup(r.content, features="html.parser")
        if page != 0:
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
    #logger.debug(maxpage)
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
                logger.debug(link)
                titel, kommissar, stadt, datum = splitTatorte(link)
                lstTatorte[titel] = kommissar, stadt, datum
        else:
            logger.error("Problem auf Seite {}", currPage)
        currPage += 1
    return lstTatorte


def writeFile(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
    # getTatorte delivers a json with Tatort Episodes.
    # If no argument is parsed, it delivers ALL ever broadcasted Tatorts.
    # Argument "1" delivers the latest 50 as is much faster
    # Argument "2" delivers 51-100 and so on
    #print(getTatorte())

    # writeFile saves the Tatort as JSON in a file:
    # writeFile("tatorte.json", getTatorte())

