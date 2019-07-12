import requests
from bs4 import BeautifulSoup
from loguru import logger
import sys
import json
import os
import configparser
from fuzzywuzzy import fuzz

def settings():
    conf = {}
    config = configparser.ConfigParser()
    if not os.path.isfile("tatort.ini"):
        config['TATORT'] = {'Verzeichnis': '',
                            'Jahr': 'no',
                            'Stadt': 'yes',
                            'Team': 'no',
                            'filename': '#team# - #titel# - #datum#',
                            'umbenennen': 'yes'
                            }
        with open('tatort.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config.read("tatort.ini")
        conf['verzeichnis'] = config['TATORT']['verzeichnis']
        conf['jahr'] = config.getboolean('TATORT', 'jahr')
        conf['stadt'] = config.getboolean('TATORT', 'stadt')
        conf['team'] = config.getboolean('TATORT', 'team')
        conf['maske'] = config['TATORT']['filename']
        conf['rename'] = config.getboolean('TATORT', 'umbenennen')
        if not os.path.isfile("tatort.json"):
            conf['liste'] = False
        else:
            conf['liste'] = True
    return conf


def getFiles(dir):
    (_, _, filenames) = next(os.walk(dir))
    return filenames


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


def readFile():
    with open('tatort.json') as f:
        return json.load(f)


if __name__ == "__main__":
    logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
    config = settings()
    logger.info("Settings: {}", config)
    # TODO: Files umbenennen
    # TODO: Files umsortieren
    if not config['liste']:
        Tatorte = getTatorte()
        writeFile('Tatort.json', Tatorte)
        logger.info("Tatorte von Webseite gelesen und in lokales JSON geschrieben.")
    else:
        Tatorte = readFile()
        logger.info("Tatorte von lokalem JSON gelesen.")
    if config['rename']:
        logger.info("Umbenennen ist aktiv, Verzeichnis wird eingelesen.")
        files = getFiles(config['verzeichnis'])
        print(repr(Tatorte))
        for tatort in Tatorte.keys():
            for file in files:
                ratio = fuzz.partial_ratio(Tatorte[tatort][0], file)
                if ratio > 50:
                    logger.info("{}:{}:{}", Tatorte[tatort][0], file, str(ratio))
