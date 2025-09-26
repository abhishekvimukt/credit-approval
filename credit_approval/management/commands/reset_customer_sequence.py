from django.core.management.base import BaseCommand
from django.db import connection
from credit_approval.models import Customer

class Command(BaseCommand):
    help = 'Resets the customer_id sequence in PostgreSQL based on the maximum existing customer_id.'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Find the maximum customer_id currently in the table
            cursor.execute("SELECT MAX(customer_id) FROM credit_approval_customer;")
            max_id = cursor.fetchone()[0]

            if max_id is not None:
                # Reset the sequence to max_id + 1
                new_sequence_value = max_id + 1
                # The sequence name typically follows the pattern: appname_modelname_id_seq
                cursor.execute(f"ALTER SEQUENCE credit_approval_customer_customer_id_seq RESTART WITH {new_sequence_value};")
                self.stdout.write(self.style.SUCCESS(f'Successfully reset customer_id sequence to {new_sequence_value}.'))
            else:
                self.stdout.write(self.style.WARNING('No customers found, sequence not reset.'))
