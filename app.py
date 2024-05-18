import logging
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Устанавливаем ваш Telegram API токен
TELEGRAM_TOKEN = '6972597302:AAFuPwFpuCgW45xetJoB2ZtsjB0kyH7syXM'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создаем логгер
logger = logging.getLogger(__name__)

# Настройка прокси с логином и паролем
PROXY = {
    "https": "http://coltellocuore:dzPJpqA7Ed@5.133.163.132:50100",
}

# Класс OpenAIClient для обработки запросов с прокси
class OpenAIClient:
    def __init__(self, api_key, proxies=None):
        self.api_key = api_key
        self.proxies = proxies
        self.base_url = "https://api.openai.com/v1"

    def chat_completion(self, model, messages):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages
        }
        try:
            response = requests.post(url, headers=headers, json=data, proxies=self.proxies)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

# Создаем клиента OpenAI с вашим API ключом и прокси
client = OpenAIClient(api_key='sk-proj-YkX1nGU81mQ6s2vcgqqjT3BlbkFJVFIh6aFFHIvH8gIIMGqx', proxies=PROXY)

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    """Отправляет приветственное сообщение при вводе команды /start."""
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! Я бот, который может ответить на ваши вопросы\!',
        reply_markup=ForceReply(selective=True),
    )

# Обработчик команды /help
async def help_command(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение с инструкциями при вводе команды /help."""
    await update.message.reply_text('Напишите мне любой вопрос, и я постараюсь вам помочь!')

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    """Отправляет ответ от модели LLM на любое текстовое сообщение."""
    try:
        user_message = update.message.text
        
        # Отправляем запрос к модели OpenAI для генерации ответа
        response = client.chat_completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_response = response['choices'][0]['message']['content'].strip()
        await update.message.reply_text(bot_response)
    except requests.exceptions.HTTPError as e:
        # Логируем детализированные ошибки HTTP
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        await update.message.reply_text(f'Произошла ошибка HTTP: {e.response.status_code}')
    except Exception as e:
        logger.error(f"Error while handling message: {e}")
        await update.message.reply_text('Произошла ошибка, пожалуйста, попробуйте позже.')

# Обработчик ошибок
async def error_handler(update: Update, context: CallbackContext) -> None:
    """Логирует ошибки, вызванные обновлениями Telegram."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text('Произошла ошибка, пожалуйста, попробуйте позже.')

# Основная функция для запуска бота
def main() -> None:
    """Запуск бота."""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Добавляем обработчик ошибок
    app.add_error_handler(error_handler)

    # Запуск бота в режиме polling
    app.run_polling()

# Запуск функции main при запуске скрипта
if __name__ == '__main__':
    main()
