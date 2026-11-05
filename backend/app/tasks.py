from app.celery import celery


@celery.task(bind=True, max_retries=5, default_retry_delay=300)
def retry_monthly_debit(self, transaction_id: int) -> dict[str, object]:
    raise NotImplementedError(
        f"Payment gateway debit adapter is not enabled for transaction {transaction_id}"
    )


@celery.task
def send_payment_reminder(tenant_id: int, message: str) -> dict[str, object]:
    raise NotImplementedError(
        f"SMS provider is not configured for tenant {tenant_id}; message was not sent"
    )
