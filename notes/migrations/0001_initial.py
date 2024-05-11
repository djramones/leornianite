import django.utils.timezone
from django.db import migrations, models

import notes.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        default=notes.utils.generate_reference_code,
                        editable=False,
                        max_length=9,
                        unique=True,
                    ),
                ),
                ("text", models.TextField()),
                ("promoted", models.BooleanField(default=False)),
                (
                    "last_drilled",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
    ]
