from django.contrib import messages
from django.db.models import Case, IntegerField, Value, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..models import News
from ..permissions import admin_required


def _with_slot_order(queryset):
    return queryset.annotate(
        slot_order=Case(
            When(top_slot=1, then=Value(1)),
            When(top_slot=2, then=Value(2)),
            When(top_slot=3, then=Value(3)),
            default=Value(99),
            output_field=IntegerField(),
        )
    ).order_by("slot_order", "-published_at", "-id")


@admin_required
def news_list(request):
    status_filter = request.GET.get("status", "")
    search = request.GET.get("search", "").strip()

    items = News.objects.all()
    if status_filter in (News.STATUS_DRAFT, News.STATUS_PUBLISHED):
        items = items.filter(status=status_filter)
    if search:
        items = items.filter(title__icontains=search)

    items = _with_slot_order(items)
    context = {
        "items": items,
        "stats": {
            "total": items.count(),
            "published": items.filter(status=News.STATUS_PUBLISHED).count(),
            "draft": items.filter(status=News.STATUS_DRAFT).count(),
            "top": items.exclude(top_slot__isnull=True).count(),
        },
        "status_filter": status_filter,
        "search": search,
    }
    return render(request, "sheep_management/news/list.html", context)


@admin_required
def news_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        summary = request.POST.get("summary", "").strip()
        cover = request.POST.get("cover", "").strip()
        content = request.POST.get("content", "").strip()
        status = request.POST.get("status", News.STATUS_DRAFT)
        top_slot = request.POST.get("top_slot", "").strip()

        if not title or not summary or not cover or not content:
            messages.error(request, "标题、摘要、封面图和正文均为必填")
            return redirect("news_create")

        if status not in (News.STATUS_DRAFT, News.STATUS_PUBLISHED):
            status = News.STATUS_DRAFT

        parsed_top_slot = None
        if top_slot in ("1", "2", "3") and status == News.STATUS_PUBLISHED:
            parsed_top_slot = int(top_slot)

        item = News(
            title=title,
            summary=summary,
            cover=cover,
            content=content,
            status=status,
            published_at=timezone.now() if status == News.STATUS_PUBLISHED else None,
            top_slot=parsed_top_slot,
        )
        item.save()
        if parsed_top_slot:
            News.objects.filter(top_slot=parsed_top_slot).exclude(pk=item.pk).update(top_slot=None)
        messages.success(request, "资讯创建成功")
        return redirect("news_list")

    return render(
        request,
        "sheep_management/news/form.html",
        {
            "is_edit": False,
            "item": None,
        },
    )


@admin_required
def news_edit(request, pk):
    item = get_object_or_404(News, pk=pk)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        summary = request.POST.get("summary", "").strip()
        cover = request.POST.get("cover", "").strip()
        content = request.POST.get("content", "").strip()
        status = request.POST.get("status", News.STATUS_DRAFT)
        top_slot = request.POST.get("top_slot", "").strip()

        if not title or not summary or not cover or not content:
            messages.error(request, "标题、摘要、封面图和正文均为必填")
            return redirect("news_edit", pk=item.id)

        if status not in (News.STATUS_DRAFT, News.STATUS_PUBLISHED):
            status = News.STATUS_DRAFT

        item.title = title
        item.summary = summary
        item.cover = cover
        item.content = content
        item.status = status

        if status == News.STATUS_PUBLISHED and not item.published_at:
            item.published_at = timezone.now()
        if status == News.STATUS_DRAFT:
            item.published_at = None
            item.top_slot = None
        elif top_slot in ("1", "2", "3"):
            item.top_slot = int(top_slot)
        else:
            item.top_slot = None

        item.save()
        if item.top_slot:
            News.objects.filter(top_slot=item.top_slot).exclude(pk=item.pk).update(top_slot=None)
        messages.success(request, "资讯更新成功")
        return redirect("news_list")

    return render(
        request,
        "sheep_management/news/form.html",
        {
            "is_edit": True,
            "item": item,
        },
    )


@admin_required
def news_delete(request, pk):
    item = get_object_or_404(News, pk=pk)

    if request.method == "POST":
        title = item.title
        item.delete()
        messages.success(request, f"资讯《{title}》已删除")
        return redirect("news_list")

    return render(
        request,
        "sheep_management/news/confirm_delete.html",
        {
            "item": item,
        },
    )


