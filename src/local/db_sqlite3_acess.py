from local.db_sqlite3 import SqliteManager
from shared_components import data_colect
from shared_components.db_structs import Anime, Episode, Platform, Channel, MsgAn, MsgEp
from shared_components import values

def _insert_animes_into_database(watch_links: list[list[dict]], download_links: list[list[dict]], animes_metadata: list[dict], database_path, print_log=False):
    db = SqliteManager(database_path)
    animes: list[Anime] = []
    episodes: list[Episode] = []

    if print_log:
        print('\n>>>>>> Add Anime <<<<<<\n')

    # Inserir animes
    for anime_data in animes_metadata:
        # Criar instância do objeto Anime
        anime = Anime.from_dict(anime_data)
        # Verifica se já existe
        anime_id = db.animes.get_table_primary_key(anime.mal_id)
        if anime_id is None or anime_id == -1:
            anime_id = db.animes.insert_in_table(anime)
            anime.anime_id=anime_id
            animes.append(anime)
            if anime_id is not None or anime_id != -1:
                if print_log:
                    print(f'Anime added: {anime}')
        else:
            print(f"Anime {anime.title} already exists in database")
    
    combined_episodes = []
    for watch_list, download_list in zip(watch_links, download_links):
        for watch_episode, download_episode in zip(watch_list, download_list):
            # Certifique-se de que os episódios têm o mesmo número
            assert watch_episode['ep'] == download_episode['episode'], "Números de episódio diferentes"
            
            # Combine os dados do episódio de assistir e fazer download
            combined_episode = {
                'mal_id': watch_episode['mal_id'],
                'episode_number': watch_episode['ep'],
                'watch_link': watch_episode['watch_link'],
                'download_link_hd': download_episode['hd'],
                'download_link_sd': download_episode['sd'],
                'temp': download_episode['temp']
            }
            combined_episodes.append(combined_episode)
            
    # Agora, combined_links contém todos os episódios combinados em uma estrutura de dicionário de listas
    if print_log:
        print('\n>>>>>> Add Episode <<<<<<\n')

    for episode_data in combined_episodes:
        # Obter anime_id com base no mal_id do episódio
        anime_id = db.animes.get_table_primary_key(episode_data['mal_id'])
        # Incluir anime_id nos dados do episódio
        episode_data['anime_id'] = anime_id
        # Criar o objeto Episode a partir dos dados do episódio
        episode = Episode.from_dict(episode_data)
        # Verificar se o episodio existe no banco de dados
        episode_id = db.episodes.get_table_primary_key(episode.mal_id, episode.episode_number)
        if episode_id is None or episode_id == -1:
            # Se o episódio não existe, inseri-lo e adicionar à lista de episódios
            episode_id = db.episodes.insert_in_table(episode)
            episode.episode_id = episode_id
            episodes.append(episode)
            if episode_id is not None or episode_id != -1:
                if print_log:
                    print(f'Episode added: {episode}')
        else:
            # Se o episódio já existe, imprimir mensagem de aviso
            print(f'Episode already exists: id - {episode_id}, mal_id - {episode.mal_id}, ep - {episode.episode_number}')
    db.close()
    return animes, episodes

def extract_releasing_animes_from_af_and_insert_into_database(extract_amount = 1, start_page = 1, database_path = values.DATABASE_PATH, print_log=False):
    '''
    Exxtract dara from Anime Fire and MyAnimeList and inserts in a sqlite3 database

    Args:
     - extract_amount: Amount of url to be extracted from Anime Fire, each url correspond to 1 anime.
     - start_page: Release page number in Anime Fire to start the extract. Exemple page: https://animefire.plus/em-lancamento/1.
     - database_path: Full path for the sqlite3 database file, editable in shared_components/values.py.
     - print_log: Boolean indicating whether to print log messages.

    Rreturns:
     - None.
    '''
    watch_links, download_links, animes_metadata = data_colect.extract_releasing_animes_from_af(extract_amount=extract_amount, start_page=start_page, print_log=print_log)
    # Conectar ao banco de dados SQLite
    animes, episodes = _insert_animes_into_database(watch_links=watch_links, download_links=download_links, animes_metadata=animes_metadata, database_path=database_path, print_log=print_log)
    return animes, episodes
    

def insert_custom_anime_from_af_into_database(url_af: str, database_path=values.DATABASE_PATH,print_log=False):
    '''
    Insert a single anime from anime fire into the database.

    Args:
     - anime_url_on_af: URL to the anime overview page on Anime Fire following the format: 
                        https://animefire.plus/animes/anime-name-todos-os-episodios.
     - database_path: Full path for the sqlite3 database file, editable in shared_components/values.py.
     - print_log: Boolean indicating whether to print log messages.

    Returns:
     - A anime and this anime episodes.
    '''
    watch_links, download_links, anime_data = data_colect.extract_custom_anime_from_af(anime_url_on_af=url_af, print_log=print_log)
    animes, episodes = _insert_animes_into_database(
        watch_links=[watch_links],
        download_links=[download_links],
        animes_metadata=[anime_data],
        database_path=database_path,
        print_log=print_log
    )
    return animes, episodes

