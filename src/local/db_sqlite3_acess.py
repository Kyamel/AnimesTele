from local.db_sqlite3 import Database
from shared_components import data_colect
from shared_components.db_structs import Anime, Episode
from shared_components import values


def data_collect_and_insert_in_database(extract_amount = 1, start_page = 1, database_path = values.DATABASE_PATH, print_log=False):
    '''
    Exxtract dara from Anime Fire and MyAnimeList and inserts in a sqlite3 database

    Args:
     - extract_amount: Amount of url to be extracted from Anime Fire, each url correspond to 1 anime.
     - start_page: Release page number in Anime Fire to start the extract. Exemple page: https://animefire.plus/em-lancamento/1.
     - database_path: Full path for the sqlite3 database file, editable in shared_components/values.py.
     - print_log: Boolean indicating whether to print log messages.

    Rreturns:
     - void return.
    '''
    watch_links, download_links, animes_metadata = data_colect.data_extract(extract_amount=extract_amount, start_page=start_page, print_log=print_log)
    # Conectar ao banco de dados SQLite
    db = Database(database_path)
    # Inserir animes
    for anime_data in animes_metadata:
        # Criar instância do objeto Anime
        anime = Anime(
            mal_id=anime_data['mal_id'],
            title=anime_data['title'],
            title_english=anime_data['title_english'],
            title_japanese=anime_data['title_japanese'],
            type=anime_data['type'],
            episodes=anime_data['episodes'],
            status=anime_data['status'],
            airing=anime_data['airing'],
            aired=anime_data['aired'],
            rating=anime_data['rating'],
            duration=anime_data['duration'],
            season=anime_data['season'],
            year=anime_data['year'],
            studios=anime_data['studios'],
            producers=anime_data['producers'],
            synopsis=anime_data['synopsis']
        )
        db.insert_anime(anime)
    
    combined_links = {}
    # Itera sobre cada lista de links de assistir e fazer download
    for watch_list, download_list in zip(watch_links, download_links):
        # Itera sobre os episódios de cada lista
        for watch_episode, download_episode in zip(watch_list, download_list):
            # Certifica-se de que os episódios têm o mesmo número
            assert watch_episode['ep'] == download_episode['episode'], "Números de episódio diferentes"

            episode_number = watch_episode['ep']
            combined_links.setdefault(episode_number, [])
            combined_links[episode_number].append({
                'mal_id': watch_episode['mal_id'],
                'episode_number': episode_number,
                'watch_link': watch_episode['watch_link'],
                'download_link_hd': download_episode['hd'],
                'download_link_sd': download_episode['sd'],
                'temp': download_episode['temp']
            })

    # Ordena os episódios com base no número do episódio
    ordered_episodes = sorted(combined_links.items())

    # Agora, combined_links contém todos os episódios combinados em uma estrutura de dicionário de listas
    # Você pode iterar sobre combined_links e inserir todos os episódios no banco de dados de uma vez
    if print_log:
        print('\n>>>>>> Add Episode <<<<<<\n')

    for episode_number, episode_data_list in ordered_episodes:
        for episode_data in episode_data_list:
            episode = Episode(**episode_data)
            episode_id = db.get_episode_id(episode)
            if episode_id is None:
                if print_log:
                    print(f'Episode added: {episode}')
                db.insert_episode(episode)
            else:
                print(f'Episode already exits: id - {episode_id}, mal_id - {episode.mal_id}, ep - {episode.episode_number}')
    db.close()

def data_print(database_path=values.DATABASE_PATH, num_animes=10, num_episodes=10, return_all=False):
    '''
    Print database.

    Args:
     - database_path: Full path for the sqlite3 database file, editable in shared_components/values.py.
     - num_animes: Num of most recent animes to be printed.
     - num_episodes: Num of most recent episodes to be printed.
     - return_all: Print all animes and all episodes in the database (heavy workload).

    Return:
     - void returm.
    '''
    db = Database(database_path)
    print("\n>>>>>> ANIMES <<<<<<\n")
    anime_list = db.get_animes_list(num_animes=num_animes, return_all=return_all)
    i = 1
    for anime in anime_list:
        print(f"entry: {i}")
        print(anime)
        print()
        i += 1
    i = 1
    print("\n>>>>>> EPISODES <<<<<<\n")
    episode_list = db.get_episodes_list(num_episodes=num_episodes, return_all=return_all)
    for episode in episode_list:
        print(f"entry: {i}")
        print(episode)
        print()
        i += 1
