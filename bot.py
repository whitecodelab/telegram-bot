import logging
import os  # ← ДОБАВИТЬ ЭТУ СТРОКУ!
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self):
        self.db = Database()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Сохраняем пользователя в БД
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Приветственное сообщение
        welcome_text = f"""
👋 Привет, {user.first_name}!

Я простой бот-визитка с базой данных PostgreSQL.

Доступные команды:
/start - начать работу
/help - помощь  
/stats - статистика
        """
        
        await update.message.reply_text(welcome_text)
        logger.info(f"👤 Пользователь {user.id} запустил бота")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
ℹ️ **Помощь по боту**

Это демонстрационный бот с подключением к PostgreSQL.

**Команды:**
/start - Начать работу с ботом
/help - Показать это сообщение  
/stats - Показать статистику пользователей

Бот сохраняет информацию о пользователях в базе данных.
        """
        await update.message.reply_text(help_text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        users_count = self.db.get_users_count()
        
        stats_text = f"""
📊 **Статистика бота**

👥 Всего пользователей: {users_count}

💾 Данные хранятся в PostgreSQL
🔄 Бот работает локально
        """
        
        await update.message.reply_text(stats_text)
        logger.info(f"📊 Показана статистика: {users_count} пользователей")
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
    
    def run(self):
        """Запуск бота"""
        try:
            # Создаем таблицы если их нет
            self.db.create_tables()
            
            # ЗАМЕНА: Используем os.getenv вместо Config
            self.application = Application.builder().token(os.getenv('BOT_TOKEN')).build()
            
            # Настраиваем обработчики
            self.setup_handlers()
            
            # Запускаем бота
            logger.info("🤖 Бот запускается...")
            self.application.run_polling()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
        finally:
            self.db.close()

if __name__ == "__main__":
    bot = SimpleBot()
    bot.run()