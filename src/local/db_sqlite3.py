import sqlite3
from typing import List, Optional
from shared_components.db_structs import Anime, Episode,Platform,Channel,MsgAn,MsgEp

class SqliteDB:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 1. A simple animes table.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS animes (
                anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mal_id INTEGER UNIQUE NOT NULL,
                title TEXT UNIQUE NOT NULL,
                title_english TEXT,
                title_japanese TEXT,
                type TEXT,
                episodes TEXT,
                status TEXT,
                airing BOOLEAN,
                aired TEXT,
                rating TEXT,
                duration TEXT,
                season TEXT,
                year INTEGER,
                studios TEXT,
                producers TEXT,
                synopsis TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 2. Table to relate episodes to an anime.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                episode_id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER NOT NULL REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                mal_id INTEGER NOT NULL REFERENCES animes(mal_id) ON DELETE CASCADE ON UPDATE CASCADE,
                episode_number INTEGER NOT NULL,
                watch_link TEXT NOT NULL,
                download_link_hd TEXT NOT NULL,
                download_link_sd TEXT NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                temp INTEGER DEFAULT 0,
                UNIQUE (mal_id, episode_number),
                UNIQUE (anime_id, episode_number),
                UNIQUE (watch_link),
                UNIQUE (download_link_hd),
                UNIQUE (download_link_sd)
            )
        ''')
        # 3. A simple platforms table.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS platforms (
                platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT UNIQUE NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        # 4. Table to relate channels to a platform.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_id INTEGER NOT NULL,
                chat_name TEXT,
                chat_id INTEGER,
                chat_description TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (platform, chat_name),
                UNIQUE (platform, chat_id),
                CHECK (
                    (chat_name IS NULL AND chat_id IS NOT NULL) OR
                    (chat_name IS NOT NULL AND chat_id IS NULL) OR
                    (chat_name IS NOT NULL AND chat_id IS NOT NULL)            
                ),
                FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        # 5. Table to recover messages related to an anime from a channel in a platform.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS msgs_an (
                msg_an_id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (anime_id, channel_id),
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        # 6. Table to recover messages related to an episode from a channel in a platform.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS msgs_ep (
                msg_ep_id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (episode_id, channel_id),
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        # 7. Table to recover messages related to general topics from a channel in a platform.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS msgs_ge (
                msg_ge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                type INTEGER NOT NULL,
                description TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        # 8. A simple users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                general_notification_on INTEGER DEFAULT 0,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 9. Table to relate a user to platforms
        # If not exists (user_id, platform_id),
        # then user is not in platform.
        # stores the user_id_on_platform for forward messages.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_in_platforms (
                uip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform_id INTEGER NOT NULL,
                user_id_on_platform INTEGER NOT NULL,
                platform_notification_on INTEGER DEFAULT 0,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, platform_id),
                UNIQUE (user_id_on_platform, platform_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')
        # 10. Table to relate a user to channels
        # if not exists (user_id, channel_id),
        # then user is not in channel.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_in_channels (
                uic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_name_on_channel TEXT UNIQUE NOT NULL,
                channel_notification_on INTEGER DEFAULT 0,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, channel_id),
                UNIQUE (user_name_on_channel, channel_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')
        # 11. Table to relate a user historic to animes
        # If not exists (user_id, anime_id), historic is empty
        # can have multiples and equals (user_id, anime_id) for historic functionality.
        self.cursor.execute('''                
            CREATE TABLE IF NOT EXISTS user_anime_relationships (
                user_anime_rel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                relationship_state TEXT NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        # 12. Table to relate a user to animes,
        # If not exists (user_id, anime_id), relationship is N/A.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS anime_ratings (
                anime_rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                rating INTEGER, -- A nota atribuída pelo usuário ao anime (pode ser NULL se o usuário ainda não atribuiu uma nota)
                favorite INTEGER DEFAULT 1, -- 0: false, 1: true
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, anime_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                CHECK (anime_rating >= 0 AND anime_rating <= 100 OR anime_rating IS NULL) -- Garante que a nota atribuída esteja dentro do intervalo válido
            );
        ''')
        # 13. Table to notify a anime to a user by channel context.
        # if (user_id, anime_id, channel_id) exists, notification is on
        # else, notification is off.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS anime_notifications (
                anime_notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                channel_id INTEGER,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, anime_id, channel_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE,
            );
        ''')
        # 14. Table to relate a user to episodes
        # if not exists (user_id, episode_id),
        # then user did not watch episode yet.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS watch_list (
                watch_list_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                episode_id INTEGER,
                watched_status INTEGER DEFAULT 1, -- 0: partially watched, 1: fully watched, non referency: not watched
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, episode_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id) ON DELETE CASCADE ON UPDATE CASCADE
            );
        ''')
        # 15. donation table
        # 16. subscription table
        self.conn.commit()

    def get_anime_mal_id_by_title(self, title: str) -> int:
        self.cursor.execute('SELECT mal_id FROM animes WHERE title = ?', (title,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return None
    
    def get_all_anime_titles_and_ids(self) -> list:
        self.cursor.execute('SELECT mal_id, title FROM animes')
        rows = self.cursor.fetchall()
        return [(row[0], row[1]) for row in rows]
    
    def get_anime_id_by_mal_id(self, mal_id: int) -> int:
        try:
            self.cursor.execute('''
                SELECT anime_id
                FROM animes
                WHERE mal_id = ?
            ''', (mal_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving anime_id for mal_id {mal_id}: {e}")
            return None

    def get_episodes_by_mal_id(self, mal_id: int):
        self.cursor.execute('SELECT * FROM episodes WHERE mal_id = ?', (mal_id,))
        rows = self.cursor.fetchall()
        episodes: List[Episode] = []
        for row in rows:
            episode = Episode(
                episode_id=row[0],
                anime_id=row[1],
                mal_id=row[2],
                episode_number=row[3],
                watch_link=row[4],
                download_link_hd=row[5],
                download_link_sd=row[6],
                temp=row[7],
                added_to=row[8]
            )
            episodes.append(episode)
        return episodes
    
    def get_episode_by_mal_id_and_number(self, mal_id: int, episode_number: int):
        self.cursor.execute('SELECT * FROM episodes WHERE mal_id = ? AND episode_number = ?', (mal_id, episode_number))
        row = self.cursor.fetchone()
        if row:
            column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
            episode_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do episódio

            return Episode(
                episode_id=episode_data['episode_id'],
                anime_id=episode_data['anime_id'],
                mal_id=episode_data['mal_id'],
                episode_number=episode_data['episode_number'],
                watch_link=episode_data['watch_link'],
                download_link_hd=episode_data['download_link_hd'],
                download_link_sd=episode_data['download_link_sd'],
                release_date=episode_data['release_date'],
                temp=episode_data['temp'],
                added_to=episode_data['added_to']
            )
        return None
    
    
    
    def get_episode_mal_id(self, episode: Episode) -> Optional[int]:
        """
       Checks if an episode already exists in the database and returns its ID if found.

        Args:
        - episode: Instance of the Episode object to be checked.

        Returns:
        - ID of the episode if found in the database, None otherwise.
        """
        try:
            self.cursor.execute('''
                SELECT episode_id FROM episodes WHERE mal_id = ? AND episode_number = ?
            ''', (episode.mal_id, episode.episode_number))
            row = self.cursor.fetchone()
            if row:
                return row[0]  # Retorna o ID do episódio se encontrado
            else:
                return None  # Retorna None se o episódio não for encontrado
        except sqlite3.Error as e:
            print(f"Error getting episode ID: {e}")
            return None

    def close(self):
        self.cursor.close()
        self.conn.close()
    
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class TableInterface:
    def create_table() -> None:
        raise NotImplementedError("Subclass must implement abstract method")

    def insert_in_table(self, arg) -> int|None:
        raise NotImplementedError("Subclass must implement abstract method")
    
class SqliteManager:
    def __init__(self, path:str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.animes = Animes(self.cursor, self.conn)
        self.episodes = Episodes(self.cursor, self.conn)
        self.platforms = Platforms(self.cursor, self.conn)
        self.channels = Channels(self.cursor, self.conn)
        self.msgs_an = MsgsAn(self.cursor, self.conn)
        self.msgs_ep = MsgsEp(self.cursor, self.conn)
        self.create_tables()

    def create_tables(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, TableInterface):
                attr.create_table()

    def close(self):
        self.cursor.close()
        self.conn.close()

class Animes(TableInterface):
    def __init__(self, cursor:sqlite3.Cursor, conn:sqlite3.Connection):
        self.cursor = cursor
        self.conn = conn
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS animes (
                anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mal_id INTEGER UNIQUE NOT NULL,
                title TEXT UNIQUE NOT NULL,
                title_english TEXT,
                title_japanese TEXT,
                type TEXT,
                episodes TEXT,
                status TEXT,
                airing BOOLEAN,
                aired TEXT,
                rating TEXT,
                duration TEXT,
                season TEXT,
                year INTEGER,
                studios TEXT,
                producers TEXT,
                synopsis TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def insert_in_table(self, anime: Anime):
        try:
            self.cursor.execute('''
                INSERT INTO animes (
                    mal_id, title, title_english, title_japanese, type, episodes, 
                    status, airing, aired, rating, duration, season, year, studios, 
                    producers, synopsis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                anime.mal_id, anime.title, anime.title_english, anime.title_japanese, anime.type, 
                anime.episodes, anime.status, anime.airing, anime.aired, anime.rating, 
                anime.duration, anime.season, anime.year, anime.studios, anime.producers, 
                anime.synopsis
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"An error occurred inserting anime: {anime.title}.\nErrmsg: {e}")
            self.conn.rollback()
            return None

    def get_table_primary_key(self, mal_id:int) -> Optional[int]:
        self.cursor.execute('SELECT anime_id FROM animes WHERE mal_id = ?', (mal_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def get_by_mal_id(self, mal_id: int):
        self.cursor.execute('SELECT * FROM animes WHERE mal_id = ?', (mal_id,))
        row = self.cursor.fetchone()
        if row:
            column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
            anime_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do anime
            return Anime.from_dict(anime_data)
        
        return None
    
    def get_animes_list(self, num_animes=1, return_all=False):
        if return_all:
            self.cursor.execute('SELECT anime_id, mal_id, title, title_english, title_japanese, type,'
                                'episodes, status, airing, aired, rating, duration, season, year, studios, producers, synopsis, creation_date FROM animes')
        else:
            self.cursor.execute('SELECT anime_id, mal_id, title, title_english, title_japanese,'
                                'type, episodes, status, airing, aired, rating, duration, season, year,'
                                'studios, producers, synopsis, channel, creation_date FROM animes ORDER BY mal_id DESC LIMIT ?', (num_animes,))
        rows = self.cursor.fetchall()

        animes: list[Anime] = []
        for row in rows:
            column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
            anime_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do anime

            anime = Anime.from_dict(anime_data)
            animes.append(anime)

        return animes


class Episodes(TableInterface):
    def __init__(self, cursor:sqlite3.Cursor, conn:sqlite3.Connection):
        self.cursor = cursor
        self.conn = conn
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                episode_id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER NOT NULL REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                mal_id INTEGER NOT NULL REFERENCES animes(mal_id) ON DELETE CASCADE ON UPDATE CASCADE,
                episode_number INTEGER NOT NULL,
                watch_link TEXT NOT NULL,
                download_link_hd TEXT NOT NULL,
                download_link_sd TEXT NOT NULL,
                temp INTEGER DEFAULT 0,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (mal_id, episode_number),
                UNIQUE (anime_id, episode_number),
                UNIQUE (watch_link),
                UNIQUE (download_link_hd),
                UNIQUE (download_link_sd)
            )
        ''')

    def insert_in_table(self, episode: Episode):
        try:
            self.cursor.execute('''
                INSERT INTO episodes (
                    anime_id, mal_id, episode_number, watch_link, 
                    download_link_hd, download_link_sd, temp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                episode.anime_id, episode.mal_id, episode.episode_number, episode.watch_link, 
                episode.download_link_hd, episode.download_link_sd, episode.temp
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"An error occurred inserting episode: {episode.episode_number}.\nErrmsg: {e}")
            self.conn.rollback()
            return None

    def get_table_primary_key(self, mal_id:int, episode_number:int) -> Optional[int]:
        self.cursor.execute('SELECT episode_id FROM episodes WHERE mal_id = ? AND episode_number = ?', (mal_id, episode_number))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def get_by_mal_id(self, mal_id: int):
        """
        Get all episodes corresponding to a given MAL ID.

        Args:
            - mal_id: MAL ID of the anime.

        Returns:
            - List of Episode objects.
        """
        self.cursor.execute('''
            SELECT anime_id, episode_id, episode_number, watch_link, download_link_hd,
                download_link_sd, release_date, temp, creation_date
            FROM episodes
            WHERE mal_id = ?
            ORDER BY release_date DESC, episode_number, added_to DESC
        ''', (mal_id,))
        
        rows = self.cursor.fetchall()
        if not rows:
            return None
        
        episodes: List[Episode] = []
        column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
        for row in rows:
            episode_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do episódio
            episode = Episode.from_dict(episode_data)
            episodes.append(episode)

        return episodes
    
    def get_episodes_list(self, num_episodes=1, return_all=False):
        if return_all:
            self.cursor.execute('SELECT episode_id, anime_id, mal_id, episode_number, watch_link, download_link_hd,'
                                'download_link_sd, release_date, temp, added_to FROM episodes ORDER BY release_date DESC, episode_number, added_to DESC')
        else:
            self.cursor.execute('SELECT episode_id, anime_id, mal_id, episode_number, watch_link, download_link_hd,'
                                'download_link_sd, release_date, temp, added_to FROM episodes ORDER BY release_date DESC, episode_number, added_to DESC LIMIT ?', (num_episodes,))
        rows = self.cursor.fetchall()

        episodes: List[Episode] = []
        column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
        for row in rows:
            episode_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do episódio
            episode = Episode.from_dict(episode_data)
            episodes.append(episode)

        return episodes

class Platforms(TableInterface):
    def __init__(self, cursor:sqlite3.Cursor, conn:sqlite3.Connection):
        self.cursor = cursor
        self.conn = conn
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS platforms (
                platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT UNIQUE NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def insert_in_table(self, platform: Platform):
        try:
            self.cursor.execute('''
                INSERT INTO platforms (
                    platform_name
                ) VALUES (?)
            ''', (platform.platform_name,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"An error occurred inserting platform: {platform.platform_name}.\nErrmsg: {e}")
            self.conn.rollback()
            return None

    def get_table_primary_key(self, platform_name:str) -> Optional[int]:
        self.cursor.execute('SELECT platform_id FROM platforms WHERE platform_name = ?', (platform_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def get_by_id(self, platform_id: int):
        """
        Get a platform by its platform_id.

        Args:
            - platform_id: The ID of the platform.

        Returns:
            - The Platform object corresponding to the platform_id, or None if not found.
        """
        self.cursor.execute('SELECT * FROM platforms WHERE platform_id = ?', (platform_id,))
        row = self.cursor.fetchone()
        if row:
            column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
            platform_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados da plataforma
            return Platform.from_dict(platform_data)
        return None
    
class Channels(TableInterface):
    def __init__(self, cursor:sqlite3.Cursor, conn:sqlite3.Connection):
        self.cursor = cursor
        self.conn = conn
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_id INTEGER NOT NULL,
                chat_name TEXT,
                chat_id INTEGER,
                chat_description TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (platform_id, chat_name),
                UNIQUE (platform_id, chat_id),
                CHECK (
                    (chat_name IS NULL AND chat_id IS NOT NULL) OR
                    (chat_name IS NOT NULL AND chat_id IS NULL) OR
                    (chat_name IS NOT NULL AND chat_id IS NOT NULL)            
                ),
                FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, channel: Channel):
        try:
            self.cursor.execute('''
                INSERT INTO channels (
                    platform_id, chat_name, chat_id, chat_description
                ) VALUES (?, ?, ?, ?)
            ''', (
                channel.platform_id, channel.chat_name, channel.chat_id, channel.chat_description
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"An error occurred inserting channel: {channel.chat_name}.\nErrmsg: {e}")
            self.conn.rollback()
            return None

    def get_table_primary_key(self, platform_id:int, chat_name:str=None, chat_id:int=None) -> Optional[int]:
        '''
        You must provide a chat_name or a chat_id.
        '''
        if chat_name:
            self.cursor.execute('SELECT channel_id FROM channels WHERE platform_id = ? AND chat_name = ?', (platform_id, chat_name))
        elif chat_id:
            self.cursor.execute('SELECT channel_id FROM channels WHERE platform_id = ? AND chat_id = ?', (platform_id, chat_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def get_by_id(self, platform_id: int):
        self.cursor.execute('SELECT * FROM platforms WHERE platform_id = ?', (platform_id,))
        row = self.cursor.fetchone()
        if row:
            column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
            platform_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados da plataforma
            return Channel.from_dict(platform_data)
        return None

class MsgsAn(TableInterface):
    def __init__(self, cursor:sqlite3.Cursor, conn:sqlite3.Connection):
        self.cursor = cursor
        self.conn = conn
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS msgs_an (
                msg_an_id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (anime_id, channel_id),
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, msg_an: MsgAn):
        try:
            self.cursor.execute('''
                INSERT INTO msgs_an (
                    anime_id, message_id, channel_id
                ) VALUES (?, ?, ?)
            ''', (
                msg_an.anime_id, msg_an.message_id, msg_an.channel_id
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"An error occurred inserting message for anime ID: {msg_an.anime_id}.\nErrmsg: {e}")
            self.conn.rollback()
            return None

    def get_table_primary_key(self, anime_id:int, channel_id:int) -> Optional[int]:
        self.cursor.execute('SELECT msg_an_id FROM msgs_an WHERE anime_id = ? AND channel_id = ?', (anime_id, channel_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class MsgsEp(TableInterface):
    def __init__(self, cursor:sqlite3.Cursor, conn:sqlite3.Connection):
        self.cursor = cursor
        self.conn = conn
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS msgs_ep (
                msg_ep_id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (episode_id, channel_id),
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, msg_ep: MsgEp):
        try:
            self.cursor.execute('''
                INSERT INTO msgs_ep (
                    episode_id, message_id, channel_id
                ) VALUES (?, ?, ?)
            ''', (
                msg_ep.episode_id, msg_ep.message_id, msg_ep.channel_id
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"An error occurred inserting message for episode ID: {msg_ep.episode_id}.\nErrmsg: {e}")
            self.conn.rollback()
            return None

    def get_table_primary_key(self, episode_id:int, channel_id:int) -> Optional[int]:
        self.cursor.execute('SELECT msg_ep_id FROM msgs_ep WHERE episode_id = ? AND channel_id = ?', (episode_id, channel_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class MsgsGe:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS msgs_ge (
                msg_ge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                type INTEGER NOT NULL,
                description TEXT,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, msg_ge):
        self.cursor.execute('''
            INSERT INTO msgs_ge (
                message_id, channel_id, type, description
            ) VALUES (?, ?, ?, ?)
        ''', (
            msg_ge['message_id'], msg_ge['channel_id'], msg_ge['type'], msg_ge['description']
        ))

    def get_table_primary_key(self, message_id, channel_id):
        self.cursor.execute('SELECT msg_ge_id FROM msgs_ge WHERE message_id = ? AND channel_id = ?', (message_id, channel_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class Users:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                general_notification_on INTEGER DEFAULT 0,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def insert_in_table(self, user):
        self.cursor.execute('''
            INSERT INTO users (
                name, general_notification_on
            ) VALUES (?, ?)
        ''', (
            user['name'], user['general_notification_on']
        ))

    def get_table_primary_key(self, name):
        self.cursor.execute('SELECT user_id FROM users WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

class UserInPlatforms:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_in_platforms (
                uip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform_id INTEGER NOT NULL,
                user_id_on_platform INTEGER NOT NULL,
                platform_notification_on INTEGER DEFAULT 0,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, platform_id),
                UNIQUE (user_id_on_platform, platform_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, user_in_platform):
        self.cursor.execute('''
            INSERT INTO user_in_platforms (
                user_id, platform_id, user_id_on_platform, platform_notification_on
            ) VALUES (?, ?, ?, ?)
        ''', (
            user_in_platform['user_id'], user_in_platform['platform_id'], user_in_platform['user_id_on_platform'], 
            user_in_platform['platform_notification_on']
        ))

    def get_table_primary_key(self, user_id, platform_id):
        self.cursor.execute('SELECT uip_id FROM user_in_platforms WHERE user_id = ? AND platform_id = ?', (user_id, platform_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class UserInChannels:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_in_channels (
                uic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_name_on_channel TEXT NOT NULL,
                channel_notification_on INTEGER DEFAULT 0,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, channel_id),
                UNIQUE (user_name_on_channel, channel_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, user_in_channel):
        self.cursor.execute('''
            INSERT INTO user_in_channels (
                user_id, channel_id, user_name_on_channel, channel_notification_on
            ) VALUES (?, ?, ?, ?)
        ''', (
            user_in_channel['user_id'], user_in_channel['channel_id'], user_in_channel['user_name_on_channel'], 
            user_in_channel['channel_notification_on']
        ))

    def get_table_primary_key(self, user_id, channel_id):
        self.cursor.execute('SELECT uic_id FROM user_in_channels WHERE user_id = ? AND channel_id = ?', (user_id, channel_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class UserAnimeRelationships:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_anime_relationships (
                user_anime_rel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                relationship_state TEXT NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, user_anime_rel):
        self.cursor.execute('''
            INSERT INTO user_anime_relationships (
                user_id, anime_id, relationship_state
            ) VALUES (?, ?, ?)
        ''', (
            user_anime_rel['user_id'], user_anime_rel['anime_id'], user_anime_rel['relationship_state']
        ))

    def get_table_primary_key(self, user_id, anime_id):
        self.cursor.execute('SELECT user_anime_rel_id FROM user_anime_relationships WHERE user_id = ? AND anime_id = ?', (user_id, anime_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class AnimeRatings:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS anime_ratings (
                anime_rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                rating INTEGER,
                favorite INTEGER DEFAULT 1,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, anime_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                CHECK (rating >= 0 AND rating <= 100 OR rating IS NULL)
            )
        ''')

    def insert_in_table(self, anime_rating):
        self.cursor.execute('''
            INSERT INTO anime_ratings (
                user_id, anime_id, rating, favorite
            ) VALUES (?, ?, ?, ?)
        ''', (
            anime_rating['user_id'], anime_rating['anime_id'], anime_rating['rating'], anime_rating['favorite']
        ))

    def get_table_primary_key(self, user_id, anime_id):
        self.cursor.execute('SELECT anime_rating_id FROM anime_ratings WHERE user_id = ? AND anime_id = ?', (user_id, anime_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class AnimeNotifications:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS anime_notifications (
                anime_notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_id INTEGER NOT NULL,
                channel_id INTEGER,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, anime_id, channel_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, anime_notification):
        self.cursor.execute('''
            INSERT INTO anime_notifications (
                user_id, anime_id, channel_id
            ) VALUES (?, ?, ?)
        ''', (
            anime_notification['user_id'], anime_notification['anime_id'], anime_notification['channel_id']
        ))

    def get_table_primary_key(self, user_id, anime_id, channel_id):
        self.cursor.execute('SELECT anime_notification_id FROM anime_notifications WHERE user_id = ? AND anime_id = ? AND channel_id = ?', (user_id, anime_id, channel_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


class WatchList:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS watch_list (
                watch_list_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                episode_id INTEGER,
                watched_status INTEGER DEFAULT 1,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, episode_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')

    def insert_in_table(self, watch_list):
        self.cursor.execute('''
            INSERT INTO watch_list (
                user_id, episode_id, watched_status
            ) VALUES (?, ?, ?)
        ''', (
            watch_list['user_id'], watch_list['episode_id'], watch_list['watched_status']
        ))

    def get_table_primary_key(self, user_id, episode_id):
        self.cursor.execute('SELECT watch_list_id FROM watch_list WHERE user_id = ? AND episode_id = ?', (user_id, episode_id))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
