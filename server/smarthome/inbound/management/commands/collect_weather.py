import os
import requests
from django.core.management.base import BaseCommand, CommandError
from smarthome.inbound.models import Entry

class Command(BaseCommand):
    help = 'Collects weather data and stores it'

    def handle(self, *args, **options):
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat=51.462254&appid={os.environ['OPENWEATHERMAP_API_KEY']}&lon=-0.182535&units=metric")
        weather = response.json()

        fields = {
            'ambient_temp': weather.get('main', {}).get('temp', None),
            'ambient_temp_feels_like': weather.get('main', {}).get('feels_like', None),
            'ambient_pressure': weather.get('main', {}).get('pressure', None),
            'ambient_humidity': weather.get('main', {}).get('humidity', None),
            'visibility': weather.get('visibility', None),
            'wind_speed': weather.get('wind', {}).get('speed', None),
            'wind_deg': weather.get('wind', {}).get('deg', None),
            'wind_gust': weather.get('wind', {}).get('gust', None),
            'clouds': weather.get('clouds', {}).get('all', None),
            'rain': weather.get('rain', {}).get('1h', 0),
            'snow': weather.get('snow', {}).get('1h', 0)
        }

        entries = []
        for field, value in fields.items():
            if value is None:
                continue

            entries.append(Entry(
                source = 'weather',
                field = field,
                value = value
            ))

        Entry.objects.bulk_create(entries)

        self.stdout.write(self.style.SUCCESS(f"Successfully pulled weather data"))
