"""Arquivo padrão do django com a model User modificada conforme a modelagem"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager for users."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("Users must have an email address.")

        # Provide defaults for non-nullable fields so manager can be used
        extra_fields.setdefault('data_nascimento', '2000-01-01')
        extra_fields.setdefault('genero', 'O')
        extra_fields.setdefault('altura_cm', 170)
        extra_fields.setdefault('peso_kg', 70)

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    
    def create_superuser(self, email, password, **extra_fields):
        """Create, save and return a new superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # cpf removed from model; no longer needed
        extra_fields.setdefault('data_nascimento', '2000-01-01')
        extra_fields.setdefault('peso_kg', 70)
        extra_fields.setdefault('altura_cm', 170)
        extra_fields.setdefault('genero', 'O')  # Mudei de 'Outro' para 'O'
    
        user = self.create_user(email, password, **extra_fields)
        user.save(using=self._db)
    
        return user


class User(AbstractBaseUser, PermissionsMixin):
    GENERO_CHOICES = [
        ("M", "Masculino"),
        ("F", "Feminino"),
        ("O", "Outro"),
    ]

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("name"),
        help_text=_("Username"),
    )
    email = models.EmailField(
        max_length=255, unique=True, verbose_name=_("email"), help_text=_("Email")
    )
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    altura_cm = models.PositiveIntegerField()
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)
    objetivo = models.CharField(max_length=50, blank=True, null=True)
    meta_peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    dias_treino = models.CharField(max_length=255, blank=True, null=True)
    grupo_foco = models.CharField(max_length=255, blank=True, null=True)
    # profile_picture field removed as per request
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Usuário está ativo"),
        help_text=_("Indica que este usuário está ativo."),
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Usuário é da equipe"),
        help_text=_("Indica que este usuário pode acessar o Admin."),
    )
    passage_id = models.CharField(
    max_length=255,
    unique=True,
    blank=True,  # ADICIONE ISSO
    null=True,   # ADICIONE ISSO
    verbose_name=_("passage_id"),
    help_text=_("Passage ID"),
)

    def __str__(self):
        return f"{self.name} - {self.email}"

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """Meta options for the model."""

        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
