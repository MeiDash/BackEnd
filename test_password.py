from app.core.security import verify_password

# Test with admin password
hashed = '$pbkdf2-sha256$29000$eE9pTWmtNUaI0do7p/S.Nw$wo5uACZWzw7JkybiwYVpzxrtFGLii8AMUsD4XXZF8qk'
plain = 'admin123'
result = verify_password(plain, hashed)
print(f'Password verification for admin: {result}')

# Test with test password
hashed2 = '$pbkdf2-sha256$29000$pbRWas2Zc671PkdIyXmvVQ$g9REtpUWGDRPHbH/76F/DjzWz2xm13AdPp6C7KWzu8M'
plain2 = 'test123'
result2 = verify_password(plain2, hashed2)
print(f'Password verification for test: {result2}')