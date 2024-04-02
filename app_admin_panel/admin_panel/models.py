from django.db import models


class StatusType(models.TextChoices):
    agency = 'agency', 'agency'
    manager = 'manager', 'manager'
    bloger = 'bloger', 'bloger'
    buyer = 'buyer', 'buyer'


class User(models.Model):
    class Meta:
        db_table = 'users'
        ordering = ['created_at']
        verbose_name = 'Пользователи'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    inst_username = models.CharField(max_length=32, null=True, blank=True)
    status = models.CharField(max_length=32, choices=StatusType, null=True, blank=True)
    link = models.CharField(max_length=64, null=True, blank=True)

    manager = models.ForeignKey('User', on_delete=models.CASCADE, related_name='to_manager', null=True, blank=True)
    agency = models.ForeignKey('User', on_delete=models.CASCADE, related_name='to_agency', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'


class Advertisement(models.Model):
    class Meta:
        db_table = 'advertisements'
        ordering = ['id']
        verbose_name = 'Рекламы'
        verbose_name_plural = verbose_name


    id = models.AutoField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    photo_file_id = models.CharField(max_length=256, blank=True, null=True)
    video_file_id = models.CharField(max_length=256, blank=True, null=True)
    document_file_id = models.CharField(max_length=256, blank=True, null=True)

    is_approved_by_bloger = models.BooleanField(default=False, blank=True)
    is_approved_by_manager = models.BooleanField(default=False, blank=True)
    is_approved_by_buyer = models.BooleanField(default=False, blank=True)  # dialog after the paid reklams

    is_paid = models.BooleanField(default=False, blank=True)

    agency = models.ForeignKey('User', on_delete=models.CASCADE, related_name='agencies', null=True, blank=True)
    manager = models.ForeignKey('User', on_delete=models.CASCADE, related_name='managers', null=True, blank=True)
    bloger = models.ForeignKey('User', on_delete=models.CASCADE, related_name='blogers', null=True, blank=True)
    buyer = models.ForeignKey('User', on_delete=models.CASCADE, related_name='buyers', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'


class Dispatcher(models.Model):
    class Meta:
        db_table = 'mailings'
        ordering = ['id']
        verbose_name = 'Рассылки'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True)
    post = models.ForeignKey('Post', to_field='id', on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=StatusType, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    send_at = models.DateTimeField()

    def __str__(self):
        return f'{self.id}'


class Post(models.Model):
    class Meta:
        db_table = 'static_content'
        ordering = ['id']
        verbose_name = 'Контент для рассылок'
        verbose_name_plural = verbose_name

    id = models.BigIntegerField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    photo_file_id = models.CharField(max_length=256, blank=True, null=True)
    video_file_id = models.CharField(max_length=256, blank=True, null=True)
    video_note_id = models.CharField(max_length=256, blank=True, null=True)
    document_file_id = models.CharField(max_length=256, blank=True, null=True)
    sticker_file_id = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'
