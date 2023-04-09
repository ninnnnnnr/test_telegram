import os
from django.core.files import File
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import UserManager
from urllib import request


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('User name', max_length=100, unique=True)
    password = models.CharField('User password', max_length=100)
    email = models.CharField('User email', max_length=100, unique=True)
    user_nickname = models.CharField('User nickname', blank=True, max_length=100, null=True)
    user_photo = models.ImageField('Photo', upload_to=f'uploads/{username}', blank=True, null=True)
    user_phone = models.CharField('Phone number', blank=True, max_length=100, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image_url = models.URLField('url_img', blank=True, null=True)


    def get_remote_image(self):
        if self.image_url and not self.user_photo:
            result = request.urlretrieve(str(self.image_url))
            self.user_photo.save(
                os.path.basename(self.image_url),
                File(open(result[0], 'rb'))
            )
            self.save()

    def __str__(self):
        return self.username

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = ('TG_User')
        verbose_name_plural = ('TG_Users')