def get_anime_from_database(mal_id: int, database_path=values.DATABASE_PATH):
    '''
    Get anime and coorespondents episodes data from the database.

    Args:
      - mal_id: anime id from MyAnimeList.
      - database_path: path for the database.

     Return:
      - Anime data and a list o Episodes data.
    '''
    db = SqliteManager(database_path)
    anime: Anime = db.animes.get_by_mal_id(mal_id=mal_id)
    episodes: list[Episode] = db.episodes.get_by_mal_id(mal_id=mal_id)
    db.close()
    return anime, episodes

def save_msg_an(anime: Anime, message_id: int, platform_name: str, chat_id: int, chat_name: str, database_path:str=values.DATABASE_PATH):
    '''
    Save a anime message into the database for future references (browser animes)

    Args:
     - anime: The anime that was sent in the message.
     - message_id: The returned id of the message when the anime is successfully sent.
     - chat_id: id of the chat where the message was sent.
     - database_path: database in where the message will be sabe.

    Returns:
     - msg_an: The message saved into the database is returned with the updated value for the msg_an_id attribute.
     - None: If message is not saved into the database due any erros, return None.
    '''
    db = SqliteManager(database_path)
    try:
        platform_id = db.platforms.get_table_primary_key(platform_name)
        if platform_id not in (None, -1):
            channel_id = db.channels.get_table_primary_key(platform_id=platform_id, chat_id=chat_id, chat_name=chat_name)
            if channel_id not in (None, -1):
                msg_an = MsgAn(anime.anime_id, message_id, channel_id)
                msg_an.msg_an_id = db.msgs_an.insert_in_table(msg_an)
                return msg_an
    finally:
        db.close()

def save_msg_ep(episode: Episode, message_id: int, platform_name: str, chat_id: int, chat_name: str, database_path: str = values.DATABASE_PATH):
    '''
    Save an episode message into the database for future references.

    Args:
     - episode: The episode that was sent in the message.
     - message_id: The returned id of the message when the episode is successfully sent.
     - platform_name: Name of the platform where the message was sent.
     - chat_id: ID of the chat where the message was sent.
     - chat_name: Name of the chat where the message was sent.
     - database_path: Path to the database where the message will be saved.

    Returns:
     - MsgEp: The message saved into the database is returned with the updated value for the msg_ep_id attribute.
     - None: If the message is not saved into the database due to any errors, return None.
    '''
    db = SqliteManager(database_path)
    try:
        platform_id = db.platforms.get_table_primary_key(platform_name)
        if platform_id not in (None, -1):
            channel_id = db.channels.get_table_primary_key(platform_id=platform_id, chat_id=chat_id, chat_name=chat_name)
            if channel_id not in (None, -1):
                msg_ep = MsgEp(episode.episode_id, message_id, channel_id)
                msg_ep.msg_ep_id = db.msgs_ep.insert_in_table(msg_ep)
                return msg_ep
    finally:
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
     - None.
    '''
    db = SqliteManager(database_path)
    print("\n>>>>>> ANIMES <<<<<<\n")
    anime_list = db.animes.get_animes_list(num_animes=num_animes, return_all=return_all)
    i = 1
    for anime in anime_list:
        print(f"entry: {i}")
        print(anime)
        print()
        i += 1
    i = 1
    print("\n>>>>>> EPISODES <<<<<<\n")
    episode_list = db.episodes.get_episodes_list(num_episodes=num_episodes, return_all=return_all)
    for episode in episode_list:
        print(f"entry: {i}")
        print(episode)
        print()
        i += 1

def init_animestele(
        path = values.DATABASE_PATH, platform_name = values.TELEGRAM_NAME,
        channel_name = values.ANIMESTELE_NAME, channel_id = values.ANIMESTELE_ID,
        channel_description = values.ANIMESTELE_DESCRIPTION
    ):
    db = SqliteManager(path)
    # See if platform exists
    platform_id = db.platforms.get_table_primary_key(platform_name)
    if platform_id is None:
        platform = Platform(platform_name)
        platform.platform_id = db.platforms.insert_in_table(platform)
        channel = Channel(platform.platform_id, chat_name=channel_name, chat_id=channel_id, chat_description=channel_description)
        channel.channel_id = db.channels.insert_in_table(channel)
        db.close()
        return platform, channel
    # See if episode exits
    else:
        channel_id = db.channels.get_table_primary_key(platform_id, channel_id)
        if channel_id is None:
            platform = db.platforms.get_by_id(platform_id)
            channel = Channel(platform_id, chat_name=channel_name, chat_id=channel_id, chat_description=channel_description)
            channel.channel_id = db.channels.insert_in_table(channel)
            db.close()
            return platform, channel
        # Both exists
        else:
            platform = db.platforms.get_by_id(platform_id)
            channel = db.channels.get_by_id(channel_id)
            db.close()
            return platform, channel
            
            

