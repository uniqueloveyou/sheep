"""
智能问答 API —— DeepSeek V3 + 直接数据注入
策略：登录用户的羊只数据直接查库 → 塞进 system prompt → AI 必定能看到
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random
import time
import requests
import logging

from ..utils import verify_token
from ..models import Sheep, GrowthRecord, FeedingRecord, VaccinationHistory, OrderItem, User, QALog

logger = logging.getLogger(__name__)
PERSONAL_QUESTION_KEYWORDS = [
    '我的', '我家', '我养', '我领养', '我的羊', '我的订单', '我的监控',
    '体重', '生长', '喂养', '饲料', '免疫', '疫苗', '耳标', '健康',
]


def _classify_question_type(question):
    q = (question or '').strip().lower()
    if not q:
        return 'general'
    if any(keyword in q for keyword in PERSONAL_QUESTION_KEYWORDS):
        return 'personal'
    return 'general'


def _safe_log_qa(
    *,
    user_id,
    question,
    question_type,
    answer,
    success,
    fallback_used,
    response_time_ms,
    source_type,
    error_message='',
):
    try:
        user = None
        user_role = None
        if user_id:
            user = User.objects.filter(id=user_id).only('id', 'role').first()
            user_role = user.role if user else None

        QALog.objects.create(
            user=user,
            user_role=user_role,
            question=(question or '')[:5000],
            question_type=question_type or 'general',
            answer=(answer or '')[:10000],
            success=success,
            fallback_used=fallback_used,
            response_time_ms=max(0, int(response_time_ms or 0)),
            source_type=source_type or 'general',
            error_message=(error_message or '')[:500],
        )
    except Exception as log_error:
        logger.warning(f'[QA] 写入日志失败: {log_error}')

# ============================================
# DeepSeek API 配置
# ============================================
DEEPSEEK_API_KEY = 'sk-db2a7aa8e86647bb88a4bd63627bf879'
DEEPSEEK_API_BASE = 'https://api.deepseek.com'
DEEPSEEK_MODEL = 'deepseek-chat'

# ============================================
# Mock 开关（True = 本地模拟，不实际调用 DeepSeek）
# 用于 JMeter 压测，避免真实 API 调用带来的延迟和费用
# 切换方式：将下面改为 False → 恢复真实 DeepSeek 调用
# ============================================
MOCK_DEEPSEEK = False

# ============================================
# 基础系统提示词
# ============================================
BASE_SYSTEM_PROMPT = (
    '你是"滩羊智品助手"，一个专业、友好的滩羊养殖与产品咨询 AI。'
    '你可以回答关于滩羊养殖技术、营养价值、烹饪方法、生长周期、盐池滩羊特色等问题。'
    '回答请使用中文，简洁专业，重点突出。'
)


# ============================================
# 直接查库：构建用户专属数据
# ============================================
def _build_user_data_context(user_id):
    """
    直接查数据库，把该用户的所有羊只数据拼成一段文字。
    不走 RAG，不做关键词匹配，简单粗暴但 100% 可靠。
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.warning(f'[QA] user_id={user_id} 不存在')
        return None

    # 只查 paid（认养中，羊仍在农场）的订单
    paid_items = OrderItem.objects.filter(
        order__user_id=user_id,
        order__status='paid'
    ).values_list('sheep_id', flat=True).distinct()
    sheep_ids = list(paid_items)

    # 也统计 shipping/completed 数量，告知 AI 有多少已发货/完成
    other_count = OrderItem.objects.filter(
        order__user_id=user_id,
        order__status__in=['shipping', 'completed']
    ).values_list('sheep_id', flat=True).distinct().count()

    logger.info(f'[QA] 用户 {user.username}(id={user_id}) 认养中IDs={sheep_ids}, 已发货/完成数={other_count}')

    if not sheep_ids and other_count == 0:
        return (
            f'当前用户：{user.username}\n'
            f'领养状态：该用户尚未领养任何滩羊。\n'
            f'提示：请引导用户前往小程序"定制领养"页面挑选心仪的滩羊。'
        )

    # ---------- 拼装完整数据卡片 ----------
    sheep_list = Sheep.objects.filter(id__in=sheep_ids)
    total = sheep_list.count()

    lines = [f'当前用户：{user.username}，目前有 {total} 只滩羊正在农场认养中。']
    if other_count > 0:
        lines.append(f'（另有 {other_count} 只已发货/完成，不在农场，此处不再展示其详情）\n')
    else:
        lines.append('')

    for sheep in sheep_list:
        lines.append(f'===== 羊只 #{sheep.id} =====')
        lines.append(f'耳标号: {sheep.ear_tag or "无"}')
        lines.append(f'性别: {sheep.get_gender_display()}')
        lines.append(f'当前体重: {sheep.weight}kg / 身高: {sheep.height}cm / 体长: {sheep.length}cm')
        lines.append(f'健康状况: {sheep.health_status}')
        lines.append(f'出生日期: {sheep.birth_date or "未知"}')
        lines.append(f'所在农场: {sheep.farm_name or "未知"}')

        # 最近 5 条喂养记录
        feedings = FeedingRecord.objects.filter(sheep=sheep).order_by('-feed_date')[:5]
        if feedings:
            lines.append('最近喂养记录:')
            for f in feedings:
                lines.append(f'  {f.feed_date}: {f.feed_type} {f.amount}{f.unit}')

        # 最近 5 条生长记录
        growths = GrowthRecord.objects.filter(sheep=sheep).order_by('-record_date')[:5]
        if growths:
            lines.append('最近生长记录:')
            for g in growths:
                lines.append(f'  {g.record_date}: 体重{g.weight}kg, 身高{g.height}cm, 体长{g.length}cm')

        # 最近 5 条疫苗记录
        vaccines = VaccinationHistory.objects.filter(sheep=sheep).select_related('vaccine').order_by('-vaccination_date')[:5]
        if vaccines:
            lines.append('疫苗接种记录:')
            for v in vaccines:
                lines.append(f'  {v.vaccination_date}: {v.vaccine.name}')

        lines.append('')  # 空行分隔

    return '\n'.join(lines)


