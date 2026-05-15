# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0006_ejercicio_creado_por_rutina_es_publica'),
    ]

    operations = [
        migrations.AddField(
            model_name='ejercicioenrutina',
            name='peso_sugerido',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
