# Generated by Django 4.2.7 on 2023-11-16 11:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("basics", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testenv",
            name="enable_flag",
            field=models.SmallIntegerField(
                blank=True,
                choices=[(0, "失效"), (1, "生效")],
                default=1,
                null=True,
                verbose_name="有效标识",
            ),
        ),
    ]
