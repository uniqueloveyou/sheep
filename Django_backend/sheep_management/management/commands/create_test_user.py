"""
Django管理命令：创建测试用户
使用方法: python manage.py create_test_user
"""
from django.core.management.base import BaseCommand
from sheep_management.models import User
from datetime import datetime


class Command(BaseCommand):
    help = '创建测试用户'

    def handle(self, *args, **options):
        # 测试用户列表
        test_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'openid': f'test_openid_admin_{int(datetime.now().timestamp())}',
                'nickname': '管理员',
                'mobile': '13800138000',
                'gender': 1
            },
            {
                'username': 'test',
                'password': 'test123',
                'openid': f'test_openid_test_{int(datetime.now().timestamp())}',
                'nickname': '测试用户',
                'mobile': '13900139000',
                'gender': 0
            },
            {
                'username': 'user1',
                'password': '123456',
                'openid': f'test_openid_user1_{int(datetime.now().timestamp())}',
                'nickname': '用户1',
                'mobile': '13700137000',
                'gender': 1
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for user_data in test_users:
            username = user_data['username']
            openid = user_data['openid']
            
            # 检查用户是否已存在（通过username或openid）
            existing_user = User.objects.filter(
                username=username
            ).first()
            
            if existing_user:
                # 更新现有用户
                existing_user.password = user_data['password']
                existing_user.nickname = user_data['nickname']
                existing_user.mobile = user_data['mobile']
                existing_user.gender = user_data['gender']
                # 如果openid为空，设置一个
                if not existing_user.openid:
                    existing_user.openid = openid
                existing_user.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 更新用户: {username} (密码: {user_data["password"]})')
                )
            else:
                # 创建新用户
                # 检查openid是否已存在
                if User.objects.filter(openid=openid).exists():
                    # 如果openid已存在，生成新的
                    openid = f'{openid}_{int(datetime.now().timestamp())}'
                
                User.objects.create(**user_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建用户: {username} (密码: {user_data["password"]})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！创建了 {created_count} 个用户，更新了 {updated_count} 个用户。'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n测试账号：\n'
                '  用户名: admin, 密码: admin123\n'
                '  用户名: test, 密码: test123\n'
                '  用户名: user1, 密码: 123456'
            )
        )

