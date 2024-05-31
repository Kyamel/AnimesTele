import sqlite3
from typing import List, Optional
from shared_components.db_structs import Anime, Episode

class SqliteDB:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 1. A simple animes table
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
        # 2. Table to relate episodes to an anime
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
        # 3. Table to store platforms
        self.cursor.execute('''
            -- Table to store platforms
            CREATE TABLE IF NOT EXISTS platforms (
                platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT UNIQUE NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        # 4. Table to relate channels to a platform
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
        # 5. Table to recover messages related to an anime from a channel in a platform
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
        # 6. Table to recover messages related to an episode from a channel in a platform
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
        # 7. Table to recover messages related to general topics from a channel in a platform
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
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 9. Table to relate a user to platforms
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_in_platforms (
                uip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform_id INTEGER NOT NULL,
                user_id_on_platform INTEGER NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP.
                UNIQUE (user_id, platform_id),
                UNIQUE (user_id_on_platform, platform_id),
                UNIQUE (user_id_on_platform),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')
        # 10. Table to relate a user to channels
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_in_channels (
                uic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                user_name_on_channel TEXT UNIQUE NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, channel_id),
                UNIQUE (user_name_on_channel, channel_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')
        # 11. Table to relate a user to animes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                anime_id INTEGER,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, anime_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (anime_id) REFERENCES animes(anime_id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        ''')
        self.conn.commit()


    def insert_anime(self, anime: Anime, print_log=False):
        """
        Insert a class Anime into the database, all attributes except anime_id are added to the database.
        """
        if anime.mal_id == -1 or anime.mal_id == None:
            try:
                self.cursor.execute('''
                    INSERT INTO animes (
                        mal_id, title, title_english, title_japanese, type, episodes, status, airing, aired, rating, 
                        duration, season, year, studios, producers, synopsis, channel, added_to
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    anime.mal_id, anime.title, anime.title_english, anime.title_japanese, anime.type, 
                    anime.episodes, anime.status, anime.airing, anime.aired, anime.rating, 
                    anime.duration, anime.season, anime.year, anime.studios, anime.producers, 
                    anime.synopsis, anime.channel, anime.added_to
                ))
                self.conn.commit()
                anime.anime_id = self.cursor.lastrowid
                return anime.anime_id
            except sqlite3.IntegrityError as e:
                print(f"Error inserting anime {anime.title} - {anime.mal_id}: {e}")
                return None
        else:
            if print_log:
                print(f"Invalid anime: mal_id={anime.mal_id}")

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
    
    def get_anime_by_mal_id(self, mal_id: int):
        self.cursor.execute('SELECT * FROM animes WHERE mal_id = ?', (mal_id,))
        row = self.cursor.fetchone()
        if row:
            column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
            anime_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do anime

            return Anime(
                anime_id=anime_data['anime_id'],
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
                synopsis=anime_data['synopsis'],
                channel=anime_data['channel'],
                added_to=anime_data['added_to']
            )
        raise ValueError("Anime not found")
    
    def get_animes_list(self, num_animes=1, return_all=False):
        if return_all:
            self.cursor.execute('SELECT anime_id, mal_id, title, title_english, title_japanese, type,'
                                'episodes, status, airing, aired, rating, duration, season, year, studios, producers, synopsis, added_to FROM animes')
        else:
            self.cursor.execute('SELECT anime_id, mal_id, title, title_english, title_japanese,'
                                'type, episodes, status, airing, aired, rating, duration, season, year,'
                                'studios, producers, synopsis, channel,added_to FROM animes ORDER BY mal_id DESC LIMIT ?', (num_animes,))
        rows = self.cursor.fetchall()

        animes: list[Anime] = []
        for row in rows:
            column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
            anime_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do anime

            anime = Anime(
                anime_id=anime_data['anime_id'],
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
                synopsis=anime_data['synopsis'],
                channel=anime_data['channel'],
                added_to=anime_data['added_to']
            )
            animes.append(anime)

        return animes
    
    def update_anime_added_to(self, anime: Anime):
        """
        Atualiza o campo added_to para um anime no banco de dados.
        """
        try:
            self.cursor.execute('''
                UPDATE animes 
                SET added_to = ?, channel = ?
                WHERE anime_id = ?
            ''', (anime.added_to, anime.channel, anime.anime_id))
            self.conn.commit() 
        except sqlite3.Error as e:
            print(f"Error updating added_to for anime {anime.title} - {anime.mal_id}: {e}")
            self.conn.rollback()

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

    def insert_episode(self, episode: Episode, print_log=False):
        if episode.anime_id == -1 or episode.anime_id == None or episode.mal_id == -1 or episode.mal_id == None:
            try:
                self.cursor.execute('''
                    INSERT INTO episodes (anime_id, mal_id, episode_number, watch_link, download_link_hd, download_link_sd, added_to) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    episode.anime_id, episode.mal_id, episode.episode_number, episode.watch_link, episode.download_link_hd, episode.download_link_sd, episode.added_to
                ))
                self.conn.commit()
                episode.episode_id = self.cursor.lastrowid 
                return episode.episode_id
            except sqlite3.IntegrityError as e:
                print(f"Error inserting episode for anime {episode.mal_id} - Episode {episode.episode_number}: {e}")
                self.conn.rollback()
                return None
        else:
            if print_log:
                print(f"Invalid episode: anime_id={episode.anime_id}, mal_id={episode.mal_id}")

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
    
    def get_episodes_by_mal_id(self, mal_id: int):
        """
        Get all episodes corresponding to a given MAL ID.

        Args:
            - mal_id: MAL ID of the anime.

        Returns:
            - List of Episode objects.
        """
        self.cursor.execute('''
            SELECT anime_id, episode_id, episode_number, watch_link, download_link_hd,
                download_link_sd, release_date, temp, added_to
            FROM episodes
            WHERE mal_id = ?
            ORDER BY release_date DESC, episode_number, added_to DESC
        ''', (mal_id,))
        
        rows = self.cursor.fetchall()
        if not rows:
            raise ValueError("No episodes found for the provided MAL ID.")
        episodes: List[Episode] = []
        column_names = [column[0] for column in self.cursor.description]  # Obter os nomes das colunas
        for row in rows:
            episode_data = dict(zip(column_names, row))  # Mapear nomes das colunas aos dados do episódio
            episode = Episode(
                episode_id=episode_data['episode_id'],
                anime_id=episode_data['anime_id'],
                mal_id=mal_id,
                episode_number=episode_data['episode_number'],
                watch_link=episode_data['watch_link'],
                download_link_hd=episode_data['download_link_hd'],
                download_link_sd=episode_data['download_link_sd'],
                release_date=episode_data['release_date'],
                temp=episode_data['temp'],
                added_to=episode_data['added_to']
            )
            episodes.append(episode)
        return episodes
    
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
            episode = Episode(
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
            episodes.append(episode)

        return episodes
    
    def update_episode_added_to(self, episode: Episode):
        """
        Atualiza o campo added_to para um episódio no banco de dados.
        """
        try:
            self.cursor.execute('''
                UPDATE episodes 
                SET added_to = ?
                WHERE episode_id = ?
            ''', (episode.added_to, episode.episode_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating added_to for episode {episode.episode_id} - {episode.mal_id}: {e}")
            self.conn.rollback()

    def close(self):
        self.conn.close()

    def close(self):
        self.cursor.close()
        self.conn.close()
    





