from django.core.exceptions import ValidationError
from django.db import models

from client.sender import send_media_group


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        db_table = 'timestamp'


# Create your models here.
class Client_Settings(TimeStamp):
    api_id = models.CharField(max_length=100)
    api_hash = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    session = models.FileField(upload_to='./', null=True, blank=True)

    def __str__(self):
        return self.phone

    class Meta:
        db_table = 'client_settings'

    def save(self, *args, **kwargs):
        self.session.name = str(self.phone) + '.session'


class Bot(TimeStamp):
    bot_name = models.CharField(max_length=100)
    bot_token = models.CharField(max_length=100)
    bot_link = models.CharField(max_length=100)

    def __str__(self):
        return self.bot_name

    class Meta:
        db_table = 'bot'


class Channels(TimeStamp):
    channel_name = models.CharField(max_length=250)
    channel_link = models.CharField(max_length=250)
    channel_id = models.CharField(max_length=100)
    my_channel = models.BooleanField(default=False)

    def __str__(self):
        return self.channel_name

    class Meta:
        db_table = 'channels'
        unique_together = ('channel_id', 'my_channel')

    def save(self, *args, **kwargs):
        # Check if channel_id doesn't already start with "-100"
        if not self.channel_id.startswith('-100'):
            self.channel_id = '-100' + self.channel_id
        super().save(*args, **kwargs)

    def clean(self):
        # check exist channel_id
        if Channels.objects.filter(channel_id=self.channel_id).exists():
            raise ValidationError('This channel_id already exists')


class KeywordChannelAds(TimeStamp):
    text = models.TextField()
    channel = models.ForeignKey(Channels, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'keywordchannelads'

    def clean(self):
        if self.channel.my_channel == True and KeywordChannelAds.objects.filter(channel=self.channel).exists():
            raise ValidationError('This channel already has keyword')


class Channel_config(TimeStamp):
    title = models.CharField(max_length=100)
    from_channel = models.ForeignKey(Channels, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='from_channel_configs')
    to_channel = models.ForeignKey(Channels, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='to_channel_configs')
    bot = models.ForeignKey(Bot, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'channel_config'
        unique_together = ('from_channel', 'to_channel')

    def clean(self):
        if self.from_channel.my_channel == True:
            raise ValidationError('This channel is my channel')
        if self.to_channel.my_channel == False:
            raise ValidationError('This channel is not my channel')


class Filename(TimeStamp):
    message_id = models.CharField(max_length=50)
    filename = models.CharField(max_length=100)
    is_caption = models.BooleanField(default=False)
    is_photo = models.BooleanField(default=False)

    def __str__(self):
        return self.filename

    class Meta:
        db_table = 'filename'


class Message(TimeStamp):
    message_id = models.CharField(max_length=500, unique=True)
    caption = models.BooleanField(default=False)
    photo = models.BooleanField(default=False)
    channel_from = models.CharField(max_length=100)
    delete_status = models.BooleanField(default=True)
    single_photo = models.BooleanField(default=False)
    send_status = models.BooleanField(default=False)
    photo_count = models.IntegerField(default=0)
    end = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if both caption and photo are True
        if self.caption and self.photo:
            self.delete_status = False
        else:
            self.delete_status = True
        if self.photo_count > 1:
            self.single_photo = False
        if self.photo_count == 1:
            self.single_photo = True

        if self.end == True  and self.delete_status == False:
            send_media_group(self.message_id)
            if send_media_group:
                self.send_status = True




        super().save(*args, **kwargs)

    def __str__(self):
        return self.message_id

    class Meta:
        db_table = 'message'
