from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone


class Command(BaseCommand):
    help = "Создаёт демо-пользователей (admin/manager/employee) для быстрого старта."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Пересоздать пользователей и сбросить им пароли.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        force = options["force"]

        # ensure at least one org/department exists (optional for demo)
        Organization = User._meta.get_field("organization").remote_field.model
        Department = User._meta.get_field("department").remote_field.model

        org, _ = Organization.objects.get_or_create(name="SmartSheet Demo", defaults={"description": "Demo org"})
        dep, _ = Department.objects.get_or_create(name="Отдел продаж", organization=org)

        demo_users = [
            ("admin", "admin12345", "admin", True, True, 90),
            ("manager", "manager12345", "head", False, False, 80),
        ]

        for username, password, role, is_staff, is_superuser, rating in demo_users:
            user = User.objects.filter(username=username).first()
            if user and not force:
                continue
            if not user:
                user = User.objects.create_user(username=username, password=password, role=role)
            else:
                user.role = role
                user.set_password(password)

            # Для админки Django нужен is_staff=True
            user.is_staff = is_staff or is_superuser
            user.is_superuser = is_superuser
            user.is_active = True
            user.rating = rating
            user.organization = org
            user.department = dep
            user.save()

        # Employees with ratings (demo leaderboard)
        employees = [
            ("employee", "employee12345", 70, "Дмитрий", "Трубачев"),
            ("olga", "olga12345", 95, "Ольга", "Смирнова"),
            ("ivan", "ivan12345", 88, "Иван", "Петров"),
            ("anna", "anna12345", 82, "Анна", "Кузнецова"),
            ("sergey", "sergey12345", 78, "Сергей", "Иванов"),
            ("nikita", "nikita12345", 60, "Никита", "Соколов"),
            ("polina", "polina12345", 55, "Полина", "Попова"),
        ]

        for username, password, rating, first_name, last_name in employees:
            user = User.objects.filter(username=username).first()
            if user and not force:
                continue
            if not user:
                user = User.objects.create_user(username=username, password=password, role=User.RoleChoices.EMPLOYEE)
            else:
                user.role = User.RoleChoices.EMPLOYEE
                user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.rating = rating
            user.organization = org
            user.department = dep
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.save()

        # Seed some daily workloads for April 2026 (so Optimize is visible immediately)
        from schedule.models import DailyWorkloadRequirement
        from schedule.models import ShiftChangeRequest
        if force:
            DailyWorkloadRequirement.objects.all().delete()
            ShiftChangeRequest.objects.all().delete()

        demo_workloads = [
            ("2026-04-10", "08:00", "12:00", 2),
            ("2026-04-10", "12:30", "16:00", 3),
            ("2026-04-10", "16:00", "20:00", 4),
            ("2026-04-11", "08:00", "12:00", 1),
            ("2026-04-11", "12:30", "16:00", 2),
            ("2026-04-12", "16:00", "20:00", 3),
        ]

        for d, start, end, required in demo_workloads:
            obj, _ = DailyWorkloadRequirement.objects.get_or_create(
                date=d,
                start_time=start,
                end_time=end,
                defaults={"required": required},
            )
            if force:
                obj.required = required
                obj.save()

        # Seed one open change request
        employee_user = User.objects.filter(username="employee").first()
        if employee_user:
            ShiftChangeRequest.objects.get_or_create(
                employee=employee_user,
                date="2026-04-11",
                defaults={"message": "Не могу работать в пятницу, нужна замена.", "status": "open"},
            )

        self.stdout.write(self.style.SUCCESS("Demo users ensured."))
