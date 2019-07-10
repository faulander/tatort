import requests
from bs4 import BeautifulSoup
from loguru import logger
import sys
import json


def openPage(link):
    r = requests.get(link)
    statuscode = r.status_code
    return r, statuscode


def getDescription(link):
    description = ""
    r, statuscode = openPage(link)
    if statuscode == 200:
        soup = BeautifulSoup(r.content, features="html.parser")
        table = soup.find("div", class_ = "box")
        paragraphs = table.find_all("p", class_ = "text small")
        for p in paragraphs:
            description = description + p.text + "\n"
        # logger.info(description)
    else:
        logger.error("Detailpage konnte nicht geladen werden.")
        description = ""
    return description


def splitTatorte(Tatort):
    tatort = Tatort.replace("\n\n", "\n")
    tatort = tatort.replace("\n", "|")
    tmp = tatort.split("|")
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
    else:  # for the one documentary which doesn't provide Detective and Town
        titel = tmp[0]
        kommissar = ""
        stadt = ""
        datum = tmp[1]
    return titel, kommissar, stadt, datum


def getTatorte(page=0, description=False):
    nr = 1
    lstTatorte = {}
    maxpage = 99
    currPage = 1
    while currPage < maxpage:
        # logger.info("Lade Seite: {}", currPage)
        if currPage == 1:
            r, statuscode = openPage("https://www.daserste.de/unterhaltung/krimi/tatort/sendung/index.html")
            soup = BeautifulSoup(r.content, features="html.parser")
            if page != 0:
                maxpage = page
            else:
                mx = soup.find("h3", class_ = "ressort paging").string
                mx = mx.split("|")
                maxpage = int(mx[1].strip())
        else:
            r, statuscode = openPage("https://www.daserste.de/unterhaltung/krimi/tatort/sendung/tatort-alle-faelle-100~_seite-" + str(currPage) + ".html")
        if statuscode == 200:
            soup = BeautifulSoup(r.content, features="html.parser")
            table = soup.find("ul", class_ = "list")
            lines = table.find_all("li")
            for line in lines:
                link = line.find("a")
                href = "https://www.daserste.de" + link["href"]
                link = link.text
                titel, kommissar, stadt, datum = splitTatorte(link)
                if description:
                    desc = getDescription(href)
                    lstTatorte[nr] = titel, kommissar, stadt, datum, href, desc
                else:
                    lstTatorte[nr] = titel, kommissar, stadt, datum, href
                # logger.debug(lstTatorte[nr])
                nr += 1
        else:
            logger.error("Problem auf Seite {}", currPage)
        logger.info("Seite {} von {} Seiten verarbeitet, {} Tatorte verarbeitet.", str(currPage), str(maxpage), str(nr))
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
    # Parameter "description" also downloads the description of the episodes.
    # Please take care that this may take a very long time.
    # print(getTatorte(1, description=True))

    # writeFile saves the Tatort as JSON in a file:
    tatorte = getTatorte(description=True)
    writeFile("tatorte.json", tatorte)
