"""
模拟数据命令：为每只羊插入 4 条喂养记录
用法：python manage.py seed_feeding
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from sheep_management.models import Sheep, FeedingRecord


FEED_OPTIONS = [
    # (饲料类型, 单位, 数量范围)
    ('青草',   'kg',  (3.0,  8.0)),
    ('玉米秸秆', 'kg', (2.0,  5.0)),
    ('精饲料',  'kg',  (0.5,  2.0)),
    ('燕麦干草', '捆', (1.0,  3.0)),
    ('豆粕',   'kg',  (0.3,  1.0)),
    ('麦麸',   'kg',  (0.5,  1.5)),
    ('胡萝卜',  'kg',  (0.5,  2.0)),
    ('盐砖',   'g',   (50.0, 100.0)),
]


class Command(BaseCommand):
    help = '为每只羊插入 4 条模拟喂养记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='插入前先清空现有喂养记录',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = FeedingRecord.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'已清空 {count} 条喂养记录'))

        sheep_list = Sheep.objects.all()
        if not sheep_list.exists():
            self.stdout.write(self.style.ERROR('数据库中没有羊只数据，请先添加羊只'))
            return

        today = date.today()
        created_total = 0

        for sheep in sheep_list:
            # 每只羊随机挑 4 种不重复的饲料
            chosen_feeds = random.sample(FEED_OPTIONS, 4)

            for i, (feed_type, unit, (low, high)) in enumerate(chosen_feeds):
                feed_date = today - timedelta(days=i * 3)   # 每隔3天一条
                amount = round(random.uniform(low, high), 1)

                FeedingRecord.objects.create(
                    sheep=sheep,
                    feed_type=feed_type,
                    feed_date=feed_date,
                    amount=amount,
                    unit=unit,
                )
                created_total += 1

        self.stdout.write(self.style.SUCCESS(
            f'✅ 成功为 {sheep_list.count()} 只羊插入共 {created_total} 条喂养记录'
        ))
