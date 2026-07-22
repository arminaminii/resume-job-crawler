from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_jobcategory_selected_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobcategory',
            name='education',
            field=models.JSONField(blank=True, default=list, verbose_name='تحصیلات مورد نیاز'),
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='certifications',
            field=models.JSONField(blank=True, default=list, verbose_name='گواهینامه‌ها'),
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='salary_range',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='بازه حقوق'),
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='career_path',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='مسیر پیشرفت'),
        ),
    ]