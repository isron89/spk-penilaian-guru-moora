# import db

# db.add_user('erika','erika');

from werkzeug.security import generate_password_hash
hashed_password = generate_password_hash('kepsek')
print(hashed_password)