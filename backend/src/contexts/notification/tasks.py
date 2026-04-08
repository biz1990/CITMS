from celery import shared_task
from backend.src.infrastructure.database import AsyncSessionLocal
from backend.src.contexts.notification.services.notifier import NotificationService
from backend.src.infrastructure.redis import redis_client
import asyncio
import smtplib
import json
from email.mime.text import MIMEText
from backend.src.core.config import settings

@shared_task(name="notification.process_event")
def process_notification_task(event: dict):
    """Process an event and send notifications asynchronously."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_process_notif(event))

async def _async_process_notif(event: dict):
    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        await service.process_event(event)

from celery.signals import worker_ready

@shared_task(name="notification.event_stream_consumer")
def event_stream_consumer_task():
    """Celery task that runs a loop to consume events from Redis Streams."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_stream_consumer())

@worker_ready.connect
def at_start(sender, **kwargs):
    """Start the consumer task when the worker is ready."""
    # Only start if this is the dedicated events worker
    if sender.hostname.startswith("events@"):
        print("Starting Event Stream Consumer Task...")
        event_stream_consumer_task.delay()

async def _async_stream_consumer():
    """Listen to all CITMS event streams using Consumer Groups and dispatch to NotificationService."""
    group_name = "citms_notification_group"
    consumer_name = f"consumer_{settings.PROJECT_NAME.lower()}"
    
    streams = [
        "citms:license:events",
        "citms:inventory:events",
        "citms:itsm:events",
        "citms:procurement:events",
        "citms:workflow:events",
        "citms:security:events",
        "citms:general:events"
    ]
    
    # 1. Ensure Consumer Groups exist for all streams
    for stream in streams:
        try:
            await redis_client.xgroup_create(stream, group_name, id="0", mkstream=True)
            print(f"Created consumer group {group_name} for stream {stream}")
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                print(f"Error creating group for {stream}: {str(e)}")

    print(f"Starting Redis Stream Consumer Group {group_name} for {streams}")
    
    while True:
        try:
            # 2. Read from all streams using XREADGROUP
            # We read from ">" (new messages) and also handle pending messages if needed
            # For simplicity in this remediation, we focus on new messages and at-least-once
            response = await redis_client.xreadgroup(
                groupname=group_name,
                consumername=consumer_name,
                streams={s: ">" for s in streams},
                count=10,
                block=5000
            )
            
            if response:
                for stream_name, messages in response:
                    for message_id, message_data in messages:
                        try:
                            # 3. Process the event
                            await _async_process_notif(message_data)
                            
                            # 4. Acknowledge the message (XACK)
                            await redis_client.xack(stream_name, group_name, message_id)
                            
                        except Exception as proc_err:
                            print(f"Error processing message {message_id} from {stream_name}: {str(proc_err)}")
                            # Message remains in PEL (Pending Entries List) for retry
                            
            # 5. Periodically check for pending messages (Optional but recommended for At-least-once)
            # In a production app, we would use XPENDING and XCLAIM here.
            
        except Exception as e:
            print(f"Error in Event Stream Consumer: {str(e)}")
            await asyncio.sleep(5) # Wait before retrying

@shared_task(name="notification.send_email")
def send_email_task(to_email: str, subject: str, body: str):
    """Send an email using SMTP."""
    # In real app, use settings.SMTP_SERVER, settings.SMTP_USER, etc.
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_FROM
    msg['To'] = to_email
    
    # Simulation: print to console or use mock SMTP
    print(f"Sending email to {to_email}: {subject}")
    # with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
    #     server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    #     server.send_message(msg)

@shared_task(name="notification.cleanup_streams")
def cleanup_redis_streams_task(max_len: int = 1000):
    """Trim Redis Streams to a maximum length."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_cleanup_streams(max_len))

async def _async_cleanup_streams(max_len: int):
    streams = [
        "citms:license:events",
        "citms:inventory:events",
        "citms:itsm:events",
        "citms:procurement:events",
        "citms:workflow:events",
        "citms:security:events",
        "citms:general:events"
    ]
    
    print(f"Trimming Redis Streams to max length {max_len}")
    for stream in streams:
        try:
            # XTRIM stream MAXLEN ~ max_len
            await redis_client.xtrim(stream, maxlen=max_len, approximate=True)
        except Exception as e:
            print(f"Error trimming stream {stream}: {str(e)}")
