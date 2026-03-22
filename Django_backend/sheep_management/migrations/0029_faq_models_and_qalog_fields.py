from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sheep_management', '0028_breederfollow_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QACategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='问答分类名称')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='问答分类编码')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='分类说明')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('status', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '问答分类',
                'verbose_name_plural': '问答分类',
                'db_table': 'qa_category',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='QAPair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255, unique=True, verbose_name='标准问题')),
                ('answer', models.TextField(verbose_name='标准答案')),
                ('answer_type', models.CharField(choices=[('text', '纯文本'), ('table', '表格型'), ('mixed', '混合型')], default='text', max_length=20, verbose_name='答案类型')),
                ('keywords', models.CharField(blank=True, max_length=500, verbose_name='关键词')),
                ('month_stage', models.CharField(blank=True, max_length=50, verbose_name='适用月龄阶段')),
                ('is_hot', models.BooleanField(default=False, verbose_name='是否热门问题')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('status', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qa_pairs', to='sheep_management.qacategory', verbose_name='所属分类')),
            ],
            options={
                'verbose_name': '问答对',
                'verbose_name_plural': '问答对',
                'db_table': 'qa_pair',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='QAAlias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias_question', models.CharField(max_length=255, verbose_name='别名问题')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('qa_pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='sheep_management.qapair', verbose_name='所属标准问题')),
            ],
            options={
                'verbose_name': '问答别名',
                'verbose_name_plural': '问答别名',
                'db_table': 'qa_alias',
            },
        ),
        migrations.CreateModel(
            name='QAAnswerDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage_name', models.CharField(max_length=50, verbose_name='阶段名称')),
                ('weight_range', models.CharField(blank=True, max_length=100, verbose_name='体重范围')),
                ('nutrition_value', models.CharField(blank=True, max_length=255, verbose_name='营养说明')),
                ('cost_value', models.CharField(blank=True, max_length=255, verbose_name='成本说明')),
                ('price_value', models.CharField(blank=True, max_length=255, verbose_name='价格说明')),
                ('description', models.TextField(blank=True, verbose_name='补充说明')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('qa_pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='sheep_management.qapair', verbose_name='所属问题')),
            ],
            options={
                'verbose_name': '问答明细',
                'verbose_name_plural': '问答明细',
                'db_table': 'qa_answer_detail',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='QARelated',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('source_qa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_sources', to='sheep_management.qapair', verbose_name='源问题')),
                ('target_qa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_targets', to='sheep_management.qapair', verbose_name='关联问题')),
            ],
            options={
                'verbose_name': '关联问题',
                'verbose_name_plural': '关联问题',
                'db_table': 'qa_related',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.AddField(
            model_name='qalog',
            name='hit_faq_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='命中的问答对ID'),
        ),
        migrations.AddField(
            model_name='qalog',
            name='qa_mode',
            field=models.CharField(default='ai', max_length=20, verbose_name='问答模式'),
        ),
        migrations.AddIndex(
            model_name='qacategory',
            index=models.Index(fields=['sort_order', 'id'], name='qa_category_sort_i_216b0e_idx'),
        ),
        migrations.AddIndex(
            model_name='qapair',
            index=models.Index(fields=['status', 'sort_order'], name='qa_pair_status_e90ed6_idx'),
        ),
        migrations.AddIndex(
            model_name='qapair',
            index=models.Index(fields=['category', 'status'], name='qa_pair_categor_49235d_idx'),
        ),
        migrations.AddIndex(
            model_name='qapair',
            index=models.Index(fields=['is_hot', 'status'], name='qa_pair_is_hot_6f2145_idx'),
        ),
        migrations.AddIndex(
            model_name='qaalias',
            index=models.Index(fields=['alias_question'], name='qa_alias_alias_q_3baf30_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='qaalias',
            unique_together={('qa_pair', 'alias_question')},
        ),
        migrations.AlterUniqueTogether(
            name='qarelated',
            unique_together={('source_qa', 'target_qa')},
        ),
    ]
