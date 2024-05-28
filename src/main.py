import argparse
import asyncio
from local import db_sqlite3_acess
from shared_components.api.bot_api.sensitive import token
from shared_components.api.bot_api.animestele_bot import Telena

async def main(mode):
    if mode == 'local_windows_run':
        local_windows_run()
    elif mode == 'local_windows_debug':
        local_windows_debug()
    elif mode == 'server_run':
        server_run()
    elif mode == 'server_debug':
        await server_debug()
    elif mode == 'local_linux_run':
        local_linux_run()
    elif mode == 'local_linux_debug':
        local_linux_debug()
    else:
        print(f"Unknown mode: {mode}")

def local_windows_run():
    print("Running in local Windows mode...")
    db_sqlite3_acess.extract_releasing_animes_from_af_and_insert_into_database()

def local_windows_debug():
    print("Debugging in local Windows mode...")
    db_sqlite3_acess.extract_releasing_animes_from_af_and_insert_into_database(print_log=True)
    
def server_run():
    print("Running in server mode...")
    animes, episdoes = db_sqlite3_acess.insert_custom_anime_from_af_into_database(
        url_af="https://animefire.plus/animes/tensei-shitara-dainana-ouji-datta-node-kimama-ni-majutsu-wo-kiwamemasu-todos-os-episodios",
        print_log=True
    )
    telena = Telena
    for anime in animes:
        telena.add_anime_to_telegram(chat_id="https://t.me/+RRKCuQTFBmcyZWIx",mal_id=anime.mal_id)
                                 
async def server_debug():
    print("Debugging in server mode...")
    telena = Telena(token=token.TOKEN)  # Substitua "your_token_here" pelo token real
    await telena.add_anime_to_telegram(chat_id="https://t.me/+RRKCuQTFBmcyZWIx", mal_id=53516)


def local_linux_run():
    print("Running in local Linux mode...")

def local_linux_debug():
    print("Debugging in local Linux mode...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the program in different modes.')
    parser.add_argument('mode', choices=[
        'local_windows_run', 'local_windows_debug','server_run', 'server_debug',
        'local_linux_run', 'local_linux_debug'
    ], help='Mode to run the program in.')

    args = parser.parse_args()
    asyncio.run(main(args.mode))