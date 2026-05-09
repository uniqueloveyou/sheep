"""
RAG检索增强生成服务
从数据库检索相关养殖档案数据，作为LLM的上下文
支持用户维度检索：根据用户领养的羊只，检索专属数据
"""
import logging
from django.db.models import Q
from ..models import Sheep, GrowthRecord, FeedingRecord, VaccinationHistory, OrderItem

logger = logging.getLogger(__name__)


class RAGService:
    """RAG检索增强生成服务"""
    
    @staticmethod
    def retrieve_context(question, user_id=None):
        """
        根据问题检索相关上下文
        核心策略：登录用户有领养记录 → 始终带上用户专属数据（不管问什么）
        """
        context_parts = []
        
        # ========== 第一步：始终尝试获取用户专属数据 ==========
        user_sheep_ids = RAGService._get_user_sheep_ids(user_id) if user_id else []
        logger.info(f'[RAG] user_id={user_id}, 领养羊只IDs={user_sheep_ids}')
        
        if user_sheep_ids:
            # 只要有领养记录，始终注入用户羊只基本信息
            sheep_context = RAGService._retrieve_user_sheep_data(user_sheep_ids)
            if sheep_context:
                context_parts.append(sheep_context)
            
            # 始终注入最近的喂养、生长、疫苗记录
            feeding_context = RAGService._retrieve_user_feeding_data(user_sheep_ids)
            if feeding_context:
                context_parts.append(feeding_context)
            
            growth_context = RAGService._retrieve_user_growth_data(user_sheep_ids)
            if growth_context:
                context_parts.append(growth_context)
            
            vaccine_context = RAGService._retrieve_user_vaccine_data(user_sheep_ids)
            if vaccine_context:
                context_parts.append(vaccine_context)
        elif user_id:
            # 已登录但没有领养记录，告诉 AI 这个事实
            context_parts.append('【用户信息】\n当前用户已登录，但尚未领养任何滩羊。请引导用户前往小程序"定制领养"页面挑选心仪的滩羊。')
        
        # ========== 第二步：根据关键词补充通用数据 ==========
        keywords = RAGService._extract_keywords(question)
        if keywords:
            # 只补充用户专属检索没有覆盖到的数据
            if not user_sheep_ids:
                # 未登录或无领养：走通用检索
                sheep_context = RAGService._retrieve_sheep_data(keywords)
                if sheep_context:
                    context_parts.append(sheep_context)
                
                growth_context = RAGService._retrieve_growth_data(keywords)
                if growth_context:
                    context_parts.append(growth_context)
                
                feeding_context = RAGService._retrieve_feeding_data(keywords)
                if feeding_context:
                    context_parts.append(feeding_context)
                
                vaccine_context = RAGService._retrieve_vaccine_data(keywords)
                if vaccine_context:
                    context_parts.append(vaccine_context)
            
        logger.info(f'[RAG] 检索到 {len(context_parts)} 段上下文')
        
        # 合并上下文
        if context_parts:
            return '\n\n'.join(context_parts)
        return None

    # ========== 用户专属检索方法 ==========

    @staticmethod
    def _get_user_sheep_ids(user_id):
        """
        获取用户领养的羊只ID列表
        通过 OrderItem 关联已支付/完成的订单
        """
        try:
            sheep_ids = list(
                OrderItem.objects.filter(
                    order__user_id=user_id,
                    order__status__in=['paid', 'adopting', 'ready_to_ship', 'shipping', 'completed']
                ).values_list('sheep_id', flat=True).distinct()
            )
            return sheep_ids
        except Exception as e:
            logger.error(f'获取用户羊只列表失败: {str(e)}')
            return []

    @staticmethod
    def _retrieve_user_sheep_data(sheep_ids):
        """检索用户领养的羊只基本信息"""
        try:
            sheep_list = list(Sheep.objects.filter(id__in=sheep_ids).select_related('owner'))
            if not sheep_list:
                return None
            
            count = len(sheep_list)
            context = f"【您领养的滩羊信息（共领养了 {count} 只）】\n"
            for sheep in sheep_list:
                context += f"- 羊只#{sheep.id}, 耳标: {sheep.ear_tag or '无'}, "
                context += f"性别: {sheep.get_gender_display()}, "
                context += f"体重: {sheep.current_weight}kg, 体高: {sheep.current_height}cm, 体长: {sheep.current_length}cm, 羊龄: {sheep.age_display}, "
                context += f"健康状况: {sheep.health_status}, "
                context += f"出生日期: {sheep.birth_date or '未知'}, "
                context += f"所在农场: {sheep.farm_name or '未知'}\n"
            
            return context
        except Exception as e:
            logger.error(f'检索用户羊只数据失败: {str(e)}')
            return None

    @staticmethod
    def _retrieve_user_feeding_data(sheep_ids):
        """检索用户羊只的喂养记录"""
        try:
            records = FeedingRecord.objects.filter(
                sheep_id__in=sheep_ids
            ).select_related('sheep').order_by('-feed_date')[:20]
            
            if not records:
                return None
            
            context = "【您的滩羊喂养记录】\n"
            for record in records:
                context += f"- 羊只#{record.sheep_id}: "
                context += f"{record.feed_date} 投喂 {record.feed_type} {record.amount}{record.unit}\n"
            
            return context
        except Exception as e:
            logger.error(f'检索用户喂养记录失败: {str(e)}')
            return None

    @staticmethod
    def _retrieve_user_growth_data(sheep_ids):
        """检索用户羊只的生长记录"""
        try:
            records = GrowthRecord.objects.filter(
                sheep_id__in=sheep_ids
            ).select_related('sheep').order_by('-record_date')[:20]
            
            if not records:
                return None
            
            context = "【您的滩羊生长记录】\n"
            for record in records:
                context += f"- 羊只#{record.sheep_id}: "
                context += f"{record.record_date} 体重{record.weight}kg, "
                context += f"体高{record.height}cm, 体长{record.length}cm\n"
            
            return context
        except Exception as e:
            logger.error(f'检索用户生长记录失败: {str(e)}')
            return None

    @staticmethod
    def _retrieve_user_vaccine_data(sheep_ids):
        """检索用户羊只的疫苗接种记录"""
        try:
            records = VaccinationHistory.objects.filter(
                sheep_id__in=sheep_ids
            ).select_related('sheep', 'vaccine').order_by('-vaccination_date')[:20]
            
            if not records:
                return None
            
            context = "【您的滩羊疫苗接种记录】\n"
            for record in records:
                context += f"- 羊只#{record.sheep_id}: "
                context += f"{record.vaccination_date} 接种 {record.vaccine.name}, "
                context += f"剂量{record.dosage}ml, 有效期至{record.expiry_date}\n"
            
            return context
        except Exception as e:
            logger.error(f'检索用户疫苗记录失败: {str(e)}')
            return None
    
    @staticmethod
    def _extract_keywords(question):
        """
        从问题中提取关键词
        :param question: 用户问题
        :return: list 关键词列表
        """
        keywords = []
        
        # 养殖相关关键词
        if any(word in question for word in ['养殖', '饲养', '喂养', '饲料', '草料']):
            keywords.append('feeding')
        
        # 生长相关关键词
        if any(word in question for word in ['生长', '体重', '体高', '身高', '体长', '周期', '发育', '羊龄', '周龄']):
            keywords.append('growth')
        
        # 疫苗相关关键词
        if any(word in question for word in ['疫苗', '接种', '预防', '驱虫', '防疫']):
            keywords.append('vaccine')
        
        # 健康相关关键词
        if any(word in question for word in ['健康', '疾病', '生病', '治疗']):
            keywords.append('health')
        
        # 滩羊相关关键词
        if any(word in question for word in ['滩羊', '盐池', '特点', '特色']):
            keywords.append('sheep_info')
        
        return keywords
    
    @staticmethod
    def _retrieve_sheep_data(keywords):
        """
        检索羊只基本信息
        """
        if 'sheep_info' not in keywords:
            return None
        
        try:
            # 获取最近添加的羊只信息（示例数据）
            sheep_list = Sheep.objects.all()[:5]
            
            if not sheep_list:
                return None
            
            context = "【羊只基本信息】\n"
            for sheep in sheep_list:
                context += f"- 耳标: {sheep.ear_tag or '无'}, 性别: {sheep.get_gender_display()}, "
                context += f"体重: {sheep.current_weight}kg, "
                context += f"体高: {sheep.current_height}cm, 体长: {sheep.current_length}cm, 羊龄: {sheep.age_display}, "
                context += f"健康状况: {sheep.health_status}\n"
            
            return context
        except Exception as e:
            logger.error(f'检索羊只数据失败: {str(e)}')
            return None
    
    @staticmethod
    def _retrieve_growth_data(keywords):
        """
        检索生长记录
        """
        if 'growth' not in keywords:
            return None
        
        try:
            # 获取最近的生长记录
            growth_records = GrowthRecord.objects.all().order_by('-record_date')[:10]
            
            if not growth_records:
                return None
            
            context = "【生长记录示例】\n"
            for record in growth_records:
                context += f"- 日期: {record.record_date}, "
                context += f"体重: {record.weight}kg, "
                context += f"体高: {record.height}cm, "
                context += f"体长: {record.length}cm\n"
            
            return context
        except Exception as e:
            logger.error(f'检索生长记录失败: {str(e)}')
            return None
    
    @staticmethod
    def _retrieve_feeding_data(keywords):
        """
        检索喂养记录
        """
        if 'feeding' not in keywords:
            return None
        
        try:
            # 获取最近的喂养记录
            feeding_records = FeedingRecord.objects.all().order_by('-feed_date')[:10]
            
            if not feeding_records:
                return None
            
            context = "【喂养记录示例】\n"
            for record in feeding_records:
                context += f"- 饲料类型: {record.feed_type}, "
                context += f"喂养日期: {record.feed_date}, "
                context += f"数量: {record.amount}{record.unit}\n"
            
            return context
        except Exception as e:
            logger.error(f'检索喂养记录失败: {str(e)}')
            return None
    
    @staticmethod
    def _retrieve_vaccine_data(keywords):
        """
        检索疫苗接种记录
        """
        if 'vaccine' not in keywords:
            return None
        
        try:
            # 获取最近的疫苗接种记录
            vaccine_records = VaccinationHistory.objects.all().order_by('-vaccination_date')[:10]
            
            if not vaccine_records:
                return None
            
            context = "【疫苗接种记录示例】\n"
            for record in vaccine_records:
                context += f"- 疫苗: {record.vaccine.name}, "
                context += f"接种日期: {record.vaccination_date}, "
                context += f"过期日期: {record.expiry_date}, "
                context += f"剂量: {record.dosage}ml\n"
            
            return context
        except Exception as e:
            logger.error(f'检索疫苗记录失败: {str(e)}')
            return None
    
    @staticmethod
    def build_rag_prompt(question, context, is_user_query=False):
        """
        构建RAG提示词
        :param question: 用户问题
        :param context: 检索到的上下文
        :param is_user_query: 是否为用户专属数据查询
        :return: str 完整的提示词
        """
        if context:
            if is_user_query:
                return f"""你是一个专业的滩羊养殖和产品咨询助手。

以下是从养殖档案数据库中检索到的【当前用户领养的滩羊】的真实数据：

{context}

【用户问题】
{question}

【回答要求】
1. 基于上述数据库中搜索到的用户专属数据回答问题
2. 回答时说“根据您的滩羊档案记录”开头，让用户知道是基于真实数据
3. 用口语化、友好的方式概括数据，而不是简单列举原始数据
4. 如果数据不足以回答，请说明并提供一般性建议
5. 回答要专业、准确、友好"""
            else:
                return f"""你是一个专业的滩羊养殖和产品咨询助手。

以下是从养殖档案数据库中检索到的相关数据，请基于这些真实数据回答用户的问题：

【检索到的上下文数据】
{context}

【用户问题】
{question}

【回答要求】
1. 请基于上述真实数据回答问题，避免编造信息
2. 如果数据不足以回答，请说明并提供一般性建议
3. 回答要专业、准确、友好
4. 如果问题不在数据范围内，请礼貌说明"""
        else:
            return f"""你是一个专业的滩羊养殖和产品咨询助手。

【用户问题】
{question}

【回答要求】
1. 请用中文回答用户关于滩羊的问题，包括养殖、营养、烹饪等方面
2. 回答要专业、准确、友好
3. 如果问题不在你的知识范围内，请礼貌说明"""
