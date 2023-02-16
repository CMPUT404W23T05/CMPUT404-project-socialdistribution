# Generated by Django 4.1.6 on 2023-02-16 05:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authors', '0002_rename_type_author_object_type_rename_id_author_uid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follow_type', models.CharField(max_length=50)),
                ('author_actor', models.CharField(max_length=50)),
                ('author_object', models.CharField(max_length=50)),
                ('following_summary', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Followers',
            fields=[
                ('author_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='authors.author')),
                ('follower_author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers_info', to='authors.author')),
            ],
            bases=('authors.author',),
        ),
    ]
