import sqlite3
from typing import Type, TypeVar
from database.db_sqlite3 import (
    SQLiteAnimes, SQLiteChannels, SQLiteEpisodes, SQLiteMsgsAn, SQLiteMsgsEp, SQLitePlatforms
)
from interface.db_interface import (
    AnimesTableInterface, ChannelsTableInterface, DatabaseManagerInterface, EpisodesTableInterface,
    MsgsAnTableInterface, MsgsEpTableInterface, PlatformsTableInterface, TableInterface
)
from shared_components import values

class SQLiteDatabaseManager(DatabaseManagerInterface):
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        table = TableFactory(self)
        table.get_animes().create_table()
        table.get_episodes().create_table()
        table.get_platforms().create_table()
        table.get_channels().create_table()
        table.get_msgs_an().create_table()
        table.get_msgs_ep().create_table()
        
    def execute_non_query(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def fetch_value(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            value = self.cursor.fetchone()
            if value:
                return value[0]
            return None
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def fetch_one(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def fetch_all(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def fetch_one_and_get_column_names(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            row = self.cursor.fetchone()
            if row:
                column_names = [description[0] for description in self.cursor.description]
                return row, column_names
            return None, None
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e
    
    def fetch_all_and_get_column_names(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            column_names = [description[0] for description in self.cursor.description]
            return rows, column_names
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def close(self):
        self.conn.close()

    def get_cursor(self):
        return self.cursor
    
    def get_conn(self):
        return self.conn

class DatabaseManagerFactory:
    @staticmethod
    def create_sqlite_db_manager() -> DatabaseManagerInterface:
        return SQLiteDatabaseManager(values.SQLITE_DATABASE_PATH)

T = TypeVar('T', bound=TableInterface)
class TableFactory:
    def __init__(self, database_manager: DatabaseManagerInterface):
        self.database_manager = database_manager

    def _check_db_manager(self, table_class: Type[T]) -> T:
        if isinstance(self.database_manager, SQLiteDatabaseManager):
            return table_class(self.database_manager)
        else:
            raise ValueError("Unsupported database type")

    def get_animes(self) -> AnimesTableInterface:
        return self._check_db_manager(SQLiteAnimes)

    def get_episodes(self) -> EpisodesTableInterface:
        return self._check_db_manager(SQLiteEpisodes)

    def get_platforms(self) -> PlatformsTableInterface:
        return self._check_db_manager(SQLitePlatforms)

    def get_channels(self) -> ChannelsTableInterface:
        return self._check_db_manager(SQLiteChannels)

    def get_msgs_an(self) -> MsgsAnTableInterface:
        return self._check_db_manager(SQLiteMsgsAn)

    def get_msgs_ep(self) -> MsgsEpTableInterface:
        return self._check_db_manager(SQLiteMsgsEp)