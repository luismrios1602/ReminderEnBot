class UserClass:
    def __init__(self, id=0, chatId=0, name="", lang="ES"):
        self.id = id
        self.chatId = chatId
        self.name = name
        self.lang = lang

    def __str__(self):
        return f"{self.chatId}"