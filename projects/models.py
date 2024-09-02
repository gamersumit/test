from django.db import models
from users.models import User
from admins.models import Admin
import uuid
# Create your models here.
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ManyToManyField(User)
    admin_id= models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admin_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name