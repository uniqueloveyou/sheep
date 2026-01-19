"""智能问答API接口"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import requests
import time


@csrf_exempt
@require_http_methods(["POST"])
def api_qa_ask(request):
    """
    智能问答接口
    POST /api/qa/ask
    请求体：
        {
            "question": "滩羊的养殖方法"
        }
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        
        if not question:
            return JsonResponse({
                'code': 400,
                'msg': '问题不能为空',
                'data': None
            }, status=400)
        
        # 尝试调用大模型API
        answer = None
        error_msg = None
        
        # 1. 尝试OpenAI API
        answer = call_openai_api(question)
        if answer:
            return JsonResponse({
                'code': 0,
                'msg': '成功',
                'data': {
                    'answer': answer,
                    'model': 'openai'
                }
            }, status=200)
        
        # 2. 尝试百度文心一言API
        answer = call_baidu_api(question)
        if answer:
            return JsonResponse({
                'code': 0,
                'msg': '成功',
                'data': {
                    'answer': answer,
                    'model': 'baidu'
                }
            }, status=200)
        
        # 3. 尝试阿里通义千问API
        answer = call_ali_api(question)
        if answer:
            return JsonResponse({
                'code': 0,
                'msg': '成功',
                'data': {
                    'answer': answer,
                    'model': 'ali'
                }
            }, status=200)
        
        # 4. 如果所有大模型都不可用，使用本地回答
        answer = get_local_answer(question)
        return JsonResponse({
            'code': 0,
            'msg': '成功（使用本地回答）',
            'data': {
                'answer': answer,
                'model': 'local'
            }
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'msg': '请求数据格式错误',
            'data': None
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 发生错误时，使用本地回答作为备用
        answer = get_local_answer(question if 'question' in locals() else '')
        return JsonResponse({
            'code': 0,
            'msg': '成功（使用本地回答）',
            'data': {
                'answer': answer,
                'model': 'local'
            }
        }, status=200)


def call_openai_api(question):
    """调用OpenAI API"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
        if not api_key:
            return None
        
        url = f"{api_base}/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 构建系统提示词
        system_prompt = """你是一个专业的滩羊养殖和产品咨询助手。请用中文回答用户关于滩羊的问题，包括：
1. 滩羊的养殖方法和技术
2. 滩羊肉的营养价值和特点
3. 如何挑选优质滩羊
4. 滩羊肉的烹饪方法
5. 滩羊的生长周期和特点
6. 盐池滩羊的特色

请提供专业、准确、友好的回答。如果问题不在你的知识范围内，请礼貌地说明。"""
        
        data = {
            'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': question}
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
        
        return None
    except Exception as e:
        print(f'OpenAI API调用失败: {str(e)}')
        return None


def call_baidu_api(question):
    """调用百度文心一言API"""
    try:
        api_key = os.getenv('BAIDU_API_KEY')
        secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        if not api_key or not secret_key:
            return None
        
        # 获取access_token
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        token_response = requests.post(token_url, timeout=5)
        
        if token_response.status_code != 200:
            return None
        
        access_token = token_response.json().get('access_token')
        if not access_token:
            return None
        
        # 调用文心一言API
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
        
        system_prompt = """你是一个专业的滩羊养殖和产品咨询助手。请用中文回答用户关于滩羊的问题。"""
        
        data = {
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': question}
            ],
            'temperature': 0.7,
            'max_output_tokens': 1000
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                return result['result']
        
        return None
    except Exception as e:
        print(f'百度API调用失败: {str(e)}')
        return None


def call_ali_api(question):
    """调用阿里通义千问API"""
    try:
        api_key = os.getenv('ALI_API_KEY')
        api_base = os.getenv('ALI_API_BASE', 'https://dashscope.aliyuncs.com/api/v1')
        
        if not api_key:
            return None
        
        url = f"{api_base}/services/aigc/text-generation/generation"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        system_prompt = """你是一个专业的滩羊养殖和产品咨询助手。请用中文回答用户关于滩羊的问题。"""
        
        data = {
            'model': os.getenv('ALI_MODEL', 'qwen-turbo'),
            'input': {
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': question}
                ]
            },
            'parameters': {
                'temperature': 0.7,
                'max_tokens': 1000
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                return result['output']['text']
        
        return None
    except Exception as e:
        print(f'阿里API调用失败: {str(e)}')
        return None


def get_local_answer(question):
    """本地回答（基于关键词匹配）"""
    q = question.lower()
    
    # 根据关键词匹配回答
    if '养殖' in q or '饲养' in q or '喂养' in q:
        return '滩羊养殖需要注意以下几点：\n\n1. 选择优质草场，确保充足的草料供应\n2. 定期进行疫苗接种和驱虫\n3. 保持圈舍清洁卫生，定期消毒\n4. 根据生长阶段调整饲料配比\n5. 注意观察羊群健康状况，及时处理疾病\n6. 提供充足的清洁饮水\n\n建议咨询专业养殖户获取更详细的指导。'
    
    elif '营养' in q or '价值' in q or '成分' in q:
        return '滩羊肉富含以下营养成分：\n\n1. 优质蛋白质：含量高达20%以上，易于消化吸收\n2. 维生素B群：有助于新陈代谢和神经系统健康\n3. 铁元素：预防贫血，提高免疫力\n4. 锌元素：促进生长发育，增强抵抗力\n5. 低脂肪：相比其他肉类，脂肪含量适中\n6. 氨基酸：含有人体必需的多种氨基酸\n\n滩羊肉具有温补作用，适合冬季进补，对体虚、贫血等有良好效果。'
    
    elif '挑选' in q or '选择' in q or '识别' in q:
        return '挑选优质滩羊的方法：\n\n1. 看体型：体型匀称，肌肉发达，骨骼健壮\n2. 看毛色：毛色纯正，光泽良好，无脱毛现象\n3. 看眼睛：眼睛明亮有神，无分泌物\n4. 看精神状态：活泼好动，食欲正常\n5. 看生长记录：查看疫苗接种记录和生长数据\n6. 闻气味：优质滩羊没有异味，肉质清香\n\n建议选择有完整生长记录和健康证明的滩羊。'
    
    elif '烹饪' in q or '做法' in q or '怎么吃' in q:
        return '滩羊肉的常见烹饪方法：\n\n1. 清炖：保留原汁原味，适合老人和小孩\n2. 红烧：搭配时令蔬菜，营养丰富\n3. 手抓羊肉：配蒜泥和辣椒面，口感更佳\n4. 烤羊肉：外焦里嫩，香味浓郁\n5. 羊肉汤：温补暖身，适合冬季\n6. 涮羊肉：鲜嫩爽滑，原汁原味\n\n详细做法请查看小程序中的相关功能模块。'
    
    elif '生长' in q or '周期' in q or '时间' in q:
        return '滩羊的生长周期：\n\n1. 哺乳期：0-3个月，主要依靠母乳\n2. 断奶期：3-6个月，开始吃草料\n3. 育成期：6-12个月，快速生长期\n4. 成熟期：12-18个月，达到出栏标准\n5. 成年期：18个月以上，可用于繁殖\n\n不同阶段的饲养重点不同，需要根据生长阶段调整饲料和管理方式。'
    
    elif '盐池' in q or '特点' in q or '特色' in q:
        return '盐池滩羊的特点：\n\n1. 地理优势：盐池县独特的地理环境和气候条件\n2. 肉质特点：肉质鲜嫩，不腥不膻，被誉为"羊肉界的顶流"\n3. 营养价值：富含优质蛋白质和多种微量元素\n4. 品牌价值：国家地理标志产品，品质有保障\n5. 养殖传统：拥有悠久的养殖历史和丰富的经验\n6. 市场认可：深受消费者喜爱，价格稳定\n\n盐池滩羊是宁夏的特色农产品，具有很高的市场价值。'
    
    else:
        return f'感谢您的提问！关于"{question}"的问题，我建议您：\n\n1. 查看小程序中的相关功能模块（如"生长周期"、"日常饲料"等）\n2. 咨询专业养殖户获取详细指导\n3. 联系客服获取更多帮助\n\n如果您有其他关于滩羊的问题，欢迎继续提问！'