# ============================================
# API 视图
# ============================================
@csrf_exempt
@require_http_methods(["POST"])
def api_qa_ask(request):
    """
    智能问答接口
    POST /api/qa/ask  { "question": "...", "token": "..." }
    """
    start_time = time.time()
    user_id = None
    question = ''
    question_type = 'general'
    source_type = 'general'
    answer = ''
    success = False
    fallback_used = False
    error_message = ''

    def build_response(payload, status=200):
        response_time_ms = int((time.time() - start_time) * 1000)
        _safe_log_qa(
            user_id=user_id,
            question=question,
            question_type=question_type,
            answer=answer,
            success=success,
            fallback_used=fallback_used,
            response_time_ms=response_time_ms,
            source_type=source_type,
            error_message=error_message,
        )
        return JsonResponse(payload, status=status)

    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        question_type = _classify_question_type(question)

        if not question:
            error_message = '问题不能为空'
            return build_response({'code': 400, 'msg': '问题不能为空', 'data': None}, status=400)

        # -------- 1. 识别用户身份 --------
        token = (
            request.headers.get('Authorization', '').replace('Bearer ', '')
            or data.get('token', '')
        )
        logger.info(f'[QA] 收到问题: "{question}", token长度={len(token) if token else 0}')

        if token:
            payload = verify_token(token)
            if payload:
                user_id = payload.get('user_id')
                logger.info(f'[QA] token验证成功, user_id={user_id}')
            else:
                logger.warning('[QA] token验证失败(可能过期)')

        # uid 做兜底：小程序同时存了 uid，万一 token 过期还能识别用户
        if not user_id:
            uid_str = data.get('uid', '')
            if uid_str:
                try:
                    user_id = int(uid_str)
                    logger.info(f'[QA] 通过uid兜底识别用户, user_id={user_id}')
                except (ValueError, TypeError):
                    pass

        # -------- 2. 构建 system prompt --------
        system_prompt = BASE_SYSTEM_PROMPT
        has_user_data = False

        if user_id:
            user_data = _build_user_data_context(user_id)
            if user_data:
                has_user_data = True
                source_type = 'user_data'
                system_prompt += (
                    '\n\n'
                    '【重要】以下是当前登录用户的真实养殖档案数据（来自数据库），'
                    '当用户问到"我的羊""我养了多少""我的羊健康吗"等个人问题时，'
                    '你必须基于以下数据如实回答，不要说"无法获取个人数据"：\n\n'
                    + user_data
                )
        else:
            logger.info('[QA] 未识别到用户身份，使用通用模式')
            system_prompt += (
                '\n\n【注意】当前用户未登录。'
                '如果用户询问"我的羊""我养了多少只""我的饲料记录"等个人相关问题，'
                '请回答："要查询您的专属信息，请先登录小程序（点击底部「我的」页面），登录后我就能告诉您啦！"'
                '不要说"无法获取"或"数据库中没有"，请用友好的方式引导用户登录。'
            )

        # -------- 3. 调用 DeepSeek --------
        logger.info(f'[QA] system_prompt长度={len(system_prompt)}, has_user_data={has_user_data}')
        llm_answer, llm_error_msg = _call_deepseek(system_prompt, question)

        if llm_answer:
            answer = llm_answer
            success = True
            return build_response({
                'code': 0,
                'msg': '成功',
                'data': {
                    'answer': answer,
                    'model': 'deepseek-v3',
                    'context_used': has_user_data,
                    'debug_user_id': user_id,
                }
            })

        logger.warning(f'[QA] DeepSeek失败: {llm_error_msg}，使用本地回答')
        answer = get_local_answer(question)
        success = True
        fallback_used = True
        error_message = llm_error_msg or ''
        return build_response({
            'code': 0,
            'msg': '成功（本地回答）',
            'data': {
                'answer': answer,
                'model': 'local',
                'context_used': False,
            }
        })

    except json.JSONDecodeError:
        error_message = '请求数据格式错误'
        return build_response({'code': 400, 'msg': '请求数据格式错误', 'data': None}, status=400)
    except Exception as e:
        logger.error(f'[QA] 接口异常: {str(e)}', exc_info=True)
        answer = get_local_answer(question)
        success = True
        fallback_used = True
        error_message = str(e)
        return build_response({
            'code': 0,
            'msg': '成功（本地回答）',
            'data': {
                'answer': answer,
                'model': 'local',
                'context_used': False,
            }
        })


