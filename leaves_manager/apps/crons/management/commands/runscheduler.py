import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from leaves_manager.apps.crons.cron_jobs import notify_weekly

logger = logging.getLogger(__name__)


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job
    executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Weekly leave notifications
        scheduler.add_job(
            notify_weekly,
            trigger=CronTrigger(day_of_week="mon", hour=10),
            id="weekly_leaves_notification",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'weekly_leaves_notification'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
