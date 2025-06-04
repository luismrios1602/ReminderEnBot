from strings.languages.Spanish import Spanish
from strings.languages.English import English
from strings.languages.Brazilian import Brazilian

langs = {
    "ES": Spanish(),
    "EN": English(),
    "BR": Brazilian(),
    "FR": Spanish(),
    "IT": Spanish()
}

class Strings:
    def __init__(self, lang="ES"):
        self.lang = langs[lang]

    def getText(self, text, **kwargs):
        return self.lang[text].format(**kwargs)
