from .models import Project,Logs,ScreenCaptures

class ProjectService:
    def get_all_projects():
        return Project.objects.all()
    
    def get_project(pk):
        return Project.objects.get(pk=pk)
    
    def filter_project_by_admin_id(admin_id):
        return Project.objects.filter(admin_id=admin_id)
    
    def filter_project_by_user_id(user_id):
        return Project.objects.filter(user=user_id)
    
class LogService:
    def get_all_logs():
        return Logs.objects.all()
    
    def get_log(pk):
        return Logs.objects.get(pk=pk)
    
    def filter_logs_by_project_id(project_id):
        return Logs.objects.filter(project_id=project_id)

class ScreenCaptureService:
    def get_all_screen_captures():
        return ScreenCaptures.objects.all()
    
    def get_screen_capture(pk):
        return ScreenCaptures.objects.get(pk=pk)
    
    def filter_screen_captures_by_log_id(log_id):
        return ScreenCaptures.objects.filter(log_id=log_id)