from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE users AUTO_INCREMENT = 100000000;",
            reverse_sql="ALTER TABLE users AUTO_INCREMENT = 1;"
        ),
    ]
