from pysolar.solar import get_altitude
from pysolar.radiation import get_radiation_direct
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from smarthome.inbound.models import Entry

class Command(BaseCommand):
    help = 'Collects weather data and stores it'

    def handle(self, *args, **options):
        sun_altitude = get_altitude(51.462246, -0.182502, timezone.now())
        radiation = get_radiation_direct(timezone.now(), sun_altitude)

        fields = {
            'sun_altitude': sun_altitude,
            'sun_clearsky_radiation': radiation
        }

        entries = []
        for field, value in fields.items():
            if value is None:
                continue

            entries.append(Entry(
                source = 'solar',
                field = field,
                value = value
            ))

        Entry.objects.bulk_create(entries)

        self.stdout.write(self.style.SUCCESS(f"Successfully calculated solar data"))
