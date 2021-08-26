from django.shortcuts import get_object_or_404
from rest_framework import filters, generics
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class ListClinic(ListAPIView):
    '''
        Get all active clinics
    '''
    permission_classes = [IsAuthenticated, ]
    queryset = Clinic.objects.filter(is_active=True)
    serializer_class = ClinicListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ClinicView(APIView):
    '''
        Clinic view class
    '''
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        now = datetime.now()
        params = request.query_params
        if params.get('ordering') == 'past':
            queryset = Reservation.objects.filter(clinic=kwargs['id'], time__lt=now)
        elif params.get('ordering') == 'upcoming':
            queryset = Reservation.objects.filter(clinic=kwargs['id'], time__gte=now)
        else:
            queryset = Reservation.objects.filter(clinic=kwargs['id'])
        serializer = ClinicReservationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Edit clinic
    def put(self, request, *args, **kwargs):
        clinic = get_object_or_404(Clinic, pk=kwargs['id'])
        serializer = ClinicSerializer(clinic, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete clinic
    def delete(self, request, *args, **kwargs):
        clinic = get_object_or_404(Clinic, pk=kwargs['id'])
        clinic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientView(APIView):
    '''
        Patient view class
    '''
    permission_classes = [IsAuthenticated, ]

    # Get patient's reservations
    def get(self, request, *args, **kwargs):
        now = datetime.now()
        params = request.query_params
        if params.get('ordering') == 'past':
            queryset = Reservation.objects.filter(patient=kwargs['id'], time__lt=now)
        elif params.get('ordering') == 'upcoming':
            queryset = Reservation.objects.filter(patient=kwargs['id'], time__gte=now)
        else:
            queryset = Reservation.objects.filter(patient=kwargs['id'])
        serializer = PatientReservationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Edit patient
    def put(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, pk=kwargs['id'])
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete patient
    def delete(self, request, *args, **kwargs):
        patient = get_object_or_404(Clinic, pk=kwargs['id'])
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservationView(APIView):
    '''
        Reservation view class
    '''
    permission_classes = [IsAuthenticated, ]

    # Create reservation for patient
    def post(self, request, *args, **kwargs):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            reservation = serializer.save(patient=kwargs['patient_id'])
            return Response(reservation.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterDoctorAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    # Create clinic
    def post(self, request):
        serializer = ClinicSerializer(data=request.data)
        if serializer.is_valid():
            clinic = serializer.save()
            return Response(clinic.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterPatientAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    # Create patient
    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            return Response(patient.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
