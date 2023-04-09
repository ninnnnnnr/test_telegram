from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email, password, user_nickname=None, image_url=None, user_phone=None):
        user = self.model(
            username=username,
            email=email,
            password=password,
            user_nickname=user_nickname,
            image_url=image_url,
            user_phone=user_phone
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email):
        user = self.create_user(
            username=username,
            password=password,
            email=email
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user