from . models import User

class AdminService:
    def get_all_admins():
        return User.objects.all()

    def create_admin(data):
        return User.objects.create(**data)

    def get_admin(pk):
        return User.objects.get(pk=pk)
    
    def get_admin_by_email(email):
        return User.objects.get(email=email)

class UserService:
    def get_all_users():
        return User.objects.all()
    
    def create_user(data):
        return User.objects.create(**data)
    
    def get_user(pk):
        return User.objects.get(pk=pk)
    
    def filter_user_by_admin_id(admin_id):
        return User.objects.filter(admin_id=admin_id)