@admin_required
def news_publish(request, pk):
    item = get_object_or_404(News, pk=pk)

    if request.method != "POST":
        return redirect("news_list")

    if item.status == News.STATUS_PUBLISHED:
        messages.info(request, f"资讯《{item.title}》已是发布状态")
        return redirect("news_list")

    item.status = News.STATUS_PUBLISHED
    if not item.published_at:
        item.published_at = timezone.now()
    item.save(update_fields=["status", "published_at"])
    messages.success(request, f"资讯《{item.title}》发布成功")
    return redirect("news_list")


@admin_required
def news_set_top_slot(request, pk):
    item = get_object_or_404(News, pk=pk)

    if request.method != "POST":
        return redirect("news_list")

    slot = request.POST.get("slot", "").strip()
    if slot == "clear":
        item.top_slot = None
        item.save(update_fields=["top_slot"])
        messages.success(request, f"资讯《{item.title}》已取消首页推荐位")
        return redirect("news_list")

    if slot not in ("1", "2", "3"):
        messages.error(request, "推荐位参数无效")
        return redirect("news_list")

    if item.status != News.STATUS_PUBLISHED:
        messages.error(request, "仅已发布资讯可设置首页推荐位")
        return redirect("news_list")

    target_slot = int(slot)
    News.objects.filter(top_slot=target_slot).exclude(pk=item.pk).update(top_slot=None)
    item.top_slot = target_slot
    item.save(update_fields=["top_slot"])
    messages.success(request, f"资讯《{item.title}》已设为首页第{target_slot}条")
    return redirect("news_list")


@admin_required
def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk)
    return render(
        request,
        "sheep_management/news/detail.html",
        {
            "item": item,
        },
    )


@csrf_exempt
@require_http_methods(["GET"])
def api_news_home(request):
    """
    小程序首页资讯：固定返回3条
    优先 top_slot=1/2/3，缺位时用最新已发布资讯补齐。
    """
    try:
        published_qs = News.objects.filter(status=News.STATUS_PUBLISHED)
        slot_items = list(
            published_qs.filter(top_slot__in=[1, 2, 3]).order_by("top_slot")
        )

        used_ids = {n.id for n in slot_items}
        if len(slot_items) < 3:
            fillers = list(
                published_qs.exclude(id__in=used_ids).order_by("-published_at", "-id")[
                    : 3 - len(slot_items)
                ]
            )
            slot_items.extend(fillers)

        result = []
        for idx, item in enumerate(slot_items[:3], start=1):
            result.append(
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "cover": item.cover,
                    "content": item.content,
                    "published_at": item.published_at.strftime("%Y-%m-%d %H:%M:%S")
                    if item.published_at
                    else "",
                    "top_slot": item.top_slot or idx,
                }
            )

        return JsonResponse({"code": 0, "msg": "获取成功", "data": result}, status=200)
    except Exception as e:
        return JsonResponse(
            {"code": 500, "msg": f"服务器错误: {str(e)}", "data": []}, status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def api_news_detail(request, news_id):
    """小程序资讯详情（仅已发布）。"""
    try:
        item = News.objects.filter(
            pk=news_id,
            status=News.STATUS_PUBLISHED,
        ).first()
        if not item:
            return JsonResponse({"code": 404, "msg": "资讯不存在", "data": None}, status=404)

        return JsonResponse(
            {
                "code": 0,
                "msg": "获取成功",
                "data": {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "cover": item.cover,
                    "content": item.content,
                    "published_at": item.published_at.strftime("%Y-%m-%d %H:%M:%S")
                    if item.published_at
                    else "",
                },
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse(
            {"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}, status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def api_news_list(request):
    """小程序资讯列表（已发布）。"""
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 50:
            page_size = 50

        queryset = _with_slot_order(
            News.objects.filter(status=News.STATUS_PUBLISHED)
        )
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        rows = queryset[start:end]

        result = []
        for item in rows:
            result.append(
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "cover": item.cover,
                    "published_at": item.published_at.strftime("%Y-%m-%d %H:%M:%S")
                    if item.published_at
                    else "",
                    "top_slot": item.top_slot,
                }
            )

        return JsonResponse(
            {
                "code": 0,
                "msg": "获取成功",
                "data": {
                    "list": result,
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "has_more": end < total,
                },
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse(
            {"code": 500, "msg": f"服务器错误: {str(e)}", "data": None}, status=500
        )
