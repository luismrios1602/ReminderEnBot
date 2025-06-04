from strings import emojis

class English:
    def __init__(self):
        self.test = f"{emojis.flags['EN']} testing"
        self.dias = "days"
        self.bienvenida = '''Welcome, {username}👋! I'm RemindEn, your word reminder ✌
Send /help to know how I work.'''
        self.ayuda = ('🤖 _What can I do?:_\n\n'
         "🔍 *Search:* Send me a word\\. If the word is registered, I will show it\\.\n\n"
         "➕ *Add:* If the word doesn't exist, you'll have the option to register it\\.\n"
         '   Explanation, Examples, Translations, and Reminder Frequency\n\n'
         '*🔊 Pronunciation:* When you send a word, you can listen to its pronunciation before registering it\\.\n\n'
         "*📅 Reminder:* Each word you register will be randomly reminded on one day within the next 7 days\\. The 7\\-day countdown resets every time the word is reminded\\.\n"
         'The day and time will be randomly selected between 8:00 UTC\\-5 and 22:00 UTC\\-5 \\.\n\n'
         '*🧠 Forget:* If you want to stop reminding a word, you can select the "Forget" option and choose the period for which you want to forget it\\.\n'
         "1 month, 3 months, 6 months, 1 year, or don't remind it anymore\\.\n\n"
         '*🗑 Delete:* Search for the word to delete and press "Delete"\\.\n\n'
         '*🖊 Edit:* Search for the word to edit and press "Edit"\\. Then, select what information you want to edit and follow the instructions\\.\n\n'
         "*🧹 Clear:* If you clear this chat, the registered words won't be deleted, and you'll continue receiving reminders\\.\n\n"
         '*🛑 Stop reminders:* Use the "Stop Bot" option to stop receiving automatic messages\\.\n\n')

    def __getitem__(self, key):
        return getattr(self, key, f'no text')
