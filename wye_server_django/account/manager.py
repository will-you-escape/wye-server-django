from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class WYEUserManager(BaseUserManager):

    def create_user(self, email, pseudo, password=None):
        if not email:
            raise ValueError('Email must be set!')
        if not pseudo:
            raise ValueError('Pseudo must be set!')
        user = self.model(email=email, pseudo=pseudo)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, pseudo, password):
        user = self.create_user(email, pseudo, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email):
        return self.get(email=email)
