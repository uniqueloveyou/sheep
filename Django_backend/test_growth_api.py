"""
测试生长周期API的脚本
直接运行此脚本来测试API是否正常工作
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_backend.settings')
django.setup()

from sheep_management.models import Sheep, GrowthRecord, FeedingRecord, VaccinationHistory
from django.test import RequestFactory
from sheep_management.views.views import api_get_sheep_with_growth
from django.db import connection
import json

print("=" * 50)
print("测试生长周期API - 数据库诊断")
print("=" * 50)

# 1. 检查数据库连接和表结构
print("\n1. 检查数据库连接和表结构...")
try:
    with connection.cursor() as cursor:
        # 检查sheep表是否存在
        cursor.execute("SHOW TABLES LIKE 'sheep'")
        sheep_table_exists = cursor.fetchone()
        if sheep_table_exists:
            print("   ✅ sheep表存在")
        else:
            print("   ❌ sheep表不存在！")
            sys.exit(1)
        
        # 检查growth_records表是否存在
        cursor.execute("SHOW TABLES LIKE 'growth_records'")
        growth_table_exists = cursor.fetchone()
        if growth_table_exists:
            print("   ✅ growth_records表存在")
        else:
            print("   ⚠️  growth_records表不存在（可选）")
        
        # 检查sheep表结构
        cursor.execute("DESCRIBE sheep")
        sheep_columns = cursor.fetchall()
        print(f"   ✅ sheep表字段: {[col[0] for col in sheep_columns]}")
        
        # 检查sheep表数据
        cursor.execute("SELECT COUNT(*) FROM sheep")
        sheep_count = cursor.fetchone()[0]
        print(f"   ✅ sheep表中有 {sheep_count} 条记录")
        
        if sheep_count > 0:
            cursor.execute("SELECT id, gender, weight, height, length FROM sheep LIMIT 3")
            sheep_data = cursor.fetchall()
            print(f"   ✅ 前3条数据: {sheep_data}")
        else:
            print("   ⚠️  sheep表中没有数据！")
            print("   ⚠️  请先在Django后台或数据库中添加羊只数据")
    
    # 使用ORM查询
    try:
        sheep_count_orm = Sheep.objects.count()
        print(f"   ✅ ORM查询成功，找到 {sheep_count_orm} 只羊")
        if sheep_count_orm > 0:
            sheep_ids = list(Sheep.objects.values_list('id', flat=True)[:3])
            print(f"   ✅ 前3只羊的ID: {sheep_ids}")
    except Exception as e:
        print(f"   ❌ ORM查询失败: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 检查生长记录表
print("\n2. 检查生长记录表...")
try:
    with connection.cursor() as cursor:
        # 检查growth_records表结构
        cursor.execute("SHOW TABLES LIKE 'growth_records'")
        if cursor.fetchone():
            cursor.execute("DESCRIBE growth_records")
            growth_columns = cursor.fetchall()
            print(f"   ✅ growth_records表字段: {[col[0] for col in growth_columns]}")
            
            cursor.execute("SELECT COUNT(*) FROM growth_records")
            growth_count_raw = cursor.fetchone()[0]
            print(f"   ✅ growth_records表中有 {growth_count_raw} 条记录")
            
            if growth_count_raw > 0:
                cursor.execute("SELECT id, sheep_id, record_date, weight, height, length FROM growth_records LIMIT 3")
                growth_data = cursor.fetchall()
                print(f"   ✅ 前3条生长记录: {growth_data}")
        else:
            print("   ⚠️  growth_records表不存在（这是正常的，如果没有生长记录数据）")
    
    # 使用ORM查询
    try:
        growth_count = GrowthRecord.objects.count()
        print(f"   ✅ ORM查询生长记录: {growth_count} 条")
        
        if growth_count > 0:
            sample = GrowthRecord.objects.first()
            print(f"   ✅ 示例记录: 羊只ID={sample.sheep_id}, 日期={sample.record_date}, 体重={sample.weight}kg")
    except Exception as e:
        print(f"   ❌ ORM查询生长记录失败: {e}")
        import traceback
        traceback.print_exc()
except Exception as e:
    print(f"   ❌ 检查生长记录失败: {e}")
    import traceback
    traceback.print_exc()

# 3. 测试API（使用第一只羊的ID）
print("\n3. 测试API...")
try:
    # 先尝试用ORM获取
    try:
        test_sheep = Sheep.objects.first()
        if test_sheep:
            test_sheep_id = test_sheep.id
            print(f"   ✅ 使用ORM获取羊只ID: {test_sheep_id}")
        else:
            # 如果ORM失败，用原始SQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM sheep LIMIT 1")
                result = cursor.fetchone()
                if result:
                    test_sheep_id = result[0]
                    print(f"   ✅ 使用原始SQL获取羊只ID: {test_sheep_id}")
                else:
                    print("   ⚠️  没有羊只数据，无法测试API")
                    sys.exit(0)
    except Exception as e:
        print(f"   ❌ 获取羊只ID失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    factory = RequestFactory()
    request = factory.get(f'/api/growth/sheep/{test_sheep_id}')
    
    print(f"   ✅ 发送请求: GET /api/growth/sheep/{test_sheep_id}")
    print(f"   ✅ 开始调用API函数...")
    
    try:
        response = api_get_sheep_with_growth(request, test_sheep_id)
        print(f"   ✅ API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"   ✅ API返回成功")
            print(f"   ✅ 返回数据:")
            print(f"      - 羊只ID: {data.get('id')}")
            print(f"      - 性别: {data.get('gender')}")
            print(f"      - 体重: {data.get('weight')}kg")
            print(f"      - 身高: {data.get('height')}cm")
            print(f"      - 体长: {data.get('length')}cm")
            print(f"      - 生长记录数: {len(data.get('growth_records', []))}")
            print(f"      - 喂养记录数: {len(data.get('feeding_records', []))}")
            print(f"      - 疫苗接种记录数: {len(data.get('vaccination_records', []))}")
        else:
            print(f"   ❌ API返回错误状态码: {response.status_code}")
            print(f"   ❌ 响应内容: {response.content.decode()}")
    except Exception as api_error:
        print(f"   ❌ API调用时发生异常: {api_error}")
        import traceback
        traceback.print_exc()
        print("\n   详细错误信息:")
        print(traceback.format_exc())
        
except Exception as e:
    print(f"   ❌ API测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
print("\n提示：如果API返回500错误，请查看上面的错误信息")
print("常见问题：")
print("  1. 数据库连接失败")
print("  2. 表不存在或字段不匹配")
print("  3. 数据格式转换错误")

