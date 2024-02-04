class WordClass: 
    def __init__(self, id=0, word="", meaning="", description="", examples="", chatId=0, scheduled=""):
        self.id = id
        self.word = word
        self.meaning = meaning
        self.description = description
        self.examples = examples
        self.chatId = chatId
        self.scheduled = scheduled

    def __str__(self):
        return f"WordClass(id={self.id}, word='{self.word}', meaning='{self.meaning}', " \
               f"description='{self.description}', examples='{self.examples}', chatId={self.chatId}, " \
               f"scheduled={self.scheduled})"