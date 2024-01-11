from dataclasses import dataclass

from environs import Env

env = Env()
env.read_env()


@dataclass
class App:
    secret_key: str = env('SECRET_KEY')


@dataclass
class DataBase:
    db_name: str = env('DB_NAME')
    db_host: str = env('DB_HOST')
    db_user: str = env('DB_USER')
    db_password: str = env('DB_PASSWORD')
    db_port: int = env('DB_PORT')


@dataclass
class EmailSettings:
    email_host_user: str = env('EMAIL_HOST_USER')
    email_host_password: str = env('EMAIL_HOST_PASSWORD')

@dataclass
class Config:
    db = DataBase()
    app = App()
    settings_email = EmailSettings()


cfg = Config()



