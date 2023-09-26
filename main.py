from bs4 import BeautifulSoup
import request3


# Fetches relationnal data from jeuxdemots for
# a given word. Might fail
def fetch_word_data(word: str) -> str | None:

    try:
        r = request3.get(
            f"https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel={word}"
        )
        print(r.status_code)

        soup = BeautifulSoup(r.text, features="html.parser")

        return '\n'.join(
            filter(lambda x: x.startswith(('r', 'e', 'n')),
                   str(soup.find("code")).split('\n')))

    except request3.exceptions.RequestException as e:
        print("Couldn't reach url with reason: ", e)

        return None
