"""Notifier — simulated notification delivery (console log)."""

import structlog

logger = structlog.get_logger()


async def send_notification(
    user_id: str,
    task_id: int,
    title: str,
    message: str,
) -> None:
    """Simulate sending a notification (email/push/SMS).

    In production, this would integrate with an email provider,
    push notification service, or SMS gateway.
    """
    logger.info(
        "NOTIFICATION_SENT",
        user_id=user_id,
        task_id=task_id,
        title=title,
        message=message,
        channel="console",
    )
