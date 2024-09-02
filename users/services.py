from . models import User

class UserService:
    def get_all_users():
        return User.objects.all()
    
    def create_user(data):
        return User.objects.create(**data)
    
    def get_user(pk):
        return User.objects.get(pk=pk)
    
    def filter_user_by_admin_id(admin_id):
        return User.objects.filter(admin_id=admin_id)