class WordClass: 
    def __init__(self, id=0, word="", lang_word="", meaning="", lang_meaning="", description="", examples="", chatId=0, daysSchedule=7, scheduled=""):
        self.id = id
        self.word = word
        self.lang_word = lang_word
        self.lang_meaning = lang_meaning
        self.meaning = meaning
        self.description = description
        self.examples = examples
        self.chatId = chatId
        self.daysSchedule = daysSchedule
        self.scheduled = scheduled

    def __str__(self):
        return f"WordClass(id={self.id}, word='{self.word}', lang_word='{self.lang_word}', " \
               f"'meaning='{self.meaning}', lang_meaning='{self.lang_meaning}', " \
               f"description='{self.description}', examples='{self.examples}', chatId={self.chatId}, " \
                f"daysSchedule={self.daysSchedule}, " \
               f"scheduled={self.scheduled})"