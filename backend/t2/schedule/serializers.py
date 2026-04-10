from rest_framework import serializers

from .models import DailyWorkloadRequirement, Shift, ShiftChangeRequest, WorkloadRequirement


class ShiftSerializer(serializers.ModelSerializer):
    employee_username = serializers.CharField(source="employee.username", read_only=True)

    class Meta:
        model = Shift
        fields = [
            "id",
            "employee",
            "employee_username",
            "date",
            "start_time",
            "end_time",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "employee": {"required": False},
        }

    def create(self, validated_data):
        instance = Shift(**validated_data)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class WorkloadRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkloadRequirement
        fields = [
            "id",
            "weekday",
            "start_time",
            "end_time",
            "required",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        instance = WorkloadRequirement(**validated_data)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class DailyWorkloadRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyWorkloadRequirement
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "required",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        instance = DailyWorkloadRequirement(**validated_data)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class ShiftChangeRequestSerializer(serializers.ModelSerializer):
    employee_username = serializers.CharField(source="employee.username", read_only=True)

    class Meta:
        model = ShiftChangeRequest
        fields = [
            "id",
            "employee",
            "employee_username",
            "date",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "employee", "status"]

    def create(self, validated_data):
        instance = ShiftChangeRequest(**validated_data)
        instance.full_clean()
        instance.save()
        return instance


class ShiftChangeRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftChangeRequest
        fields = ["status"]

    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.full_clean()
        instance.save()
        return instance
