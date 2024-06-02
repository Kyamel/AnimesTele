from typing import Optional


class Anime:
    def __init__(
            self, mal_id:int, title:str,  year:int,  season:str, title_english:Optional[str] = None, title_japanese:Optional[str] = None, type:Optional[str] = None, episodes:Optional[int] = None, 
            status:Optional[str] = None, airing:Optional[bool] = None, aired:Optional[str] = None, rating:Optional[int] = None, duration:Optional[str] = None,
            studios:Optional[str] = None, producers:Optional[str] = None, synopsis:Optional[str]=None
        ):
        self.mal_id = mal_id
        self.title = title
        self.title_english = title_english
        self.title_japanese = title_japanese
        self.type = type
        self.episodes = episodes
        self.status = status
        self.airing = airing
        self.aired = aired
        self.rating = rating
        self.duration = duration
        self.season = season
        self.year = year
        self.studios = studios
        self.producers = producers
        self.synopsis = synopsis
        self.anime_id:int = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())


class Episode:
    # in temp (temporary episode) attibute, use 0 to false, 1 to true.
    def __init__(self, anime_id:int, mal_id:int, episode_number:int, watch_link:str, download_link_hd:str, download_link_sd:str, temp=None):
        self.anime_id = anime_id
        self.mal_id = mal_id
        self.episode_number = episode_number
        self.watch_link = watch_link
        self.download_link_hd = download_link_hd
        self.download_link_sd = download_link_sd
        self.temp = temp
        self.episode_id:int = None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())


class Platform:
    def __init__(self, platform_name:str):
        self.platform_name = platform_name
        self.platfotm_id:int=None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())


class Channel:
    def __init__(self, platform_id, chat_name=None, chat_id=None, chat_description=None):
        self.platform_id = platform_id
        self.chat_name = chat_name
        self.chat_id = chat_id
        self.chat_description = chat_description
        self.channel_id:int=None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())


class MsgAn:
    def __init__(self, anime_id, message_id, channel_id):
        self.anime_id = anime_id
        self.message_id = message_id
        self.channel_id = channel_id
        self.msg_an_id:int=None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())

class MsgEp:
    def __init__(self, episode_id, message_id, channel_id):
        self.episode_id = episode_id
        self.message_id = message_id
        self.channel_id = channel_id
        self.msg_ep_id:int=None

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())

class MsgGe:
    def __init__(self, message_id, channel_id, type, description=None):
        self.message_id = message_id
        self.channel_id = channel_id
        self.type = type
        self.description = description

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())

class User:
    def __init__(self, name, general_notification_on=0):
        self.name = name
        self.general_notification_on = general_notification_on

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())


class UserInPlatform:
    def __init__(self, user_id, platform_id, user_id_on_platform, platform_notification_on=0):
        self.user_id = user_id
        self.platform_id = platform_id
        self.user_id_on_platform = user_id_on_platform
        self.platform_notification_on = platform_notification_on

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())


class UserInChannel:
    def __init__(self, user_id, channel_id, user_name_on_channel, channel_notification_on=0):
        self.user_id = user_id
        self.channel_id = channel_id
        self.user_name_on_channel = user_name_on_channel
        self.channel_notification_on = channel_notification_on

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())

class UserAnimeRelationship:
    def __init__(self, user_id, anime_id, relationship_state):
        self.user_id = user_id
        self.anime_id = anime_id
        self.relationship_state = relationship_state

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())
    
class AnimeRating:
    def __init__(self, user_id, anime_id, rating=None, favorite=1):
        self.user_id = user_id
        self.anime_id = anime_id
        self.rating = rating
        self.favorite = favorite

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())

class AnimeNotification:
    def __init__(self, user_id, anime_id, channel_id=None):
        self.user_id = user_id
        self.anime_id = anime_id
        self.channel_id = channel_id

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())

class WatchList:
    def __init__(self, user_id, episode_id, watched_status=1):
        self.user_id = user_id
        self.episode_id = episode_id
        self.watched_status = watched_status

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_dict())
