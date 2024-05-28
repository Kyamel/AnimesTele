import datetime
from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup, Message
from local.db_sqlite3 import Database
from shared_components import values
from local import db_sqlite3_acess 

class Telena:

    def __init__(self, token):
        self.token = token
        self.bot = Bot(token=token)

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
        
    def upload_video(self, chat_id, http_url, caption):
        response = self.bot.send_document(chat_id=chat_id, video=http_url, caption=caption)
        return response

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

    async def add_anime_to_telegram(self, chat_id, mal_id: int, database_path=values.DATABASE_PATH):
        anime, episodes = db_sqlite3_acess.get_anime_from_database(mal_id=mal_id, database_path=database_path)
        # Verificar se o anime ainda não foi adicionado ao Telegram
        if '@none' in anime.added_to:
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
            
            # Enviar mensagem com os campos do anime para o canal
            returned_anime_message: Message = await self.write_message(chat_id=chat_id, msg_text=anime_message)           
            # Atualizar o campo added_to no banco de dados com o ID da mensagem do Telegram
            anime.added_to = f"@telegram={returned_anime_message.id}"
            db_sqlite3_acess.update_anime_added_to(anime)
            
            return returned_anime_message
        else:
            # Se o anime já estiver adicionado ao Telegram, tentar adicionar os episódios
            for episode in episodes:
                if '@none' in episode.added_to:
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
                        f"Temp: {episode.temp}"
                        f"Added to: {episode.added_to}"
                    )
                    
                    # Enviar mensagem com os campos do episódio para o canal
                    returned_episode_message: Message = await self.write_message(chat_id, episode_message)
                    
                    # Atualizar o campo added_to no banco de dados com o ID da mensagem do Telegram
                    new_added_to = f"@telegram={returned_episode_message.id}"
                    if anime.added_to == "@none":
                        anime.added_to = new_added_to
                    else:
                        anime.added_to = f"{anime.added_to},{new_added_to}"
                    db_sqlite3_acess.update_episode_added_to(episode)
            
            return None