from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from donos.models import Drive
from PIL import Image

# Create your models here.


class Profile(models.Model):
    # TODO binary org Column
    user = models.OneToOneField(User,  on_delete=models.CASCADE, null=True)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    # abbreviated state name
    state = models.CharField(max_length=2)
    # TODO min_length, max_length
    zipcode = models.CharField(max_length=5)
    follows = models.ManyToManyField('donos.Drive', related_name='followed_by')

    def __str__(self):
        return f'{self.user.username} Profile'

    # resize images
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

