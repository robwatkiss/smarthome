from .models import Entry

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def record(request):
    source = request.data.get('source')
    fields = request.data.get('fields', {})

    entries = []
    for field, value in fields.items():
        entries.append(Entry(
            source = source,
            field = field,
            value = value
        ))

    Entry.objects.bulk_create(entries)
    return Response(status=status.HTTP_201_CREATED)