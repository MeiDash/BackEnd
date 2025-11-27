"""Script para testar bcrypt direto"""
import bcrypt

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
        # Truncar para 72 bytes se necessário
        pwd_bytes = pwd.encode('utf-8')
        if len(pwd_bytes) > 72:
            pwd_bytes = pwd_bytes[:72]
            
        # Hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        print(f"  ✓ Hash direto: OK")
        
        # Verificar
        verified = bcrypt.checkpw(pwd_bytes, hashed)
        print(f"  ✓ Verificação: {verified}")
    except Exception as e:
        print(f"  ✗ Erro: {e}")
