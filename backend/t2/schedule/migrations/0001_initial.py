# Generated manually (no Django runtime in repo environment)
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Shift",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("status", models.CharField(choices=[("plan", "Plan"), ("fact", "Fact"), ("confirmed", "Confirmed")], default="plan", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("employee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shifts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-date", "start_time"],
            },
        ),
        migrations.AddIndex(
            model_name="shift",
            index=models.Index(fields=["employee", "date"], name="shift_employee_date_idx"),
        ),
    ]
