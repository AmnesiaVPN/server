from typing import Iterable

from celery import Task as CeleryTask
from celery.result import AsyncResult
from django.db import transaction

from telegram_bot.models import User, ScheduledTask
from telegram_bot.selectors import get_previously_scheduled_tasks


@transaction.atomic
def remove_previously_scheduled_tasks(*, user: User | int):
    previously_scheduled_tasks = get_previously_scheduled_tasks(user=user)
    for task in previously_scheduled_tasks:
        AsyncResult(str(task.uuid)).revoke()
    previously_scheduled_tasks.delete()


def create_new_scheduled_tasks(*, user: User | int, tasks: Iterable[CeleryTask]):
    scheduled_tasks = [ScheduledTask(user_id=user, uuid=task.task_id) for task in tasks]
    ScheduledTask.objects.bulk_create(scheduled_tasks)
