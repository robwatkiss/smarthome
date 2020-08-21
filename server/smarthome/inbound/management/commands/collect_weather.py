import requests
from django.db.models import Max
from django.core.management.base import BaseCommand, CommandError
from smarthome.inbound.models import Entry

class Command(BaseCommand):
    help = 'Collects weather data and stores it'

    def handle(self, *args, **options):
        response = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=51.462254&appid=6472b326579fd18de85118950380da91&lon=-0.182535&units=metric")
        weather = response.json()

        fields = {
            'ambient_temp': weather['main']['temp'],
            'ambient_temp_feels_like': weather['main']['feels_like'],
            'ambient_pressure': weather['main']['pressure'],
            'ambient_humidity': weather['main']['humidity'],
            'visibility': weather['visibility'],
            'wind_speed': weather['wind']['speed'],
            'wind_deg': weather['wind']['deg'],
            'wind_gust': weather['wind']['gust'],
            'clouds': weather['clouds']['all']
        }

        entries = []
        for field, value in fields.items():
            entries.append(Entry(
                source = 'weather',
                field = field,
                value = value
            ))

        Entry.objects.bulk_create(entries)

        self.stdout.write(self.style.SUCCESS(f"Successfully pulled weather data"))
