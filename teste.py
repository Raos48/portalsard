from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

# Imprime as variáveis de ambiente para debugar
print("DEBUG:", os.getenv("DEBUG"))
print("USER:", os.getenv("USER"))
print("PASSWORD:", os.getenv("PASSWORD"))
print("SERVER:", os.getenv("SERVER"))
print("DB:", os.getenv("DB"))


