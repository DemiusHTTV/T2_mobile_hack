from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Organization, Department

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание тестовых данных (организации, подразделения, пользователи)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Начало создания тестовых данных...'))

        # Создание организаций
        org1, _ = Organization.objects.get_or_create(
            name='ООО "ТестКомпания"',
            defaults={'description': 'Тестовая организация'}
        )
        self.stdout.write(f'  ✓ Организация: {org1}')

        # Создание подразделений
        dept1, _ = Department.objects.get_or_create(
            name='Отдел разработки',
            organization=org1
        )
        self.stdout.write(f'  ✓ Подразделение: {dept1}')

        dept2, _ = Department.objects.get_or_create(
            name='Отдел аналитики',
            organization=org1
        )
        self.stdout.write(f'  ✓ Подразделение: {dept2}')

        # Создание пользователей
        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='admin123',
                role=User.RoleChoices.ADMIN,
                organization=org1
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Admin: admin / admin123'))

        # Head
        if not User.objects.filter(username='head_dev').exists():
            head = User.objects.create_user(
                username='head_dev',
                email='head@test.com',
                password='head123',
                first_name='Иван',
                last_name='Руководитель',
                role=User.RoleChoices.HEAD,
                department=dept1,
                organization=org1
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Head: head_dev / head123'))

        # Employees
        employees_data = [
            ('employee1', 'Сотрудник1', 'employee1@test.com', dept1),
            ('employee2', 'Сотрудник2', 'employee2@test.com', dept1),
            ('employee3', 'Сотрудник3', 'employee3@test.com', dept2),
        ]

        for username, last_name, email, dept in employees_data:
            if not User.objects.filter(username=username).exists():
                emp = User.objects.create_user(
                    username=username,
                    email=email,
                    password='emp123',
                    first_name=username.capitalize(),
                    last_name=last_name,
                    role=User.RoleChoices.EMPLOYEE,
                    department=dept,
                    organization=org1
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Employee: {username} / emp123'))

        self.stdout.write(self.style.SUCCESS('\n✓ Тестовые данные успешно созданы!'))
        self.stdout.write(self.style.WARNING('\nУчетные данные:'))
        self.stdout.write('  Admin:     admin / admin123')
        self.stdout.write('  Head:      head_dev / head123')
        self.stdout.write('  Employee:  employee1 / emp123')
        self.stdout.write('  Employee:  employee2 / emp123')
        self.stdout.write('  Employee:  employee3 / emp123')
