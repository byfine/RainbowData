# Generated by Django 4.2.22 on 2025-06-08 10:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lottery', '0004_add_crawler_models'),
    ]

    operations = [
        # 添加UserProfile表的user字段
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name='关联用户',
                default=1  # 临时默认值，稍后会移除
            ),
            preserve_default=False,
        ),
    ]
