import sqlite3
from datetime import datetime, timedelta

# Conectar ao banco
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Verificar usuários
cursor.execute("SELECT id, email FROM users")
users = cursor.fetchall()
print("=== USUÁRIOS NO BANCO ===")
for u in users:
    print(f"  ID: {u[0]}, Email: {u[1]}")

if not users:
    print("Nenhum usuário encontrado. Encerrando.")
    conn.close()
    exit()

# Usar o primeiro usuário (ou user_id=1)
user_id = 1

# Dados de notas fiscais de exemplo
notas_exemplo = [
    {
        "empresa": "AGROPECUARIA DOCARIRI LTDA",
        "valor": 4203.00,
        "categoria": "Alimentação",
        "data": "2026-01-20"
    },
    {
        "empresa": "AGROPECUARIA DOCARIRI LTDA",
        "valor": 4203.00,
        "categoria": "Alimentação",
        "data": "2026-01-20"
    },
    {
        "empresa": "AGROPECUARIA DOCARIRI LTDA",
        "valor": 4203.00,
        "categoria": None,
        "data": "2026-01-20"
    },
    {
        "empresa": "AGROPECUARIA DOCARIRI LTDA",
        "valor": 4203.00,
        "categoria": None,
        "data": "2026-01-20"
    },
    {
        "empresa": "Chiquinho sorvetes",
        "valor": 5000.00,
        "categoria": "Material de Escritório",
        "data": "2024-10-26"
    },
]

print(f"\n=== INSERINDO {len(notas_exemplo)} NOTAS FISCAIS PARA USER_ID={user_id} ===")

for nota in notas_exemplo:
    cursor.execute("""
        INSERT INTO notas_fiscais (user_id, empresa, valor_total, categoria, data, created_at, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        nota["empresa"],
        nota["valor"],
        nota["categoria"],
        nota["data"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        f"/uploads/nota_{nota['empresa'][:10]}.pdf"  # URL fictícia
    ))
    print(f"  ✓ Inserida nota: {nota['empresa']} - R$ {nota['valor']}")

conn.commit()

# Verificar
cursor.execute("SELECT COUNT(*) FROM notas_fiscais WHERE user_id = ?", (user_id,))
total = cursor.fetchone()[0]
print(f"\n✓ Total de notas fiscais para user_id={user_id}: {total}")

conn.close()
