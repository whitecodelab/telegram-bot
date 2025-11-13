import psycopg2
import os
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Подключение к базе данных с поддержкой Railway и локальной разработки"""
        try:
            # Пытаемся получить DATABASE_URL от Railway
            database_url = os.getenv('DATABASE_URL')
            
            if database_url:
                # Для Railway
                parsed_url = urlparse(database_url)
                db_conn_config = {
                    'dbname': parsed_url.path[1:],
                    'user': parsed_url.username,
                    'password': parsed_url.password,
                    'host': parsed_url.hostname,
                    'port': parsed_url.port
                }
                logger.info("🔗 Используем DATABASE_URL от Railway")
            else:
                # Для локальной разработки
                db_conn_config = {
                    'dbname': os.getenv('DB_NAME', 'telegram_bot'),
                    'user': os.getenv('DB_USER', 'postgres'),
                    'password': os.getenv('DB_PASSWORD', 'postgres'),
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'port': os.getenv('DB_PORT', '5432')
                }
                logger.info("🔗 Используем локальные настройки БД")
            
            self.connection = psycopg2.connect(**db_conn_config)
            logger.info("✅ Успешно подключились к PostgreSQL")
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            raise
    
    def create_tables(self):
        """Создание таблиц если их нет"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT UNIQUE NOT NULL,
                        username VARCHAR(100),
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                self.connection.commit()
                logger.info("✅ Таблица users создана/проверена")
        except Exception as e:
            logger.error(f"❌ Ошибка создания таблицы: {e}")
            raise
    
    def add_user(self, user_id, username, first_name, last_name):
        """Добавление пользователя в базу"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                ''', (user_id, username, first_name, last_name))
                self.connection.commit()
                logger.info(f"✅ Пользователь {user_id} добавлен в БД")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка добавления пользователя: {e}")
            return False
    
    def get_users_count(self):
        """Получение количества пользователей"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM users')
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"❌ Ошибка получения количества пользователей: {e}")
            return 0
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
            logger.info("✅ Соединение с БД закрыто")