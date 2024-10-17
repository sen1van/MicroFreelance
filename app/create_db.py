from app import app
app.app_context().push()
from app import db
from models import User
db.create_all()
admin = User()
admin.login = 'admin'
admin.set_password('admin')
admin.account_type = 'admin'
db.session.add(admin)
db.session.commit()

