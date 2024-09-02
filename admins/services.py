from . models import Admin

class AdminService:
    def get_all_admins():
        return Admin.objects.all()

    def create_admin(data):
        return Admin.objects.create(**data)

    def get_admin(pk):
        return Admin.objects.get(pk=pk)
    
    def get_admin_by_email(email):
        return Admin.objects.get(email=email)