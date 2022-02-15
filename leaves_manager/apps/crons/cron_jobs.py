from datetime import datetime, timedelta

from leaves_manager.apps.core.db_utils import get_query_set
from leaves_manager.apps.leaves.models import TimeOffRequest
from leaves_manager.apps.organization.models import Organization, SlackIntegration
from leaves_manager.integrations.slack import SlackCentral


def format_emp_block(time_off):
    name = f"{time_off.employee.last_name} {time_off.employee.first_name}"
    from_date = time_off.from_date
    to_date = time_off.to_date
    days = (to_date - from_date).days
    from_str = from_date.strftime("%A, %B %d, %Y")
    to_str = to_date.strftime("%A, %B %d, %Y")
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f":ninja: *{name}*\n Starting: {from_str} \n Ending: {to_str} \n Days: {days}"
        }
    },
        {
            "type": "divider",
        }]


def prepare_slack_message(weeks_time_off_requests, org):
    if weeks_time_off_requests.count() < 1:
        return
    else:
        blocks = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hello <!here> *The following employees will be out this week*"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }
        for time_off in weeks_time_off_requests:
            dc = format_emp_block(time_off)
            blocks["blocks"].extend(dc)
        slack_instance = SlackIntegration.objects.filter(organization=org).first()
        access_token, channel_id = slack_instance.access_token, slack_instance.channel_id
        sc = SlackCentral(access_token)
        sc.post_to_channel(channel=channel_id, message="Hello :wave:", blocks=blocks["blocks"])


def notify_weekly():
    present_date = datetime.now()
    mon = present_date - timedelta(days=present_date.weekday())
    mon_midnight = datetime(mon.year, mon.month, mon.day, 0, 0)
    saturday_midnight = present_date + timedelta(days=5)
    organizations = Organization.objects.filter(slack_integrated=True)
    for org in organizations:
        weeks_time_off_requests = get_query_set(TimeOffRequest, org, distinct_qs='employee').filter(
            status='AP',
            to_date__gte=mon_midnight,
            to_date__lte=saturday_midnight)
        prepare_slack_message(weeks_time_off_requests, org)
