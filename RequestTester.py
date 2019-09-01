import requests
from bs4 import BeautifulSoup, Tag
from googletrans import Translator
import re

def clean(stringToClean):
    stringToClean = ' '.join(stringToClean.split())
    return re.sub(r'[^\x00-\x7f]', r' ', stringToClean)

def main():
    req = requests.get("https://www.cbs.dk/uddannelse/bachelor/hajur-erhvervsoekonomi-erhvervsjura")
    req.encoding = "utf-8"
    soup = BeautifulSoup(req.content, 'lxml')

    translator = Translator()
    desc = soup.find('section', {'class': 'panel-pane pane-node'}).get_text()


    desc = ' '.join(desc.split())

    desc = translator.translate("omkostningstunge").text
    print(desc)


if __name__ == '__main__':
    main()

