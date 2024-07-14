from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify


class CustomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(still_alive=True)


class AbstractBaseModel(models.Model):
    class Meta:
        abstract = True
        ordering = ['-created_at']

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f"{self.__class__.__name__} ({self.pk})"


class Person(AbstractBaseModel):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, null=True, blank=True, db_column='surname',
                                 db_comment='Информация о фамилии', verbose_name='Фамилия')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    age = models.PositiveSmallIntegerField(editable=False, validators=[MaxValueValidator(120)], null=True, blank=True,
                                           verbose_name='Возраст')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True, verbose_name='Фото профиля')
    still_alive = models.BooleanField(default=True, verbose_name='Жив')
    total_rating = models.FloatField(default=0.0, verbose_name='Общий рейтинг')

    objects = CustomManager()

    class Meta:
        db_table = 'person'
        db_table_comment = 'Эта таблица содержит записи о людях'
        get_latest_by = 'created_at'
        constraints = [
            models.UniqueConstraint(fields=['first_name', 'last_name'], name='unique_person_name')
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.full_name)
        super().save(*args, **kwargs)

    def clean(self):
        # Логика для валидации
        pass

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('person_detail', kwargs={'slug': self.slug})


class ProxyPerson(Person):
    class Meta:
        proxy = True
        ordering = ['-total_rating']

    def top_rating(self):
        return self.total_rating >= 90


class Address(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='address', verbose_name='Человек')
    address_line_1 = models.CharField(max_length=255, verbose_name='Адрес 1')
    address_line_2 = models.CharField(max_length=255, null=True, blank=True, verbose_name='Адрес 2')
    city = models.CharField(max_length=100, verbose_name='Город')
    country = models.CharField(max_length=100, verbose_name='Страна')
    postal_code = models.CharField(max_length=20, verbose_name='Почтовый индекс')

    def __str__(self):
        return f"{self.address_line_1}, {self.city}"


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название проекта')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    team_members = models.ManyToManyField(Person, related_name='projects', verbose_name='Участники команды')

    def __str__(self):
        return self.name


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, verbose_name='Название документа')
    file = models.FileField(upload_to='documents/', verbose_name='Файл')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents', verbose_name='Проект')

    def __str__(self):
        return self.title


class Invoice(AbstractBaseModel):
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    due_date = models.DateField(verbose_name='Срок оплаты')
    paid = models.BooleanField(default=False, verbose_name='Оплачено')

    def __str__(self):
        return f"Счёт {self.id} - {self.amount} USD"


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name='Счёт')
    date = models.DateField(verbose_name='Дата платежа')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
                                 verbose_name='Сумма')

    def __str__(self):
        return f"Платеж {self.id} - {self.amount} USD"
