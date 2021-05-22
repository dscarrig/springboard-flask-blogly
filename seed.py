from models import User, Tag, db
from app import app

db.drop_all()
db.create_all()

User.query.delete()

db.session.add(User(
    first_name = "Bob",
    last_name = "Barfly",
    image_url = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"
))

db.session.add(User(first_name = "George",
    last_name = "Meany",
    image_url = "https://upload.wikimedia.org/wikipedia/en/d/d1/Meany-George-portrait.jpg"))

db.session.add(Tag(name = "TestTag"))

db.session.commit()