"""
测试养殖户API的脚本
直接运行此脚本来测试API是否正常工作
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_backend.settings')
django.setup()

from sheep_management.models import Breeder, Sheep
from django.db import connection

print("=" * 50)
print("测试养殖户API")
print("=" * 50)

# 1. 测试数据库连接
print("\n1. 测试数据库连接...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"   ✅ 当前数据库: {db_name}")
except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    sys.exit(1)

# 2. 测试表是否存在
print("\n2. 测试breeders表是否存在...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'breeders'")
        table_exists = cursor.fetchone()
        if table_exists:
            print(f"   ✅ breeders表存在")
        else:
            print(f"   ❌ breeders表不存在！")
            sys.exit(1)
except Exception as e:
    print(f"   ❌ 检查表失败: {e}")
    sys.exit(1)

# 3. 测试原始SQL查询
print("\n3. 测试原始SQL查询...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM breeders")
        raw_count = cursor.fetchone()[0]
        print(f"   ✅ 原始SQL查询结果: {raw_count} 条记录")
        
        if raw_count > 0:
            cursor.execute("SELECT id, name, gender, phone FROM breeders LIMIT 3")
            raw_data = cursor.fetchall()
            print(f"   ✅ 原始SQL查询数据:")
            for row in raw_data:
                print(f"      - ID: {row[0]}, 姓名: {row[1]}, 性别: {row[2]}, 电话: {row[3]}")
        else:
            print(f"   ⚠️  表中没有数据！")
except Exception as e:
    print(f"   ❌ 原始SQL查询失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 测试ORM查询
print("\n4. 测试ORM查询...")
try:
    breeders = Breeder.objects.all()
    breeder_count = breeders.count()
    print(f"   ✅ ORM查询结果: {breeder_count} 个养殖户")
    print(f"   ✅ 模型映射的表名: {Breeder._meta.db_table}")
    
    if breeder_count > 0:
        print(f"   ✅ ORM查询数据:")
        for breeder in breeders[:3]:
            print(f"      - ID: {breeder.id}, 姓名: {breeder.name}, 性别: {breeder.gender}, 电话: {breeder.phone}")
    else:
        print(f"   ⚠️  ORM查询没有数据！")
except Exception as e:
    print(f"   ❌ ORM查询失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 测试API视图函数
print("\n5. 测试API视图函数...")
try:
    from django.test import RequestFactory
    from sheep_management.views.views import api_get_breeders
    
    factory = RequestFactory()
    request = factory.get('/api/breeders')
    
    response = api_get_breeders(request)
    print(f"   ✅ API响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        if isinstance(data, list):
            print(f"   ✅ API返回数组，包含 {len(data)} 条数据")
            if len(data) > 0:
                print(f"   ✅ 第一条数据: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
        else:
            print(f"   ⚠️  API返回的不是数组: {type(data)}")
            print(f"   ⚠️  返回内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
    else:
        print(f"   ❌ API返回错误状态码: {response.status_code}")
        print(f"   ❌ 响应内容: {response.content.decode()}")
except Exception as e:
    print(f"   ❌ API测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)

