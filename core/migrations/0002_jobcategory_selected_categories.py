from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='نام حوزه')),
                ('slug', models.CharField(max_length=100, unique=True, verbose_name='اسلاگ')),
                ('icon_svg', models.TextField(blank=True, default='', verbose_name='آیکون SVG')),
                ('color', models.CharField(default='#6366f1', max_length=7, verbose_name='رنگ')),
                ('jobvision_slug', models.CharField(blank=True, default='', max_length=100)),
                ('estekhdam_slug', models.CharField(blank=True, default='', max_length=100)),
                ('irantalent_slug', models.CharField(blank=True, default='', max_length=100)),
                ('skills', models.JSONField(blank=True, default=list, verbose_name='مهارت‌ها')),
                ('positions', models.JSONField(blank=True, default=list, verbose_name='موقعیت‌های شغلی')),
                ('keywords_fa', models.JSONField(blank=True, default=list, verbose_name='کلیدواژه‌های فارسی')),
                ('keywords_en', models.JSONField(blank=True, default=list, verbose_name='کلیدواژه‌های انگلیسی')),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='core.jobcategory', verbose_name='دسته والد')),
            ],
            options={
                'verbose_name': 'حوزه شغلی',
                'verbose_name_plural': 'حوزه‌های شغلی',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='jobsearch',
            name='selected_categories',
            field=models.JSONField(blank=True, default=list, verbose_name='حوزه‌های انتخابی'),
        ),
    ]