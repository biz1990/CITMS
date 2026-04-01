from celery.schedules import crontab
from app.core.celery_app import celery_app
from app.tasks import (
    notifications, reports, itsm, license, maintenance, auth
)

# Celery Beat Routing (Cron schedules) - Full Phase 4 Verified Schedule
celery_app.conf.beat_schedule = {
    "itsm_sla_escalation_every_5_mins": {
        "task": "itsm.check_escalation_rules_task",
        "schedule": crontab(minute="*/5")
    },
    "audit_license_violations_daily": {
        "task": "license.audit_violations_task",
        "schedule": crontab(hour=1, minute=0)
    },
    "enforce_password_rotation_daily": {
        "task": "maintenance.password_rotation_task",
        "schedule": crontab(hour=2, minute=0)
    },
    "cleanup_retained_data_weekly": {
        "task": "maintenance.data_cleanup_task",
        "schedule": crontab(day_of_week=0, hour=3, minute=0)
    },
    "monthly_reports_1st_day": {
        "task": "reports.generate_monthly_report_task",
        "schedule": crontab(day_of_month=1, hour=0, minute=0)
    },
    "ldap_ad_sync_daily": {
        "task": "auth.ldap_ad_sync_task",
        "schedule": crontab(hour=4, minute=0)
    },
    "create_next_month_partitions": {
        "task": "maintenance.maintain_partitions_task",
        "schedule": crontab(day_of_month="28", hour=5, minute=0)
    }
}
