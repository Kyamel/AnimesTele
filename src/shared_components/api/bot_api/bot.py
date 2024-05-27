import datetime
from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup, Message
from shared_components import values

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

