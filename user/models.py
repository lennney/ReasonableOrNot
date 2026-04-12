from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=32, unique=False)
    email = models.EmailField()

    class Meta:
        db_table = "user"


class Phone(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    cpu = models.CharField(max_length=100, blank=True, default="")
    ram = models.IntegerField(default=0)
    rom = models.IntegerField(default=0)
    charging = models.IntegerField(default=0)
    battery = models.IntegerField(default=0)
    screen_refresh_rate = models.IntegerField(default=60)
    screen_resolution = models.CharField(max_length=20, blank=True, default="")
    weight = models.IntegerField(default=0)
    front_camera = models.IntegerField(default=0)
    rear_camera = models.IntegerField(default=0)
    screen_size = models.FloatField(default=0.0)

    class Meta:
        db_table = "phone"

    def __str__(self):
        return f"{self.brand} {self.model}"
