"""
管理命令：为所有尚未生成二维码的羊只批量补生成溯源 QR 码。

用法：
    python manage.py generate_qrcodes            # 只处理没有 qr_code 的羊只
    python manage.py generate_qrcodes --all      # 强制为所有羊只重新生成
    python manage.py generate_qrcodes --id 42    # 只为指定 ID 的羊只生成
"""
import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from sheep_management.models import Sheep
from sheep_management.services.sheep_service import TRACE_BASE_URL


class Command(BaseCommand):
    help = '为羊只批量生成溯源二维码'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='强制重新生成所有羊只的二维码')
        parser.add_argument('--id', type=int, help='只为指定 ID 的羊只生成')

    def handle(self, *args, **options):
        try:
            import qrcode
        except ImportError:
            self.stderr.write(self.style.ERROR('请先安装 qrcode[pil]：pip install "qrcode[pil]"'))
            return

        if options['id']:
            qs = Sheep.objects.filter(pk=options['id'])
        elif options['all']:
            qs = Sheep.objects.all()
        else:
            qs = Sheep.objects.filter(qr_code='')  # 只处理没有 QR 的

        total = qs.count()
        self.stdout.write(f'待处理羊只数量：{total}')

        ok = 0
        fail = 0
        for sheep in qs.iterator():
            try:
                trace_url = f"{TRACE_BASE_URL}/trace/{sheep.id}/"
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(trace_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')

                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)

                filename = f'qr_sheep_{sheep.id}.png'
                # 先删除旧文件（如果有）
                if sheep.qr_code:
                    try:
                        sheep.qr_code.delete(save=False)
                    except Exception:
                        pass
                sheep.qr_code.save(filename, ContentFile(buf.read()), save=True)
                ok += 1
                if ok % 50 == 0:
                    self.stdout.write(f'  已完成 {ok}/{total}...')
            except Exception as e:
                fail += 1
                self.stderr.write(f'  sheep_id={sheep.id} 失败: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'完成！成功 {ok} 只，失败 {fail} 只。溯源 URL 格式：{TRACE_BASE_URL}/trace/<id>/'
        ))