# ============================================
# DeepSeek API 调用（简化版：始终 system + user）
# ============================================
def _call_deepseek(system_prompt, question):
    """调用 DeepSeek，返回 (answer, error_msg)

    MOCK_DEEPSEEK = True 时：休眠 1.5~2 秒后返回模拟答案，不发起真实 HTTP 请求。
    MOCK_DEEPSEEK = False 时：走真实 DeepSeek API（生产/真实测试用）。
    """

    # ---- Mock 分支（压测专用，原始代码完整保留在下方）----
    if MOCK_DEEPSEEK:
        sleep_time = random.uniform(1.5, 2.0)  # 模拟 AI 思考延迟 1.5~2 秒
        logger.info(f'[QA] [MOCK] 模拟 DeepSeek 休眠 {sleep_time:.2f}s')
        time.sleep(sleep_time)
        mock_answer = (
            f'【Mock 回答】您好！您问的是："{question}"。\n'
            '这是一条模拟回答，用于压测。实际部署时请将 MOCK_DEEPSEEK 改为 False。\n'
            '滩羊智品助手为您服务，有任何关于滩羊养殖的问题欢迎继续提问！'
        )
        return mock_answer, None

    # ---- 真实 DeepSeek API 调用（MOCK_DEEPSEEK = False 时生效）----
    try:
        if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'your_deepseek_api_key_here':
            return None, '未配置 DEEPSEEK_API_KEY'

        resp = requests.post(
            f'{DEEPSEEK_API_BASE}/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': DEEPSEEK_MODEL,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': question},
                ],
                'temperature': 0.7,
                'max_tokens': 2000,
                'stream': False,
            },
            timeout=30,
        )

        if resp.status_code == 200:
            choices = resp.json().get('choices', [])
            if choices:
                return choices[0]['message']['content'], None
            return None, 'API返回无choices'

        detail = resp.text
        try:
            detail = resp.json().get('error', {}).get('message', detail)
        except Exception:
            pass
        return None, f'HTTP {resp.status_code}: {detail}'

    except requests.exceptions.Timeout:
        return None, 'API请求超时'
    except requests.exceptions.RequestException as e:
        return None, f'网络异常: {e}'
    except Exception as e:
        logger.error(f'[QA] DeepSeek调用异常: {e}', exc_info=True)
        return None, str(e)


def get_local_answer(question):
    """
    本地回答（基于关键词匹配）- 作为备用方案
    """
    if not question:
        return '感谢您的提问！如果您有其他关于滩羊的问题，欢迎继续提问！'
    
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
