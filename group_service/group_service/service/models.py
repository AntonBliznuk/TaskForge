from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=255, blank=False)
    password = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now=True)
    creater_id = models.IntegerField(blank=False)

    def __str__(self):
        return f'{self.name} [{self.id}]'
    
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'



class Role(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'



class UserToGroup(models.Model):
    user_id = models.IntegerField(blank=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    join_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user_id}({self.role}) -> {self.group}'
    
    class Meta:
        verbose_name = 'User To Group'
        verbose_name_plural = 'Users To Groups'
