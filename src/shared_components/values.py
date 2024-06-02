'''
Const values used in all the AnimesTele project
'''

# Data colect
URL_AF_RELEASES = "https://animefire.plus/em-lancamento/1"
URL_AF_DOWNLOADS = "https://animefire.plus/download/"
URL_AF_FILTER_RELEAES = 'https://animefire.plus/animes/'
URL_JIKAN_SEARCH = "https://api.jikan.moe/v4/anime?q="
URL_JIKAN_SEARCH_BY_MALID = "https://api.jikan.moe/v4/anime/"
URLS_AF_FILTER_DOWNLOADS_LINKS = ["https://s2.lightspeedst.net/s2/mp4/", "https://s2.lightspeedst.net/s2/mp4_temp/"]
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Database
BAD_ID = -1
DATABASE_PATH = "data/animestele.db"

# Telegram
TELEGRAM_NAME = 'telegram'
TELEGRAM_URL = 't.me/'
ANIMESTELE_ID = -1002039517569
ANIMESTELE_NAME = "animestele"
ANIMESTELE_DESCRIPTION = (
    "AnimesTele é a sua plataforma de animes no Telegram! "
    "Somente animes legendados em pt-br. "
    "Use nosso bot para pesquisar: "
    "- AnimesTeleOficialBot: @animestele_oficial_bot"
)
