"""
为所有保留羊只生成统一的养殖记录：
- 生长记录：每2周一次
- 喂养记录：每1周一次（轮换饲料类型）
- 疫苗记录：按标准免疫程序
"""
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import GrowthRecord, FeedingRecord, Sheep, VaccinationHistory, VaccineType

# 饲料类型轮换
FEED_TYPES = ["青贮玉米", "干草", "玉米秸秆", "精饲料", "胡萝卜", "麸皮", "豆粕"]
FEED_UNIT = "kg"

# 羔羊/成羊饲料量
FEED_AMOUNT_BY_WEEK = [
    (0, 0.3), (4, 0.5), (8, 0.8), (12, 1.0),
    (16, 1.2), (20, 1.5), (24, 1.8), (30, 2.0),
    (40, 2.5), (52, 3.0),
]


def feed_amount_for_week(week):
    for w, a in reversed(FEED_AMOUNT_BY_WEEK):
        if week >= w:
            return round(a + random.uniform(-0.1, 0.2), 2)
    return 0.3


def weight_for_week(week, base=3.0):
    daily_gain = random.uniform(0.15, 0.25)
    return round(base + week * 7 * daily_gain + random.uniform(-1, 1), 1)


def height_for_week(week, base=30):
    gain = week * random.uniform(0.2, 0.4)
    return round(base + gain + random.uniform(-1, 1), 1)


def length_for_week(week, base=25):
    gain = week * random.uniform(0.3, 0.5)
    return round(base + gain + random.uniform(-1, 1), 1)


# 免疫程序：周龄 → (vaccine_name, dosage_ml)
VACCINE_SCHEDULE = [
    (2, "小反刍兽疫活疫苗", 1.0),
    (4, "口蹄疫疫苗（O型+亚洲I型）", 2.0),
    (8, "羊快疫四防灭活疫苗", 1.0),
    (12, "山羊传染性胸膜肺炎疫苗", 2.0),
    (16, "口蹄疫疫苗", 2.0),
    (24, "布鲁氏菌活疫苗（S2株）", 1.0),
    (36, "羊四防苗", 1.5),
    (52, "羊痘活疫苗", 0.5),
]

ADMINISTRATORS = ["张兽医", "李兽医", "王兽医", "刘兽医", "陈兽医"]


class Command(BaseCommand):
    help = "为所有羊只生成统一的生长/喂养/疫苗记录"

    def handle(self, *args, **options):
        today = date.today()
        sheep_list = list(Sheep.objects.all().order_by('id'))
        total = len(sheep_list)
        self.stdout.write(f"开始为 {total} 只羊生成记录...")

        # 清空已有记录
        sheep_ids = [s.id for s in sheep_list]
        GrowthRecord.objects.filter(sheep_id__in=sheep_ids).delete()
        FeedingRecord.objects.filter(sheep_id__in=sheep_ids).delete()
        VaccinationHistory.objects.filter(sheep_id__in=sheep_ids).delete()
        self.stdout.write("已清空现有记录")

        # 预加载疫苗种类
        vaccine_map = {v.name: v for v in VaccineType.objects.all()}

        growth_batch = []
        feeding_batch = []
        vaccine_batch = []

        for idx, sheep in enumerate(sheep_list, 1):
            if not sheep.birth_date:
                sheep.birth_date = today - timedelta(days=random.randint(30, 180))
                sheep.save(update_fields=["birth_date"])

            birth = sheep.birth_date
            age_days = (today - birth).days
            age_weeks = max(age_days // 7, 1)

            base_weight = sheep.weight if sheep.weight and sheep.weight > 1 else 3.0
            base_height = sheep.height if sheep.height and sheep.height > 1 else 30.0
            base_length = sheep.length if sheep.length and sheep.length > 1 else 25.0

            # ---- 1. 生长记录：每2周 ----
            for wk in range(1, age_weeks + 1, 2):
                record_date = birth + timedelta(weeks=wk)
                if record_date > today:
                    continue
                growth_batch.append(GrowthRecord(
                    sheep=sheep,
                    record_date=record_date,
                    weight=weight_for_week(wk, base_weight),
                    height=height_for_week(wk, base_height),
                    length=length_for_week(wk, base_length),
                ))

            # ---- 2. 喂养记录：每1周，轮换饲料 ----
            for wk in range(1, age_weeks + 1):
                feed_date = birth + timedelta(weeks=wk)
                if feed_date > today:
                    continue
                feed_type = FEED_TYPES[wk % len(FEED_TYPES)]
                amount = feed_amount_for_week(wk)
                feeding_batch.append(FeedingRecord(
                    sheep=sheep,
                    feed_type=feed_type,
                    feed_date=feed_date,
                    amount=amount,
                    unit=FEED_UNIT,
                ))

            # ---- 3. 疫苗记录：按免疫程序 ----
            for wk, vname, dosage in VACCINE_SCHEDULE:
                if wk > age_weeks:
                    continue
                vaccine_date = birth + timedelta(weeks=wk)
                if vaccine_date > today:
                    continue
                vaccine = vaccine_map.get(vname)
                if not vaccine:
                    continue
                expiry = vaccine_date + timedelta(days=180)
                vaccine_batch.append(VaccinationHistory(
                    vaccine=vaccine,
                    sheep=sheep,
                    vaccination_date=vaccine_date,
                    expiry_date=expiry,
                    dosage=round(dosage + random.uniform(-0.1, 0.1), 2),
                    administered_by=random.choice(ADMINISTRATORS),
                    notes="常规免疫接种",
                ))

            if idx % 20 == 0:
                self.stdout.write(f"  已处理 {idx}/{total} 只羊...")

        with transaction.atomic():
            GrowthRecord.objects.bulk_create(growth_batch, batch_size=500)
            FeedingRecord.objects.bulk_create(feeding_batch, batch_size=500)
            VaccinationHistory.objects.bulk_create(vaccine_batch, batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"\n生成完成！\n"
            f"  生长记录: {len(growth_batch)} 条\n"
            f"  喂养记录: {len(feeding_batch)} 条\n"
            f"  疫苗记录: {len(vaccine_batch)} 条"
        ))
