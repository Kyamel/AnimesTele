from abc import ABC, abstractmethod
from typing import List, Any, Union
from shared_components.db_structs import (
    Anime, Channel, Episode, MsgAn, MsgEp, Platform
)
from shared_components import values


class DatabaseManagerInterface(ABC):

    @abstractmethod
    def create_tables(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def execute_non_query(self, query: str, params: tuple = ()) -> Union[int | None]:
        pass

    @abstractmethod
    def fetch_value(self, query: str, params: tuple = ()) -> Any:
        pass

    @abstractmethod
    def fetch_one(self, query: str, params: tuple = ()) -> Any:
        pass

    @abstractmethod
    def fetch_all(self, query: str, params: tuple = ()) -> list:
        pass

    @abstractmethod
    def fetch_one_and_get_column_names(self, query: str, params: tuple = ()) -> tuple:
        pass

    @abstractmethod
    def fetch_all_and_get_column_names(self, quuery: str, params: tuple = ()) -> list[tuple]:
        pass

    @abstractmethod
    def get_cursor(self) -> Any:
        pass

    @abstractmethod
    def get_conn(self) -> Any:
        pass


class TableInterface(ABC):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__()
        self.database_manager = database_manager

    @abstractmethod
    def create_table(self) -> None:
        pass

    @abstractmethod
    def insert_data(self, db_struct) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, *args, **kwargs) -> int:
        pass

    @abstractmethod
    def get_by_id(self, id:int) -> Any:
        pass


class AnimesTableInterface(TableInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__(database_manager)

    @abstractmethod
    def create_table(self) -> None:
        pass

    @abstractmethod
    def insert_data(self, anime:Anime) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, mal_id:int) -> int:
        pass

    @abstractmethod
    def get_by_id(self, anime_id: int) -> Anime:
        pass

    @abstractmethod
    def get_by_mal_id(self, mal_id: int) -> Union[Anime, values.NOT_FOUND]:
        pass

class EpisodesTableInterface(TableInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__(database_manager)
    
    @abstractmethod
    def create_table(self) -> None:
        pass
    
    @abstractmethod
    def insert_data(self, episode:Episode) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, mal_id:int, episode_number:int) -> int:
        pass

    @abstractmethod
    def get_by_id(self, episode_id: int) -> Episode:
        pass

    @abstractmethod
    def get_by_mal_id(self, mal_id:int) -> Union[list[Episode], values.NOT_FOUND]:
        pass

class PlatformsTableInterface(TableInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__(database_manager)

    @abstractmethod    
    def create_table(self) -> None:
        pass

    @abstractmethod
    def insert_data(self, platform:Platform) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, platform_name:str) -> int:
        pass

    @abstractmethod
    def get_by_id(self, platform_id: int) -> Platform:
        pass

class ChannelsTableInterface(TableInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__(database_manager)

    @abstractmethod
    def create_table(self) -> None:
        pass

    @abstractmethod
    def insert_data(self, channel:Channel) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, platform_id:int, chat_id:int) -> int:
        pass

    @abstractmethod
    def get_by_id(self, channel_id: int) -> Channel:
        pass

class MsgsAnTableInterface(TableInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__(database_manager)

    @abstractmethod
    def create_table(self) -> None:
        pass

    @abstractmethod
    def insert_data(self, msg_an:MsgAn) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, anime_id:int, channel_id:int) -> int:
        pass

    @abstractmethod
    def get_by_id(self, msg_an_id: int) -> MsgAn:
        pass

class MsgsEpTableInterface(TableInterface):
    def __init__(self, database_manager: DatabaseManagerInterface) -> None:
        super().__init__(database_manager)

    @abstractmethod
    def create_table(self) -> None:
        pass

    @abstractmethod
    def insert_data(self, msg_ep:MsgEp) -> int:
        pass

    @abstractmethod
    def get_primary_key(self, episode_id:int, channel_id) -> int:
        pass

    @abstractmethod
    def get_by_id(self, msg_ep_id:int) -> MsgEp:
        pass

class EpisodeTableInterface(TableInterface):
    @abstractmethod
    def get_episodes_by_mal_id(self, mal_id: int) -> Union[List[Episode], values.NOT_FOUND]:
        pass


# Não faz sentido ter uma TableFactory pois isso reduziria a genericidade de meu código.
# Eu não posso ter diferentes factory para as tabelas, pois isso vai deixar meu código dependente da factory escolhida.
# Ao invés disso preciso de uma única classe com uma lógica adequada para de adaptar ao banco de dados usado.
# Uma ideia é usar o tipo do databaseManager selecionado para determinar isso.
# Teria de usar uma interface do databaseManager para determinar o tipo de databaseManager instanciado.
# Para que a Table ela possa se adaptar caso eu mude a instancia de databaseManager.