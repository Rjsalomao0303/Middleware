# config.py
# Megatool
# Dev: Ricardo J. Salomão 04/04/2025 v1.1
# coding: utf-8

TOKEN_BD = 'M@t34200969#H@ndiX3420'
DEBUG_MODE = True  # Altere para True / False se não desejar logs de depuração
LOG_LEVEL = 'DEBUG' if DEBUG_MODE else 'INFO'
LOG_FILE = '/app/igo/middleware.log'

DATABASE_CONFIG = {
     'dsn': 'postgresql://handix:M%40t34200969@localhost:5432/handix'
}
