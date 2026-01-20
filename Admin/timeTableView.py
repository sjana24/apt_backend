from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import TimetableSlot
from .timeTableSerializers import (
    TimetableSlotGetSerializer,
    TimetableSlotWriteSerializer
)

class TimetableSlotListCreateAPIView(APIView):

    def get(self, request):
        slots = TimetableSlot.objects.all()
        serializer = TimetableSlotGetSerializer(slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TimetableSlotWriteSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TimetableSlotDetailAPIView(APIView):

    def get(self, request, pk):
        slot = get_object_or_404(TimetableSlot, pk=pk)
        serializer = TimetableSlotGetSerializer(slot)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        slot = get_object_or_404(TimetableSlot, pk=pk)
        serializer = TimetableSlotWriteSerializer(
            slot,
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        slot = get_object_or_404(TimetableSlot, pk=pk)
        slot.delete()
        return Response(
            {"message": "Timetable slot deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
