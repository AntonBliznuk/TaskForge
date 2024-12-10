from django.db import models
from cloudinary.models import CloudinaryField


class Task(models.Model):
    group_id = models.IntegerField()
    title = models.CharField(max_length=255, blank=False)
    discription = models.TextField()
    status = models.CharField(max_length=50, default='posted')
    photo = CloudinaryField('image')
    user_id = models.IntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return f'{self.title}  {self.status}'
    
    def take(self, user_id):
        self.status = 'taken'
        self.user_id = user_id
        return
    
    def finish(self):
        self.status = 'finished'
        return
        

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


