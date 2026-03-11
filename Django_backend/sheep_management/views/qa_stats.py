from datetime import timedelta

from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from ..models import QALog
from ..permissions import admin_required


@admin_required
def qa_stats(request):
    period = request.GET.get('period', '7')
    question_type = request.GET.get('question_type', '').strip()

    days = 7
    if period == '1':
        days = 1
    elif period == '30':
        days = 30

    start_time = timezone.now() - timedelta(days=days)

    queryset = QALog.objects.filter(created_at__gte=start_time)
    if question_type in {'personal', 'general'}:
        queryset = queryset.filter(question_type=question_type)

    total_count = queryset.count()
    success_count = queryset.filter(success=True).count()
    fallback_count = queryset.filter(fallback_used=True).count()
    avg_response = queryset.aggregate(avg=Avg('response_time_ms')).get('avg') or 0

    success_rate = (success_count / total_count * 100) if total_count else 0
    fallback_rate = (fallback_count / total_count * 100) if total_count else 0

    # `localdate()` requires an aware datetime and can crash when USE_TZ=False.
    trend_start = timezone.now().date() - timedelta(days=6)
    trend_queryset = QALog.objects.filter(created_at__date__gte=trend_start)
    if question_type in {'personal', 'general'}:
        trend_queryset = trend_queryset.filter(question_type=question_type)

    trend_data_raw = (
        trend_queryset
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    trend_map = {item['day']: item['count'] for item in trend_data_raw}
    trend_data = []
    for i in range(7):
        day = trend_start + timedelta(days=i)
        trend_data.append({'day': day, 'count': trend_map.get(day, 0)})

    max_trend = max([item['count'] for item in trend_data], default=1)

    top_questions = (
        queryset
        .exclude(question='')
        .values('question')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    recent_logs = queryset.select_related('user').order_by('-created_at')[:50]

    context = {
        'period': period,
        'question_type': question_type,
        'stats': {
            'total_count': total_count,
            'success_rate': round(success_rate, 2),
            'avg_response_ms': int(avg_response),
            'fallback_rate': round(fallback_rate, 2),
        },
        'trend_data': trend_data,
        'max_trend': max_trend,
        'top_questions': top_questions,
        'recent_logs': recent_logs,
    }
    return render(request, 'sheep_management/permissions/qa_stats.html', context)
