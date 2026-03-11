from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import News
from ..permissions import admin_required


@admin_required
def news_list(request):
    status_filter = request.GET.get("status", "")
    search = request.GET.get("search", "").strip()

    items = News.objects.all()
    if status_filter in (News.STATUS_DRAFT, News.STATUS_PUBLISHED):
        items = items.filter(status=status_filter)
    if search:
        items = items.filter(title__icontains=search)

    items = items.order_by("-published_at", "-id")
    context = {
        "items": items,
        "stats": {
            "total": items.count(),
            "published": items.filter(status=News.STATUS_PUBLISHED).count(),
            "draft": items.filter(status=News.STATUS_DRAFT).count(),
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

        if not title or not summary or not cover or not content:
            messages.error(request, "标题、摘要、封面图和正文均为必填")
            return redirect("news_create")

        if status not in (News.STATUS_DRAFT, News.STATUS_PUBLISHED):
            status = News.STATUS_DRAFT

        item = News(
            title=title,
            summary=summary,
            cover=cover,
            content=content,
            status=status,
            published_at=timezone.now() if status == News.STATUS_PUBLISHED else None,
        )
        item.save()
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

        item.save()
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
    item.published_at = timezone.now()
    item.save(update_fields=["status", "published_at"])
    messages.success(request, f"资讯《{item.title}》发布成功")
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
