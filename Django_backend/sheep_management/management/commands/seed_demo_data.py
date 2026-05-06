from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from sheep_management.models import (
    CartItem,
    FeedingRecord,
    GrowthRecord,
    Order,
    OrderItem,
    QAAlias,
    QACategory,
    QAPair,
    Sheep,
    User,
    VaccineType,
    VaccinationHistory,
)
from sheep_management.services.sheep_service import TRACE_BASE_URL


DEMO_PASSWORD = "Yanchi@2026Demo"
DEMO_USERNAMES = [
    "admin_demo",
    "breeder_yanchi",
    "breeder_pending",
    "consumer_demo",
    "consumer_family",
]
DEMO_EAR_PREFIX = "YCDEMO"


class Command(BaseCommand):
    help = "Create polished demo data for the Yanchi Tan sheep traceability and adoption platform."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-reset",
            action="store_true",
            help="Do not clear previously generated demo users/sheep before seeding.",
        )
        parser.add_argument(
            "--skip-qrcode",
            action="store_true",
            help="Skip QR image generation. Trace URLs remain available.",
        )
        parser.add_argument(
            "--skip-faq",
            action="store_true",
            help="Skip the existing FAQ seed command.",
        )

    def handle(self, *args, **options):
        reset = not options["no_reset"]

        with transaction.atomic():
            if reset:
                self._clear_demo_data()

            users = self._seed_users()
            vaccines = self._seed_vaccines()
            sheep_list = self._seed_sheep(users)
            self._seed_trace_records(sheep_list, vaccines)
            self._seed_orders(users, sheep_list)

        if not options["skip_qrcode"]:
            self._generate_qrcodes(sheep_list)

        if not options["skip_faq"]:
            try:
                call_command("seed_faq")
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"FAQ seed skipped: {exc}"))

        self._print_summary(users, sheep_list)

    def _clear_demo_data(self):
        demo_sheep = Sheep.objects.filter(ear_tag__startswith=DEMO_EAR_PREFIX)
        demo_users = User.objects.filter(username__in=DEMO_USERNAMES)

        CartItem.objects.filter(sheep__in=demo_sheep).delete()
        OrderItem.objects.filter(sheep__in=demo_sheep).delete()
        Order.objects.filter(user__in=demo_users).delete()
        demo_sheep.delete()
        demo_users.delete()
        QAPair.objects.filter(question__startswith="演示：").delete()

    def _seed_users(self):
        user_specs = [
            {
                "username": "admin_demo",
                "nickname": "平台管理员-马晓宁",
                "mobile": "13809530001",
                "role": 2,
                "is_verified": True,
                "is_staff": True,
                "is_superuser": True,
                "description": "负责养殖户资质审核、订单监管和溯源数据巡检。",
                "province": "宁夏回族自治区",
                "city": "吴忠市盐池县",
            },
            {
                "username": "breeder_yanchi",
                "nickname": "马建国",
                "mobile": "13909530026",
                "role": 1,
                "is_verified": True,
                "description": "盐池县王乐井乡养殖户，负责振兴滩羊合作社示范羊舍日常养殖管理。",
                "province": "宁夏回族自治区",
                "city": "吴忠市盐池县",
                "latitude": Decimal("37.784620"),
                "longitude": Decimal("107.407980"),
            },
            {
                "username": "breeder_pending",
                "nickname": "李秀兰",
                "mobile": "13909530038",
                "role": 1,
                "is_verified": False,
                "description": "盐池县花马池镇养殖户，已提交家庭牧场资质材料，等待管理员审核。",
                "province": "宁夏回族自治区",
                "city": "吴忠市盐池县",
                "latitude": Decimal("37.792310"),
                "longitude": Decimal("107.389120"),
            },
            {
                "username": "consumer_demo",
                "nickname": "银川品质家庭客户",
                "mobile": "13619510018",
                "role": 0,
                "is_verified": True,
                "balance": Decimal("6800.00"),
                "description": "用于小程序端浏览、领养、订单和扫码溯源演示。",
                "province": "宁夏回族自治区",
                "city": "银川市金凤区",
            },
            {
                "username": "consumer_family",
                "nickname": "盐池本地团购客户",
                "mobile": "13709530058",
                "role": 0,
                "is_verified": True,
                "balance": Decimal("3600.00"),
                "description": "用于展示历史订单、我的羊只和智能问答。",
                "province": "宁夏回族自治区",
                "city": "吴忠市盐池县",
            },
        ]

        users = {}
        for spec in user_specs:
            username = spec.pop("username")
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    **spec,
                    "openid": f"demo_openid_{username}",
                    "unionid": f"demo_unionid_{username}",
                    "country": "中国",
                    "gender": 0,
                    "is_active": True,
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.save()
            users[username] = user
        return users

    def _seed_vaccines(self):
        vaccine_specs = [
            ("小反刍兽疫活疫苗", "用于羊群小反刍兽疫基础免疫。", "宁夏动物疫病预防控制中心", 365),
            ("羊三联四防灭活疫苗", "用于羊快疫、猝狙、肠毒血症等疫病综合预防。", "中牧实业股份有限公司", 180),
            ("羊口蹄疫O型灭活疫苗", "用于口蹄疫O型免疫保护。", "金宇保灵生物药品有限公司", 180),
        ]
        vaccines = {}
        for name, description, manufacturer, validity_days in vaccine_specs:
            vaccine, _ = VaccineType.objects.update_or_create(
                name=name,
                defaults={
                    "description": description,
                    "manufacturer": manufacturer,
                    "validity_days": validity_days,
                },
            )
            vaccines[name] = vaccine
        return vaccines

    def _seed_sheep(self, users):
        breeder = users["breeder_yanchi"]
        today = date.today()
        sheep_specs = [
            ("YCDEMO-2026-001", 1, "健康", 38.6, 63.0, 77.5, today - timedelta(days=210), "盐池县王乐井乡振兴滩羊合作社一号舍", "2680.00"),
            ("YCDEMO-2026-002", 0, "健康", 34.2, 60.5, 73.8, today - timedelta(days=185), "盐池县王乐井乡振兴滩羊合作社一号舍", "2380.00"),
            ("YCDEMO-2026-003", 1, "良好", 42.8, 66.2, 81.4, today - timedelta(days=245), "盐池县王乐井乡振兴滩羊合作社二号舍", "2980.00"),
            ("YCDEMO-2026-004", 0, "健康", 31.5, 58.8, 71.0, today - timedelta(days=165), "盐池县王乐井乡振兴滩羊合作社二号舍", "2180.00"),
            ("YCDEMO-2026-005", 1, "健康", 46.4, 68.0, 84.5, today - timedelta(days=275), "盐池县王乐井乡振兴滩羊合作社核心示范区", "3280.00"),
            ("YCDEMO-2026-006", 0, "需关注", 29.7, 57.2, 69.6, today - timedelta(days=150), "盐池县王乐井乡振兴滩羊合作社隔离观察栏", "1980.00"),
        ]

        sheep_list = []
        for ear_tag, gender, health_status, weight, height, length, birth_date, farm_name, price in sheep_specs:
            sheep, _ = Sheep.objects.update_or_create(
                ear_tag=ear_tag,
                defaults={
                    "gender": gender,
                    "health_status": health_status,
                    "weight": weight,
                    "height": height,
                    "length": length,
                    "birth_date": birth_date,
                    "farm_name": farm_name,
                    "owner": breeder,
                    "price": Decimal(price),
                },
            )
            sheep_list.append(sheep)
        return sheep_list

    def _seed_trace_records(self, sheep_list, vaccines):
        for sheep in sheep_list:
            GrowthRecord.objects.filter(sheep=sheep).delete()
            FeedingRecord.objects.filter(sheep=sheep).delete()
            VaccinationHistory.objects.filter(sheep=sheep).delete()

            age_days = max((date.today() - sheep.birth_date).days if sheep.birth_date else 180, 120)
            start_date = sheep.birth_date or (date.today() - timedelta(days=age_days))
            growth_points = [
                (30, 10.8, 42.0, 48.5),
                (75, 18.6, 49.5, 57.2),
                (120, 26.4, 55.8, 66.0),
                (165, 32.1, 59.5, 72.3),
                (min(age_days, 210), sheep.weight, sheep.height, sheep.length),
            ]
            for offset, weight, height, length in growth_points:
                record_date = start_date + timedelta(days=min(offset, age_days))
                if record_date <= date.today():
                    GrowthRecord.objects.create(
                        sheep=sheep,
                        record_date=record_date,
                        weight=round(float(weight), 1),
                        height=round(float(height), 1),
                        length=round(float(length), 1),
                    )

            feeding_specs = [
                (date.today() - timedelta(days=21), "天然草场补饲+青贮玉米", 1.80, "kg/日"),
                (date.today() - timedelta(days=14), "紫花苜蓿干草+玉米精料", 2.10, "kg/日"),
                (date.today() - timedelta(days=7), "盐池草原牧草+矿物质盐砖", 1.95, "kg/日"),
                (date.today() - timedelta(days=1), "苜蓿干草+燕麦草+少量玉米", 2.20, "kg/日"),
            ]
            for feed_date, feed_type, amount, unit in feeding_specs:
                FeedingRecord.objects.create(
                    sheep=sheep,
                    feed_date=feed_date,
                    feed_type=feed_type,
                    amount=amount,
                    unit=unit,
                )

            vaccine_plan = [
                ("小反刍兽疫活疫苗", start_date + timedelta(days=45), 1.0, "盐池县动物防疫员 李建军", "基础免疫，接种后观察正常。"),
                ("羊三联四防灭活疫苗", start_date + timedelta(days=90), 2.0, "合作社兽医 马彩霞", "按免疫程序接种，无异常反应。"),
            ]
            if age_days >= 180:
                vaccine_plan.append(("羊口蹄疫O型灭活疫苗", start_date + timedelta(days=150), 1.0, "合作社兽医 马彩霞", "加强免疫，精神状态良好。"))

            for vaccine_name, vaccination_date, dosage, administered_by, notes in vaccine_plan:
                if vaccination_date > date.today():
                    continue
                vaccine = vaccines[vaccine_name]
                expiry_date = vaccination_date + timedelta(days=vaccine.validity_days or 180)
                VaccinationHistory.objects.create(
                    sheep=sheep,
                    vaccine=vaccine,
                    vaccination_date=vaccination_date,
                    expiry_date=expiry_date,
                    dosage=dosage,
                    administered_by=administered_by,
                    notes=notes,
                )

    def _seed_orders(self, users, sheep_list):
        consumer = users["consumer_demo"]
        family = users["consumer_family"]
        for user in [consumer, family]:
            CartItem.objects.filter(user=user).delete()
            Order.objects.filter(user=user, order_no__startswith="YCADOPT").delete()

        paid_order = Order.objects.create(
            user=consumer,
            order_no="YCADOPT202605020001",
            total_amount=sheep_list[0].price + sheep_list[2].price,
            status="paid",
            receiver_name="刘思源",
            receiver_phone="13619510018",
            shipping_address="宁夏银川市金凤区阅海湾中央商务区示范住址18号",
            pay_time=timezone.now() - timedelta(days=2),
        )
        OrderItem.objects.create(order=paid_order, sheep=sheep_list[0], price=sheep_list[0].price)
        OrderItem.objects.create(order=paid_order, sheep=sheep_list[2], price=sheep_list[2].price)

        shipping_order = Order.objects.create(
            user=family,
            order_no="YCADOPT202605020002",
            total_amount=sheep_list[4].price,
            status="shipping",
            receiver_name="张雅琴",
            receiver_phone="13709530058",
            shipping_address="宁夏吴忠市盐池县花马池镇民族西街演示小区6号楼",
            logistics_company="顺丰冷链",
            logistics_tracking_number="SFLL202605020098",
            pay_time=timezone.now() - timedelta(days=5),
            shipping_date=timezone.now() - timedelta(days=1),
        )
        OrderItem.objects.create(order=shipping_order, sheep=sheep_list[4], price=sheep_list[4].price)

        CartItem.objects.create(
            user=consumer,
            sheep=sheep_list[1],
            quantity=1,
            price=sheep_list[1].price,
        )

        category, _ = QACategory.objects.get_or_create(
            code="demo_trace",
            defaults={"name": "演示问答", "description": "答辩演示常用问答", "sort_order": 1},
        )
        qa_items = [
            (
                "演示：消费者如何完成在线领养",
                "消费者登录后进入羊只列表，选择可领养羊只，加入购物车或直接结算，填写收货人、联系电话和地址后提交订单。余额支付成功后，订单状态会变为已支付/认养中。",
                "领养,在线领养,下单,订单",
            ),
            (
                "演示：二维码溯源能看到哪些信息",
                "二维码会进入对应羊只的溯源详情页，展示耳标编号、牧场名称、健康状态、体重、成长记录、饲喂记录和疫苗接种记录。",
                "二维码,溯源,扫码,羊只档案",
            ),
            (
                "演示：管理员如何审核养殖户",
                "管理员登录后台后进入养殖户审核页面，查看待审核牧场资料，确认主体信息后执行审核通过；通过后养殖户即可登录后台维护羊只档案和养殖记录。",
                "管理员,审核,养殖户,认证",
            ),
        ]
        for question, answer, keywords in qa_items:
            qa, _ = QAPair.objects.update_or_create(
                question=question,
                defaults={
                    "category": category,
                    "answer": answer,
                    "keywords": keywords,
                    "is_hot": True,
                    "status": True,
                },
            )
            QAAlias.objects.get_or_create(qa_pair=qa, alias_question=question.replace("演示：", ""))

    def _generate_qrcodes(self, sheep_list):
        from sheep_management.utils import generate_qr_code

        for sheep in sheep_list:
            try:
                generate_qr_code(sheep)
            except Exception as exc:
                self.stdout.write(
                    self.style.WARNING(f"QR generation failed for {sheep.ear_tag}: {exc}")
                )

    def _print_summary(self, users, sheep_list):
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(f"Password for all demo accounts: {DEMO_PASSWORD}")
        self.stdout.write("Accounts:")
        for username in DEMO_USERNAMES:
            user = users.get(username)
            if user:
                self.stdout.write(
                    f"  {user.username} | role={user.role} | verified={user.is_verified} | {user.nickname}"
                )
        self.stdout.write("Trace URLs:")
        for sheep in sheep_list[:4]:
            self.stdout.write(f"  {sheep.ear_tag}: {TRACE_BASE_URL}/trace/{sheep.id}/")
