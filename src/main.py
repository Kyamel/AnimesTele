import argparse
import asyncio
from local import db_sqlite3_acess
from shared_components.api.bot_api.sensitive import token
from shared_components.api.bot_api.animestele_bot import Telena
import urllib.parse

async def main(mode):
    if mode == 'local_windows_run':
        await local_windows_run()
    elif mode == 'local_windows_debug':
        await local_windows_debug()
    elif mode == 'server_run':
        await server_run()
    elif mode == 'server_debug':
        await server_debug()
    elif mode == 'local_linux_run':
        await local_linux_run()
    elif mode == 'local_linux_debug':
        await local_linux_debug()
    else:
        print(f"Unknown mode: {mode}")

async def local_windows_run():
    print("Running in local Windows mode...")
    #db_sqlite3_acess.extract_releasing_animes_from_af_and_insert_into_database()
    telena = Telena(token=token.TOKEN_TELENA)
    url = "https://lightspeedst.net/s5/mp4/boku-to-roboko/sd/1.mp4?type=video/mp4&title=[AnimeFire.plus]%20Boku%20to%20Roboko%20-%20Epis%C3%B3dio%201%20(SD)"
    encoded_url = urllib.parse.quote(url, safe=':/?&=')
    responde = await telena.upload_video(
        chat_id="@AnimesTele",
        http_url=encoded_url,
        print_log=True
    )
    print(responde)

async def local_windows_debug():
    print("Debugging in local Windows mode...")
    animes, episdoes = db_sqlite3_acess.extract_releasing_animes_from_af_and_insert_into_database(start_page=3, extract_amount=2, print_log=True)
    telena = Telena(token=token.TOKEN_TELENA)  
    for anime in animes:
        await telena.add_anime_to_telegram(chat_id="@AnimesTele",mal_id=anime.mal_id, print_log=True)

    
async def server_run():
    print("Running in server mode...")
    animes, episdoes = db_sqlite3_acess.insert_custom_anime_from_af_into_database(
        url_af="https://animefire.plus/animes/tensei-shitara-dainana-ouji-datta-node-kimama-ni-majutsu-wo-kiwamemasu-todos-os-episodios",
        print_log=True
    )
    telena = Telena(token=token.TOKEN_TELENA)  
    for anime in animes:
        await telena.add_anime_to_telegram(chat_id="@AnimesTele",mal_id=anime.mal_id, print_log=True)
                                 
async def server_debug():
    print("Debugging in server mode...")
    telena = Telena(token=token.TOKEN_TELENA)  # Substitua "your_token_here" pelo token real
    await telena.add_anime_to_telegram(chat_id="@AnimesTele", mal_id=53516, print_log=True)


async def local_linux_run():
    print("Running in local Linux mode...")

async def local_linux_debug():
    print("Debugging in local Linux mode...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the program in different modes.')
    parser.add_argument('mode', choices=[
        'local_windows_run', 'local_windows_debug','server_run', 'server_debug',
        'local_linux_run', 'local_linux_debug'
    ], help='Mode to run the program in.')

    args = parser.parse_args()
    asyncio.run(main(args.mode))