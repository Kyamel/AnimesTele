import asyncio
import datetime
import httpx
from telegram import Bot, InputMediaVideo, KeyboardButton, ReplyKeyboardMarkup, Message
from telegram.error import TimedOut
from src.shared_components import values
from src.local import db_sqlite3_acess 
from src.shared_components.api.bot_api.sensitive import token

class Telena:

    def __init__(self, token=token.TOKEN_TELENA):
        self.token = token
        self.bot = Bot(token=token)
        platform, channel = db_sqlite3_acess.init_animestele()
        self.platform = platform
        self.chaneel = channel

    def check_token(self):
        user = self.bot.getMe()
        print(user)

    def create_channel(self, name: str, description: str):
        channel = self.bot.create_channel(name, description)
        return channel
    
    def search_channel(self, query):
        chaneels = self.bot.search_channels(query)
        for channel in chaneels:
            return channel
    
    def write_message(self, chat_id, msg_text):
        try:
            message = self.bot.send_message(chat_id=chat_id, text=msg_text)
            # Retornar um objeto Message
            return message
        except Exception as e:
            print(f"Erro ao escrever mensagem: {e}")
            return None

    def search_message(self, chat_id, query):
        messages = self.bot.search_messages(chat_id, query)
        return messages
    
    async def fetch_url(self, url):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Isso vai lançar um erro se o status não for 200-399
            return response
            
    async def upload_video(self, chat_id, http_url, print_log=False):
        try:
            if(print_log):
               print(f"Checking http url:\n{http_url}\n...")
            await self.fetch_url(http_url)
            
            if print_log:
                print("Trying to send video...")
            response = await self.bot.send_video(chat_id=chat_id, video=http_url)
            return response
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            print(f"HTTP error occurred: {e}")
        except (httpx.ReadTimeout, asyncio.exceptions.CancelledError) as e:
            print(f"Timeout error occurred: {e}. Retrying...")
            await asyncio.sleep(3)  # Espera antes de tentar novamente
            try:
                await self.fetch_url(http_url)
                response = await self.bot.send_video(chat_id=chat_id, video=http_url)
                return response
            except Exception as e:
                print(f"Failed again: {e}")
                raise
        except Exception as e:
            print(f"Unhandled exception: {e}")
            raise

    def write_coments_view_message(self, chat_id, msg_test):
        keyboard = ReplyKeyboardMarkup([[KeyboardButton('Ver comentários')]])
        response = self.bot.send_message(chat_id=chat_id, text=msg_test, reply_markup=keyboard)
        return response
    
    def edit_messages(self, chat_id, message_id, new_text):
        try:
            self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)
            print("Mensagem editada com sucesso!")
        except Exception as e:
            print(f"Erro ao editar mensagem: {e}")

    # Função para modificar a imagem de perfil do canal
    def modificar_imagem_perfil(self, chat_id,image_path):
        try:
            with open(image_path, 'rb') as photo:
                self.bot.set_chat_photo(chat_id=chat_id, photo=photo)
            print("Imagem de perfil do canal modificada com sucesso!")
        except Exception as e:
            print(f"Erro ao modificar imagem de perfil do canal: {e}")

    async def edit_message(self, chat_id, message_id, new_text):
        try:
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text
            )
            print(f"Message {message_id} in chat {chat_id} was successfully edited.")
        except Exception as e:
            print(f"Error editing message {message_id} in chat {chat_id}: {e}")


    async def add_anime_to_telegram(self, chat_id, mal_id: int, database_path=values.DATABASE_PATH, print_log=False):
        try:
            if print_log:
                print(f"Trying to send anime {mal_id} to telegram channel {chat_id}")
            anime, episodes = db_sqlite3_acess.get_anime_from_database(mal_id=mal_id, database_path=database_path)
            
            # Verify if anime is not in telegram yet
            if '#telegram' not in anime.added_to:
                # Formatar mensagem com os campos do anime
                anime_message = (
                    f"Anime ID: {anime.mal_id}\n"
                    f"Title: {anime.title}\n"
                    f"English Title: {anime.title_english}\n"
                    f"Japanese Title: {anime.title_japanese}\n"
                    f"Type: {anime.type}\n"
                    f"Episodes: {anime.episodes}\n"
                    f"Status: {anime.status}\n"
                    f"Airing: {anime.airing}\n"
                    f"Aired: {anime.aired}\n"
                    f"Rating: {anime.rating}\n"
                    f"Duration: {anime.duration}\n"
                    f"Season: {anime.season}\n"
                    f"Year: {anime.year}\n"
                    f"Studios: {anime.studios}\n"
                    f"Producers: {anime.producers}\n"
                    f"Synopsis: {anime.synopsis}\n"
                )
                
                try:
                    # send message
                    returned_anime_message: Message = await self.write_message(chat_id=chat_id, msg_text=anime_message)
                    # if message sent susscefully, update channel
                    new_channel = f'#telegram={chat_id}'
                    if anime.channel == '#none':
                        anime.channel = new_channel
                    else:
                        anime.channel = f"{anime.channel},{new_channel}"           
                    new_added_to = f"#telegram={returned_anime_message.message_id}"
                    #  update added_to
                    if anime.added_to == "#none":
                        anime.added_to = new_added_to
                    else:
                        anime.added_to = f"{anime.added_to},{new_added_to}"
                    # save into database    
                    db_sqlite3_acess.save_msg_an(anime)
                    if print_log:
                        print(anime)
                except Exception as e:
                    print(f"Failed to send anime message: {e}")
                    return None
                
            else:
                if print_log:
                    print(f"Anime \"{anime.title}\" already in telegram at channel: {anime.channel} and message: {anime.added_to}.")
            
            for episode in episodes:
                # Se o anime já estiver adicionado ao Telegram, tentar adicionar os episódios
                if '#telegram' not in episode.added_to:
                    # Formatar mensagem com os campos do episódio
                    episode_message = (
                        f"Episode ID: {episode.episode_id}\n"
                        f"Anime ID: {episode.anime_id}\n"
                        f"Anime MAL ID: {episode.mal_id}\n"
                        f"Episode Number: {episode.episode_number}\n"
                        f"Watch Link: {episode.watch_link}\n"
                        f"Download Link HD: {episode.download_link_hd}\n"
                        f"Download Link SD: {episode.download_link_sd}\n"
                        f"Release Date: {episode.release_date}\n"
                        f"Temp: {episode.temp}\n"
                        f"Added to: {episode.added_to}\n"
                    )
                    
                    try:
                        # Enviar mensagem com os campos do episódio para o canal
                        returned_episode_message: Message = await self.write_message(chat_id, episode_message)
                        
                        # Atualizar o campo added_to no banco de dados com o ID da mensagem do Telegram
                        new_added_to = f"#telegram={returned_episode_message.message_id}"
                        if episode.added_to == "#none":
                            episode.added_to = new_added_to
                        else:
                            episode.added_to = f"{episode.added_to},{new_added_to}"
                        db_sqlite3_acess.save_msg_ep(episode)
                        if print_log:
                            print(episode)
                    except Exception as e:
                        print(f"Failed to send episode message: {e}")
                        return None
                    
                else:
                    if print_log:
                        print(f"Episode {episode.episode_number} already in telegram at message: {episode.added_to}")
                    
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
