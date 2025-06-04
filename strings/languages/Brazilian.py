from strings import emojis

class Brazilian:
    def __init__(self):
        self.test = f"{emojis.flags['BR']} testando"
        self.dias = "dias"
        self.bienvenida = '''Bem-vindo, {username}👋! Eu sou RemindEn, o seu recordatório de palavras ✌
Envia /help para saber como eu trabalho.'''

    def __getitem__(self, key):
        return getattr(self, key, f'sem texto')