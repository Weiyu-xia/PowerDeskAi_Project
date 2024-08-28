from django.db import models

class User_infomation(models.Model):
    phone_number = models.CharField(max_length=15)
    id_number = models.CharField(max_length=18)
    user_code = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20)
    property_address = models.CharField(max_length=255)
    has_multiple_properties = models.BooleanField(default=False)

    def __str__(self):
        return self.phone_number
