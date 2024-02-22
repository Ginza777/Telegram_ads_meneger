import os
from datetime import timedelta

from celery import shared_task, Celery
from django.db.models import Q
from django.utils import timezone

from client.models import Message, Filename
from log_info.models import SomeErrors
from log_info.views import message_log_view
from sender.log_chat import send_msg_log
from sender.sender_msg import send_message

app = Celery('task', broker='redis://localhost:6379/0')


def check_photo_caption_with_count(message_id):
    message = Message.objects.get(message_id=message_id)
    if message.photo_count > 0:
        photo_file = Filename.objects.filter(message_id=message_id, is_photo=True)
        caption_file = Filename.objects.filter(message_id=message_id, is_caption=True)
        if photo_file.count() == message.photo_count and caption_file.count() == 1:
            return True
        else:
            message_log_view(message,
                             f"check_photo_with_count error message_id={message_id} photo_file.count()={photo_file.count()} message.photo_count={message.photo_count} caption_file.count()={caption_file.count()}")
            SomeErrors.objects.create(title=f"check_photo_with_count error",
                                      error=f"message_id={message_id} photo_file.count()={photo_file.count()} message.photo_count={message.photo_count} caption_file.count()={caption_file.count()}")
            return False


def check_files_existence(message_id):
    # Fetch image and caption file paths from the database
    message = Message.objects.get(message_id=message_id)
    image_file_paths = Filename.objects.filter(message_id=message_id, is_photo=True).values_list('filename', flat=True)
    caption_file_paths = Filename.objects.filter(message_id=message_id, is_caption=True).values_list('filename',
                                                                                                     flat=True)

    # Check if all image files exist
    all_image_files_exist = all(os.path.exists(image_path) for image_path in image_file_paths)

    # Check if all caption files exist
    all_caption_files_exist = all(os.path.exists(caption_path) for caption_path in caption_file_paths)

    if not all_image_files_exist:
        missing_image = next((image_path for image_path in image_file_paths if not os.path.exists(image_path)), None)
        if missing_image:
            # ================[log start]================
            message_log_view(message,
                             f"check_files_existence: IF NOT ALL_IMAGE_FILES_EXIST: TRY: MISSING_IMAGE={missing_image}")
            # ================[log end]================

    if not all_caption_files_exist:
        missing_caption = next(
            (caption_path for caption_path in caption_file_paths if not os.path.exists(caption_path)), None)
        if missing_caption:
            # ================[log start]================
            message_log_view(message,
                             f"check_files_existence: IF NOT ALL_CAPTION_FILES_EXIST: TRY: MISSING_CAPTION={missing_caption}")

            # ================[log end]================

    if all_image_files_exist and all_caption_files_exist:
        message.end = True
        message.save()
        return True

    return False


@shared_task
def send_message_task():
    messages = Message.objects.filter(
        send_status=False,
        delete_status=False,
        channel_from__isnull=False  # Filter qo'shildi
    )
    for message in messages:
        if check_photo_caption_with_count(message_id=message.message_id):
            if check_files_existence(message_id=message.message_id):
                send_message(message_id=message.message_id)


@shared_task(name='delete_message')
def delete_message():
    # Bugungi sana olish
    today = timezone.now()

    txt = f"delete_message: today={today}\n"
    txt_not = ''
    # Bir kun oldingi sana
    one_day_ago = today - timedelta(days=1)
    # Send_status=True yoki Delete_status=True va updated_at oldingi sana
    messages = Message.objects.filter(Q(send_status=True) | Q(delete_status=True), updated_at__lt=one_day_ago)
    for message_id in messages.values_list('message_id', flat=True):
        folder_name = f"media/{message_id}"
        if os.path.exists(folder_name):
            os.rmdir(folder_name)
            txt += f"EXISTS    = {message_id}\n"
        else:
            txt_not += f"NOTEXISTS = {message_id}\n"
    txt += txt_not
    txt += f"delete_message count: {messages.count()}\n"
    send_msg_log(txt)
