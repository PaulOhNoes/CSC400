from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.urls import reverse

# Create your models here.


class Organization(models.Model):
    user = models.OneToOneField(User,  on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    # TODO file = models.ImageField(default='default.jpg', upload_to='profile_pics')
    verified = models.BooleanField(default=False)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    #abbreviated state name
    state = models.CharField(max_length=2)
    # TODO min_length, max_length
    zipcode = models.IntegerField()
    file = models.FileField(default='verification_files/default.pdf', upload_to='verification_files',
                            validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    def __str__(self):
        return self.name


class Drive(models.Model):
    # TODO orgID, end_date
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    orgID = models.ForeignKey(Organization, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('drive-detail', kwargs={'pk': self.pk})

    # user.post_set will find all posts created by the user


class userDrives(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    driveID = models.ForeignKey(Drive, on_delete=models.CASCADE)
    join_date = models.DateTimeField(default=timezone.now)


class Donation(models.Model):
    driveID = models.ForeignKey(Drive, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)
    # TODO verification code
    # UUID is randomly generated code
    code = models.UUIDField()


class DonationItem(models.Model):
    donationID = models.ForeignKey(Donation, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    quantity = models.IntegerField()


class Notifications(models.Model):
    driveID = models.ForeignKey(Drive, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)