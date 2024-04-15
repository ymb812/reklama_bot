import logging
from datetime import datetime
from tortoise import fields
from tortoise.models import Model
from enum import Enum

logger = logging.getLogger(__name__)


class StatusType(Enum):
    agency = 'agency'
    manager = 'manager'
    bloger = 'bloger'
    buyer = 'buyer'


class User(Model):
    class Meta:
        table = 'users'
        ordering = ['created_at']

    id = fields.BigIntField(pk=True, index=True)
    user_id = fields.BigIntField(unique=True, null=True)
    username = fields.CharField(max_length=32, null=True)
    inst_username = fields.CharField(max_length=32, null=True)
    status = fields.CharEnumField(enum_type=StatusType, max_length=64, null=True)
    link = fields.CharField(max_length=64, unique=True, null=True)
    is_banned = fields.BooleanField(default=False)

    manager = fields.ForeignKeyField('models.User', to_field='id', related_name='to_manager', null=True)
    agency = fields.ForeignKeyField('models.User', to_field='id', related_name='to_agency', null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @classmethod
    async def update_data(cls, user_id: int, username: str, status: str):
        user = await cls.filter(user_id=user_id).first()
        if user is None:
            await cls.create(
                user_id=user_id,
                username=username,
                status=status,
            )
        else:
            await cls.filter(user_id=user_id).update(
                username=username,
                status=status,
                updated_at=datetime.now()
            )

    @classmethod
    async def set_status(cls, user_id: int, status: str | None):
        await cls.filter(user_id=user_id).update(status=status)


class Advertisement(Model):
    class Meta:
        table = 'advertisements'
        ordering = ['id']

    id = fields.BigIntField(pk=True)
    text = fields.TextField(null=True)
    photo_file_id = fields.CharField(max_length=256, null=True)
    video_file_id = fields.CharField(max_length=256, null=True)
    document_file_id = fields.CharField(max_length=256, null=True)

    is_approved_by_bloger = fields.BooleanField(default=False)
    is_rejected = fields.BooleanField(default=False)
    is_paid = fields.BooleanField(default=False)
    is_done = fields.BooleanField(default=False)

    agency = fields.ForeignKeyField('models.User', to_field='id', related_name='agencies', null=True)
    manager = fields.ForeignKeyField('models.User', to_field='id', related_name='managers', null=True)
    bloger = fields.ForeignKeyField('models.User', to_field='id', related_name='blogers', null=True)
    buyer = fields.ForeignKeyField('models.User', to_field='id', related_name='buyers', null=True)

    created_at = fields.DatetimeField(auto_now_add=True)


class UserStats(Model):
    class Meta:
        table = 'user_stats'
        ordering = ['id']

    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField('models.User', to_field='id', related_name='user_stats', null=True)
    video_file_id = fields.CharField(max_length=256, null=True)
    document_file_id = fields.CharField(max_length=256, null=True)


class Dispatcher(Model):
    class Meta:
        table = 'mailings'
        ordering = ['send_at']

    id = fields.BigIntField(pk=True)
    post = fields.ForeignKeyField('models.Post', to_field='id')
    status = fields.CharEnumField(enum_type=StatusType, max_length=64, null=True)
    user = fields.ForeignKeyField('models.User', to_field='id', null=True)
    send_at = fields.DatetimeField()


class Post(Model):
    class Meta:
        table = 'static_content'

    id = fields.BigIntField(pk=True)
    text = fields.TextField(null=True)
    photo_file_id = fields.CharField(max_length=256, null=True)
    video_file_id = fields.CharField(max_length=256, null=True)
    video_note_id = fields.CharField(max_length=256, null=True)
    document_file_id = fields.CharField(max_length=256, null=True)
    sticker_file_id = fields.CharField(max_length=256, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
