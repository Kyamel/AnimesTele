'''
Const values used in all the AnimesTele project
'''

# Data colect
URL_AF_RELEASES:str = "https://animefire.plus/em-lancamento/1"
URL_AF_DOWNLOADS:str = "https://animefire.plus/download/"
URL_AF_FILTER_RELEAES:str = 'https://animefire.plus/animes/'
URL_JIKAN_SEARCH:str = "https://api.jikan.moe/v4/anime?q="
URL_JIKAN_SEARCH_BY_MALID:str = "https://api.jikan.moe/v4/anime/"
URLS_AF_FILTER_DOWNLOADS_LINKS:list[str] = ["https://s2.lightspeedst.net/s2/mp4/", "https://s2.lightspeedst.net/s2/mp4_temp/"]
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Database
BAD_ID:int = -1
DATABASE_PATH:str = "data/animestele.db"

# Telegram
TELEGRAM_NAME:str = 'telegram'
TELEGRAM_URL:str = 't.me/'
ANIMESTELE_ID:int = -1002039517569
ANIMESTELE_NAME:str = "animestele"
ANIMESTELE_DESCRIPTION:str = (
    "AnimesTele é a sua plataforma de animes no Telegram! "
    "Somente animes legendados em pt-br. "
    "Use nosso bot para pesquisar: "
    "- AnimesTeleOficialBot: @animestele_oficial_bot"
)
