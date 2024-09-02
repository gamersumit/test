from .models import Project

class ProjectService:
    def get_all_projects():
        return Project.objects.all()
    
    def get_project(pk):
        return Project.objects.get(pk=pk)
    
    def filter_project_by_admin_id(admin_id):
        return Project.objects.filter(admin_id=admin_id)