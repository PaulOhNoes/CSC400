from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.urls import reverse
from PIL import Image

# Create your models here.

class Organization(models.Model):
    user = models.OneToOneField(User,  on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    verified = models.BooleanField(default=False)
    logo = models.ImageField(default='logo_pics/default.jpg', upload_to='logo_pics')
    header = models.ImageField(default='header_pics/default.png', upload_to='header_pics')
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    # abbreviated state name
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)
    email = models.EmailField()
    file = models.FileField(default='verification_files/default.pdf', upload_to='verification_files',
                            validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
                            verbose_name="Verification Pdf")

    def __str__(self):
        return self.name

    # resize images
    def save(self, *args, **kwargs):
        super(Organization, self).save(*args, **kwargs)

        logo = Image.open(self.logo.path)
        header = Image.open(self.header.path)

        if logo.height > 300 or logo.width > 300:
            output_size = (300, 300)
            logo.thumbnail(output_size)
            logo.save(self.logo.path)
        if header.height > 350 or header.width > 1110:
            new_header = header.resize((1110, 350), Image.ANTIALIAS)
            new_header.save(self.header.path)


class Category(models.Model):
    category = (
        ('food', 'Food'),
        ('clothes', 'Clothes'),
        ('toiletries', 'Toiletries'),
        ('toys', 'Toys'),
        ('money', 'Money')
    )
    name = models.CharField(max_length=50, choices=category, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Drive(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    orgID = models.ForeignKey(Organization, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    # abbreviated state name
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)
    banner = models.ImageField(default='banner_pics/default.jpg', upload_to='banner_pics')
    progress = models.IntegerField(default=1,
                                   validators=[MaxValueValidator(100, 'Integer value must be between 1 and 100'),
                                               MinValueValidator(1, 'Integer value must be between 1 and 100')])
    category = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('drive-detail', kwargs={'pk': self.pk})

    # resize images
    def save(self, *args, **kwargs):
        super(Drive, self).save(*args, **kwargs)

        banner = Image.open(self.banner.path)

        if banner.height > 350 or banner.width > 1110:
            new_banner = banner.resize((1110, 350), Image.ANTIALIAS)
            new_banner.save(self.banner.path)



    # Check to see if the drive is expired
    @property
    def is_expired(self):
        if timezone.now() > self.end_date:
            return True
        else:
            return False

    # time left before expiration
    @property
    def time_left(self):
        if timezone.now() < self.end_date:
            return self.end_date - timezone.now()
        else:
            return 0


class Donation(models.Model):
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)


class DonationItem(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Notifications(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    date_posted = models.DateTimeField(default=timezone.now)
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE)