import re

class Anime:
    def __init__(self, mal_id, title, title_english, title_japanese, type,
                  episodes, status, airing, aired, rating, duration, season,
                    year, studios, producers, synopsis, channel='#none', added_to='#none', anime_id=-1):
        self.anime_id = anime_id
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
        self.channel = channel
        self.added_to = added_to

    @classmethod
    def from_tuple(cls, data_tuple):
        """
        Consider using the from_dict method instead.
        """
        return cls(
            anime_id=data_tuple[0],
            mal_id=data_tuple[1],
            title=data_tuple[2],
            title_english=data_tuple[3],
            title_japanese=data_tuple[4],
            type=data_tuple[5],
            episodes=data_tuple[6],
            status=data_tuple[7],
            airing=data_tuple[8],
            aired=data_tuple[9],
            rating=data_tuple[10],
            duration=data_tuple[11],
            season=data_tuple[12],
            year=data_tuple[13],
            studios=data_tuple[14],
            producers=data_tuple[15],
            synopsis=data_tuple[16],
            channel=data_tuple[17] if len(data_tuple) > 17 else '#none',
            added_to=data_tuple[18] if len(data_tuple) > 18 else '#none'
        )

    @classmethod
    def from_dict(cls, data):
        return cls(
            anime_id=data.get('anime_id', -1),
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
            synopsis=data.get('synopsis'),
            channel=data.get('channel', '#none'),
            added_to=data.get('added_to', '#none'),
        )

    def to_tuple(self, include_anime_id=True):
        """
        Consider using the to_dict method instead.
        """
        if include_anime_id:
            return (
                self.anime_id, self.mal_id, self.title, self.title_english, self.title_japanese, self.type, self.episodes, self.status,
                self.airing, self.aired, self.rating, self.duration, self.season,
                self.year, self.studios, self.producers, self.synopsis, self.channel, self.added_to
            )
        else:
            return (
                self.mal_id, self.title, self.title_english, self.title_japanese, self.type, self.episodes, self.status,
                self.airing, self.aired, self.rating, self.duration, self.season,
                self.year, self.studios, self.producers, self.synopsis, self.channel, self.added_to
            )

    def to_dict(self):
        return {
            'anime_id': self.anime_id,
            'mal_id': self.mal_id,
            'title': self.title,
            'title_english': self.title_english,
            'title_japanese': self.title_japanese,
            'type': self.type,
            'episodes': self.episodes,
            'status': self.status,
            'airing': self.airing,
            'aired': self.aired,
            'rating': self.rating,
            'duration': self.duration,
            'season': self.season,
            'year': self.year,
            'studios': self.studios,
            'producers': self.producers,
            'synopsis': self.synopsis,
            'channel': self.channel,
            'added_to': self.added_to
        }  

    def add_to(self, platform):
        if re.match(r'^(#[a-zA-Z0-9_=@]+)+$', platform):
            if platform not in self.added_to.split():
                self.added_to += f' {platform}'
        else:
            raise ValueError("Platform string must start with '#', contain only lowercase letters, numbers, underscores, and no spaces or multiple '@' characters.")

    def __str__(self):
        return (f"Anime(\n"
                f"    anime_id: {self.anime_id}\n"
                f"    mal_id: {self.mal_id}\n"
                f"    title: {self.title}\n"
                f"    english title: {self.title_english}\n"
                f"    japanese title: {self.title_japanese}\n"
                f"    type: {self.type}\n"
                f"    episodes: {self.episodes}\n"
                f"    status: {self.status}\n"
                f"    airing: {self.airing}\n"
                f"    aired: {self.aired}\n"
                f"    rating: {self.rating}\n"
                f"    duration: {self.duration}\n"
                f"    season: {self.season}\n"
                f"    year: {self.year}\n"
                f"    studios: {self.studios}\n"
                f"    producers: {self.producers}\n"
                f"    synopsis: {self.synopsis}\n"
                f"    channel: {self.channel}\n"
                f"    added_to: {self.added_to}\n"
                f")"
                )
   
class Episode:
    def __init__(self, mal_id, episode_number, watch_link, download_link_hd,
                  download_link_sd, anime_id=-1, episode_id=-1, release_date=-1, temp=False, added_to='#none'):
        self.anime_id = anime_id
        self.episode_id = episode_id
        self.mal_id = mal_id
        self.episode_number = episode_number
        self.watch_link = watch_link
        self.download_link_hd = download_link_hd
        self.download_link_sd = download_link_sd
        self.release_date = release_date,
        self.temp = temp
        self.added_to = added_to

    @classmethod
    def from_dict(cls, data):
        return cls(
            episode_id=data.get('episode_id', -1),
            anime_id=data.get('anime_id'),
            mal_id=data.get('mal_id'),
            episode_number=data.get('episode_number'),
            watch_link=data.get('watch_link'),
            download_link_hd=data.get('download_link_hd'),
            download_link_sd=data.get('download_link_sd'),
            release_date=data.get('release_date', -1),
            temp=data.get('temp', False),  # Se não houver valor para temp, define como False por padrão
            added_to=data.get('added_to', '#none')
        )

    def to_tuple(self, include_episode_id=True):
        if(include_episode_id):
            return (
                self.episode_id, self.anime_id, self.mal_id, self.episode_number, self.watch_link,
                self.download_link_hd, self.download_link_sd, self.release_date, self.temp, self.added_to
            )
        else:
            return(
                self.anime_id, self.mal_id, self.episode_number, self.watch_link,
                self.download_link_hd, self.download_link_sd, self.release_date, self.temp, self.added_to
            )
        
    def to_dict(self):
        return {
            'episode_id': self.episode_id,
            'anime_id': self.anime_id,
            'mal_id': self.mal_id,
            'episode_number': self.episode_number,
            'watch_link': self.watch_link,
            'download_link_hd': self.download_link_hd,
            'download_link_sd': self.download_link_sd,
            'release_date': self.release_date,
            'temp': self.temp,
            'added_to': self.added_to
        }
    
    def add_to(self, platform):
        if re.match(r'^(#[a-zA-Z0-9_=@]+)+$', platform):
            if platform not in self.added_to.split():
                self.added_to += f' {platform}'
        else:
            raise ValueError("Platform string must start with '#', contain only lowercase letters, numbers, underscores, equals sign, and no spaces or multiple '@' characters.")

    def __repr__(self):
        return (
            f"Episode(\n"
            f"    episode_id={self.episode_id},\n"
            f"    anime_id={self.anime_id},\n"
            f"    mal_id={self.mal_id},\n"
            f"    episode_number={self.episode_number},\n"
            f"    watch_link={self.watch_link},\n"
            f"    download_link_hd={self.download_link_hd},\n"
            f"    download_link_sd={self.download_link_sd},\n"
            f"    temp={self.temp},\n"
            f"    added_to={self.added_to}\n"
            f")"
        )

   