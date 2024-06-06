import psycopg2
from psycopg2 import sql
from typing import List, Optional
from shared_components.db_structs import Anime, Episode

class PostgreDB:
    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.conn = psycopg2.connect(**connection_params)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Criar tabela de animes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS animes (
                animes_id SERIAL PRIMARY KEY,            
                mal_id INTEGER UNIQUE NOT NULL,
                title TEXT UNIQUE NOT NULL,
                title_english UNIQUE TEXT,
                title_japanese UNIQUE TEXT,
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
                added_to TEXT
            )
        ''')
        # Criar tabela de episódios
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            episode_id BIGSERIAL PRIMARY KEY,
            mal_id INTEGER UNIQUE NOT NULL REFERENCES animes(mal_id),
            episode_number REAL NOT NULL,
            watch_link TEXT UNIQUE NOT NULL,
            download_link_hd UNIQUE TEXT NOT NULL,
            download_link_sd UNIQUE TEXT NOT NULL,
            release_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            temp BOOLEAN DEFAULT FALSE,
            added_to TEXT,
            UNIQUE (mal_id, episode_number),
        )
    ''')
        self.conn.commit()

    def insert_anime(self, anime: Anime):
        try:
            self.cursor.execute('''
                INSERT INTO animes (
                    mal_id, title, title_english, title_japanese, type, episodes, status, airing, aired, rating, 
                    duration, season, year, studios, producers, synopsis
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                anime.mal_id, anime.title, anime.title_english, anime.title_japanese, anime.type, anime.episodes,
                anime.status, anime.airing, anime.aired, anime.rating, anime.duration, anime.season, anime.year,
                anime.studios, anime.producers, anime.synopsis
            ))
            self.conn.commit()
            return self.cursor.lastrowid 
        except psycopg2.IntegrityError as e:
            print(f"Error inserting anime {anime.title} - {anime.mal_id}: {e}")
            self.conn.rollback()
            return None

    def get_anime_by_id(self, anime_id: int) -> Anime:
        self.cursor.execute('SELECT * FROM animes WHERE mal_id = %s', (anime_id,))
        row = self.cursor.fetchone()
        if row:
            return Anime.from_tuple(row)
        return None

    def get_anime_id_by_title(self, title: str) -> int:
        self.cursor.execute('SELECT mal_id FROM animes WHERE title = %s', (title,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return None
    
    def get_all_anime_titles_and_ids(self) -> list:
        self.cursor.execute('SELECT mal_id, title FROM animes')
        rows = self.cursor.fetchall()
        return [(row[0], row[1]) for row in rows]
    
    def get_animes_list(self, num_animes=1, return_all=False) -> list:
        if return_all:
            self.cursor.execute('SELECT mal_id, title, title_english, title_japanese, type, episodes, status, airing, aired, rating, duration, season, year, studios, producers, synopsis FROM animes')
        else:
            self.cursor.execute('SELECT mal_id, title, title_english, title_japanese, type, episodes, status, airing, aired, rating, duration, season, year, studios, producers, synopsis FROM animes ORDER BY mal_id DESC LIMIT %s', (num_animes,))
        rows = self.cursor.fetchall()
        return [{
            'mal_id': row[0],
            'title': row[1],
            'title_english': row[2],
            'title_japanese': row[3],
            'type': row[4],
            'episodes': row[5],
            'status': row[6],
            'airing': row[7],
            'aired': row[8],
            'rating': row[9],
            'duration': row[10],
            'season': row[11],
            'year': row[12],
            'studios': row[13],
            'producers': row[14],
            'synopsis': row[15]
        } for row in rows]
    
    def insert_episode(self, episode: Episode):
        try:
            self.cursor.execute('''
                INSERT INTO episodes (mal_id, episode_number, watch_link, download_link_hd, download_link_sd, temp) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                episode.mal_id, episode.episode_number, episode.watch_link, episode.download_link_hd, episode.download_link_sd, episode.temp
            ))
            self.conn.commit()
            return self.cursor.lastrowid 
        except psycopg2.IntegrityError as e:
            print(f"Error inserting episode for anime {episode.mal_id} - Episode {episode.episode_number}: {e}")
            self.conn.rollback()
            return None

    def get_episodes_by_anime_id(self, anime_id: int) -> List[Episode]:
        self.cursor.execute('SELECT * FROM episodes WHERE mal_id = %s', (anime_id,))
        rows = self.cursor.fetchall()
        episodes = []
        for row in rows:
            episode = Episode.from_tuple(row)  # Assuming Episode has a from_tuple method
            episodes.append(episode)
        return episodes
    
    def get_episode_id(self, episode: Episode) -> Optional[int]:
        """
        Checks if an episode already exists in the database and returns its ID if found.

        Args:
        - episode: Instance of the Episode object to be checked.

        Returns:
        - ID of the episode if found in the database, None otherwise.
        """
        try:
            self.cursor.execute('''
                SELECT id FROM episodes WHERE mal_id = %s AND episode_number = %s
            ''', (episode.mal_id, episode.episode_number))
            row = self.cursor.fetchone()
            if row:
                return row[0]  # Retorna o ID do episódio se encontrado
            else:
                return None  # Retorna None se o episódio não for encontrado
        except psycopg2.Error as e:
            print(f"Error getting episode ID: {e}")
            return None
    
    def get_episodes_list(self, num_episodes=1, return_all=False) -> list:
        if return_all:
            self.cursor.execute('SELECT id, mal_id, episode_number, watch_link, download_link_hd, download_link_sd, release_date, temp FROM episodes ORDER BY release_date DESC, episode_number DESC')
        else:
            self.cursor.execute('SELECT id, mal_id, episode_number, watch_link, download_link_hd, download_link_sd, release_date, temp FROM episodes ORDER BY release_date DESC, episode_number DESC LIMIT %s', (num_episodes,))
        rows = self.cursor.fetchall()

        return [{
            'id': row[0],
            'mal_id': row[1],
            'episode_number': row[2],
            'watch_link': row[3],
            'download_link_hd': row[4],
            'download_link_sd': row[5],
            'release_date': row[6],
            'temp': row[7]
        } for row in rows]

    def close(self):
        self.cursor.close()
        self.conn.close()

# Exemplo de conexão com parâmetros
connection_params = {
    'dbname': 'seu_banco_de_dados',
    'user': 'seu_usuario',
    'password': 'sua_senha',
    'host': 'localhost',
    'port': 5432
}