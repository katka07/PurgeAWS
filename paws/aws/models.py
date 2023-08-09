from django.db import models

class AWSUser(models.Model):
    access_key = models.TextField(max_length=50)
    secret_key = models.TextField(max_length=50)

    def __str__(self):
        return f"User {self.id}"

class Resource(models.Model):
    user = models.ForeignKey(AWSUser, on_delete=models.CASCADE)
    resource_id = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)

    def __str__(self):
        return f"Resource {self.id} ({self.resource_type})"
