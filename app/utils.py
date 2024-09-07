from models import User
def check_role(user: User, roles: list[str]):
    if user.is_authenticated and user.account_type in roles:
        return True
    False
    
    