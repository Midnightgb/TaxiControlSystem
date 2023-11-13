import secrets

# Generar una SECRET_KEY de 32 bytes (256 bits)
SECRET_KEY = secrets.token_hex(32)

# Imprimir la clave generada
print("SECRET_KEY:", SECRET_KEY)