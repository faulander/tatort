import os
from tatort import splitTatorte, openPage, getFiles


def test_splitTatorte():
    titel, kommissar, stadt, datum = splitTatorte("Rattennest\n(Kasulke (Berlin))\n\n08.10.1972")
    assert titel == "Rattennest"
    assert kommissar == "Kasulke"
    assert stadt == "Berlin"
    assert datum == "08.10.1972"


def test_splitTatorteOhneKommissar():
    titel, kommissar, stadt, datum = splitTatorte("Sonntagsmörder\n\n13.11.2016")


def test_openPage():
    r, statuscode = openPage("https://www.google.at")
    assert statuscode == 200


def test_getFiles():
    print(os.name)
    dir = ''
    erg = getFiles(dir)
    assert erg False

