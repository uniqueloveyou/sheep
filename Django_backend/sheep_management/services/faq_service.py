import re

from django.db import OperationalError, ProgrammingError
from django.db.models import Q

from ..models import QAPair, QAAlias, QARelated


class FAQService:
    """问答对服务：命中标准问答并返回级联问题。"""

    @staticmethod
    def normalize_question(question):
        # 先做最基础的归一化，避免大小写和多余空格影响匹配。
        return ' '.join((question or '').strip().lower().split())

    @staticmethod
    def _keyword_tokens(question):
        # 把一句问题拆成多个 token，供模糊匹配 question / keywords / aliases 使用。
        normalized = FAQService.normalize_question(question)
        if not normalized:
            return []

        tokens = [normalized]
        split_tokens = re.split(r'[\s,，。！？、;；:/\\|]+', normalized)
        tokens.extend(token for token in split_tokens if token)

        deduped = []
        seen = set()
        for token in tokens:
            token = token.strip()
            if len(token) < 1 or token in seen:
                continue
            seen.add(token)
            deduped.append(token)
        return deduped

    @staticmethod
    def match_question(question):
        # FAQ 命中顺序：
        # 1. 标准问题精确匹配
        # 2. 别名精确匹配
        # 3. 关键词模糊匹配
        question = FAQService.normalize_question(question)
        if not question:
            return None

        try:
            qa = (
                QAPair.objects
                .filter(question__iexact=question, status=True)
                .select_related('category')
                .prefetch_related('details')
                .first()
            )
            if qa:
                return FAQService.build_result(qa)

            alias = (
                QAAlias.objects
                .filter(alias_question__iexact=question, qa_pair__status=True)
                .select_related('qa_pair', 'qa_pair__category')
                .prefetch_related('qa_pair__details')
                .first()
            )
            if alias:
                return FAQService.build_result(alias.qa_pair)

            tokens = FAQService._keyword_tokens(question)
            if not tokens:
                return None

            query = Q()
            for token in tokens:
                # token 只要命中标准问题、关键词或别名中的任意一个，就参与候选。
                query |= Q(question__icontains=token)
                query |= Q(keywords__icontains=token)
                query |= Q(aliases__alias_question__icontains=token)

            qa = (
                QAPair.objects
                .filter(status=True)
                .filter(query)
                .select_related('category')
                .prefetch_related('details')
                .distinct()
                .order_by('-is_hot', 'sort_order', 'id')
                .first()
            )
            if qa:
                return FAQService.build_result(qa)
        except (ProgrammingError, OperationalError):
            # 尚未执行迁移时不阻塞原有 AI 问答流程。
            return None

        return None

    @staticmethod
    def get_related_questions(qa):
        # 返回最多 5 个关联问题，供前端做快捷追问。
        related = (
            QARelated.objects
            .filter(source_qa=qa, target_qa__status=True)
            .select_related('target_qa')
            .order_by('sort_order', 'id')[:5]
        )
        return [item.target_qa.question for item in related]

    @staticmethod
    def get_suggested_questions(limit=6):
        # 推荐问题优先取热门问答，再按排序字段返回。
        try:
            return list(
                QAPair.objects
                .filter(status=True)
                .order_by('-is_hot', 'sort_order', 'id')
                .values_list('question', flat=True)[:limit]
            )
        except (ProgrammingError, OperationalError):
            return []

    @staticmethod
    def build_result(qa):
        # 统一把 ORM 对象整理成接口层可直接返回的结构。
        details = []
        for detail in qa.details.all().order_by('sort_order', 'id'):
            details.append({
                'stage_name': detail.stage_name,
                'weight_range': detail.weight_range,
                'nutrition_value': detail.nutrition_value,
                'cost_value': detail.cost_value,
                'price_value': detail.price_value,
                'description': detail.description,
            })

        return {
            'id': qa.id,
            'category': qa.category.name if qa.category else '',
            'question': qa.question,
            'answer': qa.answer,
            'answer_type': qa.answer_type,
            'month_stage': qa.month_stage,
            'details': details,
            'related_questions': FAQService.get_related_questions(qa),
        }
