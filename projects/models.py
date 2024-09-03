from django.db import models
from admins.models import User
import uuid
# Create your models here.
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    users = models.ManyToManyField(User)
    admin_id= models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
class Logs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_id= models.ForeignKey(User, on_delete=models.CASCADE)
    date= models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()
    images = models.ManyToManyField('ScreenCaptures')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.log
    
class ScreenCaptures(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log_id = models.ForeignKey(Logs, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image