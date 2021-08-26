from datetime import datetime

from rest_framework import serializers

from .models import Reservation, Clinic, Patient, Doctor, BaseUser
from .utils import tomorrow, before_or_after_delta
from .validators import phone_number
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

class ReservationSerializer(serializers.ModelSerializer):
    '''
        Reservation serializer class
    '''

    class Meta:
        model = Reservation
        fields = ('patient', 'clinic', 'time', 'description')
        extra_kwargs = {
            'patient': {'read_only': True},
            'time': {'read_only': True},
        }

    def create(self, validated_data):
        clinic_id = validated_data['clinic'].id
        patient = Patient.objects.get(pk=validated_data['patient'])
        now = datetime.now()
        try:
            last_reservation = Reservation.objects.filter(clinic=clinic_id).latest('time')
            clinic = Clinic.objects.get(id=clinic_id)
            clinic_start_time = clinic.start_time
            clinic_end_time = clinic.end_time

            # Today
            if last_reservation.time.date() == now.date():

                if last_reservation.time.hour == clinic_end_time:
                    time = tomorrow(clinic_start_time, last_reservation.time)

                elif last_reservation.time.hour >= now.hour:
                    time = before_or_after_delta(last_reservation.time)

                elif last_reservation.time.hour < now.hour:
                    time = before_or_after_delta(now)

            # Before Today
            elif last_reservation.time.date() < now.date():

                if now.hour == clinic_end_time:
                    time = tomorrow(clinic_start_time, now)

                else:
                    time = before_or_after_delta(now)

            # After Today
            elif last_reservation.time.date() > now.date():

                if last_reservation.time.hour == clinic_end_time:
                    time = tomorrow(clinic_start_time, last_reservation.time)

                else:
                    time = before_or_after_delta(last_reservation.time)

            reservation = Reservation.objects.create(
                patient=patient,
                clinic=validated_data['clinic'],
                description=validated_data.get('description'),
                time=time
            )

        except Reservation.DoesNotExist:

            if now.hour == clinic_end_time:
                time = tomorrow(clinic_start_time, now)
            else:
                time = before_or_after_delta(now)

            reservation = Reservation.objects.create(
                patient=patient,
                clinic=validated_data['clinic'],
                description=validated_data.get('description'),
                time=time
            )
        return reservation


class ClinicSerializer(serializers.ModelSerializer):
    '''
        Clinic Serializer class
    '''
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    date = serializers.DateField(required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)

    class Meta:
        model = Clinic

        fields = ('id', 'doctor', 'price', 'date', 'start_time', 'end_time', 'description', 'active',)
        read_only_fields = ('id',)

    def validate(self, data):
        now = datetime.now()

        if data["end_time"] < data["start_time"]:
            raise serializers.ValidationError("Start time must be earlier than end time.")
        elif data["date"] < now.date():
            raise serializers.ValidationError("Clinic Date is invalid.")

        return data

    def create(self, validated_data):
        clinic = Clinic(**validated_data)
        clinic.save()
        return clinic

    def update(self, instance, validated_data):
        for key, item in validated_data.items():
            setattr(instance, key, item)
        instance.save()
        return instance


class PatientSerializer(serializers.ModelSerializer):
    '''
        Patient Serializer class
    '''

    phone = serializers.CharField(validators=[phone_number])

    class Meta:
        model = Patient
        fields = ('email', 'password', 'name', 'phone')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'write_only': True},
        }

    def create(self, validated_data):
        patient = Patient(**validated_data)
        patient.set_password()
        patient.save()
        return patient

    def update(self, instance, validated_data):
        for key, item in validated_data.items():
            setattr(instance, key, item)
            if key == 'password':
                instance.set_password()
        instance.save()
        return instance


class DoctorSerializer(serializers.ModelSerializer):
    '''
        Doctor Serializer class
    '''

    phone = serializers.CharField(validators=[phone_number])

    class Meta:
        model = Doctor
        fields = ('email', 'password', 'name', 'phone')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'write_only': True},
        }

    def create(self, validated_data):
        doctor = Doctor(**validated_data)
        doctor.set_password()
        doctor.save()
        return doctor

    def update(self, instance, validated_data):
        for key, item in validated_data.items():
            setattr(instance, key, item)
            if key == 'password':
                instance.set_password()
        instance.save()
        return instance


class DoctorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('email', 'name', 'phone')


class PatientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('email', 'name', 'phone')


class ClinicDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ('doctor', 'price', 'date', 'start_time', 'end_time', 'description',)
        read_only_fields = fields


class ClinicListSerializer(serializers.ModelSerializer):
    doctor = DoctorDetailSerializer(read_only=True)

    class Meta:
        model = Clinic
        fields = ('id', 'doctor', 'name', 'price', 'date', 'start_time', 'end_time', 'is_active')
        read_only_fields = ('id', 'is_active')


class ClinicReservationSerializer(serializers.ModelSerializer):
    patient = PatientDetailSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ('id', 'patient', 'created_at', 'description', 'time')


class PatientReservationSerializer(serializers.ModelSerializer):
    clinic = ClinicDetailSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ('id', 'clinic', 'created_at', 'description', 'time',)


class UserLoginSerializer(serializers.ModelSerializer):
    """
    A serializer for user login.
    """
    email = serializers.EmailField()
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BaseUser
        fields = ['email', 'password', 'token']
        extra_kwargs = {"password": {'write_only': True}}

    def get_token(self, obj):
        user = BaseUser.objects.get(email=obj['email'])
        refresh = RefreshToken.for_user(user)
        response = {'refresh': str(refresh), 'access': str(
            refresh.access_token), }
        return response

    def validate(self, data):
        """
        Validate that entered email and password are correct.
        """
        user = authenticate(**data)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account is not active')
        return data