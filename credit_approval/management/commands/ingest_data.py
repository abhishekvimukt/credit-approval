from django.core.management.base import BaseCommand
from credit_approval.tasks import ingest_customer_data, ingest_loan_data

class Command(BaseCommand):
    help = 'Ingests initial customer and loan data from Excel files using Celery tasks.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))
        
        # Enqueue customer data ingestion task
        customer_task = ingest_customer_data.delay()
        self.stdout.write(self.style.SUCCESS(f'Customer data ingestion task enqueued (ID: {customer_task.id}).'))

        # Enqueue loan data ingestion task
        loan_task = ingest_loan_data.delay()
        self.stdout.write(self.style.SUCCESS(f'Loan data ingestion task enqueued (ID: {loan_task.id}).'))

        self.stdout.write(self.style.SUCCESS('Data ingestion tasks enqueued. Check Celery worker logs for progress.'))
