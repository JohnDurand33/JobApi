from models import User

def get_user_id(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return user.id
    return None