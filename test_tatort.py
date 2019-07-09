from tatort import splitTatorte, openPage

def test_splitTatorte():
    titel, kommissar, stadt, datum = splitTatorte("Rattennest\n(Kasulke (Berlin))\n\n08.10.1972")
    assert titel == "Rattennest"
    assert kommissar == "Kasulke"
    assert stadt == "Berlin"
    assert datum == "08.10.1972"


def test_openPage():
    r, statuscode = openPage("https://www.google.at")
    assert statuscode == 200
