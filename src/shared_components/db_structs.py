import re


class Anime:
    def __init__(self, mal_id, title, title_english, title_japanese, type, episodes, status, airing, aired, rating, duration, season, year, studios, producers, synopsis):
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
        self.added_to = '@none'

    @classmethod
    def from_tuple(cls, data_tuple):
        return cls(
            mal_id=data_tuple[0],
            title=data_tuple[1],
            title_english=data_tuple[2],
            title_japanese=data_tuple[3],
            type=data_tuple[4],
            episodes=data_tuple[5],
            status=data_tuple[6],
            airing=data_tuple[7],
            aired=data_tuple[8],
            rating=data_tuple[9],
            duration=data_tuple[10],
            season=data_tuple[11],
            year=data_tuple[12],
            studios=data_tuple[13],
            producers=data_tuple[14],
            synopsis=data_tuple[15],
        )
    @classmethod
    def from_dict(cls, data):
        return cls(
            mal_id=data.get('mal_id'),
            title=data.get('title'),
            title_english=data.get('title_english'),
            title_japanese=data.get('title_japanese'),
            type=data.get('type'),
            episodes=data.get('episodes'),
            status=data.get('status'),
            airing=data.get('airing'),
            aired=data.get('aired'),
            rating=data.get('rating'),
            duration=data.get('duration'),
            season=data.get('season'),
            year=data.get('year'),
            studios=data.get('studios'),
            producers=data.get('producers'),
            synopsis=data.get('synopsis')
        )

    def to_tuple(self):
        return (
            self.mal_id, self.title, self.title_english, self.title_japanese, self.type, self.episodes, self.status,
            self.airing, self.aired, self.rating, self.duration, self.season,
            self.year, self.studios, self.producers, self.synopsis
        )  

    def addTo(self, plataform):
        # Verifica se começa com @, contém apenas letras minúsculas após @, e não tem espaços em branco
        if re.match(r'^@[a-z0-9_]+$', plataform):
            self.added_to += plataform
        else:
            raise ValueError("Plataform string must start with '@', contain only lowercase letters, and no spaces or multiple '@' characters.")

    def __str__(self):
        return (f"Anime(\n"
            f"    MAL ID: {self.mal_id}\n"
            f"    Title: {self.title}\n"
            f"    English Title: {self.title_english}\n"
            f"    Japanese Title: {self.title_japanese}\n"
            f"    Type: {self.type}\n"
            f"    Episodes: {self.episodes}\n"
            f"    Status: {self.status}\n"
            f"    Airing: {self.airing}\n"
            f"    Aired: {self.aired}\n"
            f"    Rating: {self.rating}\n"
            f"    Duration: {self.duration}\n"
            f"    Season: {self.season}\n"
            f"    Year: {self.year}\n"
            f"    Studios: {self.studios}\n"
            f"    Producers: {self.producers}\n"
            f"    Synopsis: {self.synopsis}\n"
            f"    AddedTo: {self.added_to}"
            f")"
        )
    
class Episode:
    def __init__(self, mal_id, episode_number, watch_link, download_link_hd, download_link_sd, temp=False):
        self.mal_id = mal_id
        self.episode_number = episode_number
        self.watch_link = watch_link
        self.download_link_hd = download_link_hd
        self.download_link_sd = download_link_sd
        self.temp = temp
        self.added_to = '@none'

    def to_tuple(self):
        return (
            self.mal_id, self.episode_number, self.watch_link, self.download_link_hd, self.download_link_sd, self.temp
        )
    
    def addTo(self, plataform):
        # Verifica se começa com @, contém apenas letras minúsculas após @, e não tem espaços em branco
        if re.match(r'^@[a-z0-9_]+$', plataform):
            self.added_to += plataform
        else:
            raise ValueError("Plataform string must start with '@', contain only lowercase letters, and no spaces or multiple '@' characters.")

    def __repr__(self):
        return (
            f"Episode(\n"
            f"    mal_id={self.mal_id},\n"
            f"    episode_number={self.episode_number},\n"
            f"    watch_link={self.watch_link},\n"
            f"    download_link_hd={self.download_link_hd},\n"
            f"    download_link_sd={self.download_link_sd},\n"
            f"    temp={self.temp},\n"
            f"    added_to{self.added_to},\n"
            f")"
        )

    @classmethod
    def from_tuple(cls, data):
        return cls(*data)
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            mal_id=data.get('mal_id'),
            episode_number=data.get('episode_number'),
            watch_link=data.get('watch_link'),
            download_link_hd=data.get('download_link_hd'),
            download_link_sd=data.get('download_link_sd'),
            temp=data.get('temp', False)  # Se não houver valor para temp, define como False por padrão
        )