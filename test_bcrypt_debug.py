"""Script para debugar problema com bcrypt"""
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12
)

# Testar várias senhas
test_passwords = [
    "admin123",
    "securepass",
    "password123",
    "a" * 50,
    "a" * 72,
    "a" * 100,
]

for pwd in test_passwords:
    print(f"\nTestando senha: '{pwd[:20]}{'...' if len(pwd) > 20 else ''}' ({len(pwd)} chars, {len(pwd.encode('utf-8'))} bytes)")
    try:
        # Tentar hash direto
        hashed = pwd_context.hash(pwd)
        print(f"  ✓ Hash direto: OK")
        
        # Tentar verificar
        verified = pwd_context.verify(pwd, hashed)
        print(f"  ✓ Verificação: {verified}")
    except Exception as e:
        print(f"  ✗ Erro: {e}")
