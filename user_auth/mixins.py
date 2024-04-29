from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class OwnedModelMixin(models.Model):
    OWNER_FIELD: str

    def get_owner(self) -> AbstractBaseUser:
        return getattr(self, self.OWNER_FIELD)

    class Meta:
        abstract = True
