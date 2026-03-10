"""Monitor device business logic."""
from django.db.models import Count

from ..models import MonitorDevice, User

ROLE_NORMAL_USER = 0
ROLE_BREEDER = 1
ROLE_ADMIN = 2


class MonitorError(Exception):
    """Monitor business exception."""

    def __init__(self, message, code=400, http_status=400):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)


class MonitorService:
    """Monitor device service layer."""

    @staticmethod
    def _serialize_breeder(user):
        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname or "",
            "mobile": user.mobile or "",
            "is_verified": user.is_verified,
            "monitor_count": getattr(user, "monitor_count", 0),
        }

    @staticmethod
    def _serialize_device(device):
        return {
            "id": device.id,
            "owner_id": device.owner_id,
            "owner_name": device.owner.nickname or device.owner.username,
            "name": device.name,
            "device_code": device.device_code,
            "stream_url": device.stream_url,
            "location": device.location or "",
            "status": device.status,
            "is_active": device.is_active,
            "last_heartbeat": device.last_heartbeat.isoformat() if device.last_heartbeat else None,
            "created_at": device.created_at.isoformat() if device.created_at else None,
            "updated_at": device.updated_at.isoformat() if device.updated_at else None,
        }

    @staticmethod
    def _assert_admin(user):
        if not user or user.role != ROLE_ADMIN:
            raise MonitorError("没有权限执行该操作", code=403, http_status=403)

    @staticmethod
    def _assert_breeder_or_admin(user):
        if not user or user.role not in (ROLE_BREEDER, ROLE_ADMIN):
            raise MonitorError("没有权限访问监控数据", code=403, http_status=403)

    @staticmethod
    def _assert_monitor_viewer(user):
        if not user or user.role not in (ROLE_NORMAL_USER, ROLE_BREEDER, ROLE_ADMIN):
            raise MonitorError("没有权限访问监控数据", code=403, http_status=403)

    @staticmethod
    def list_breeders(user):
        MonitorService._assert_admin(user)

        breeders = (
            User.objects.filter(role=ROLE_BREEDER)
            .annotate(monitor_count=Count("monitor_devices"))
            .order_by("-created_at")
        )
        return [MonitorService._serialize_breeder(item) for item in breeders]

    @staticmethod
    def list_devices(user, breeder_id=None):
        MonitorService._assert_monitor_viewer(user)

        if user.role == ROLE_ADMIN:
            owner_id = breeder_id
        elif user.role == ROLE_BREEDER:
            owner_id = user.id
        else:
            # Mini program normal users can view breeder monitors by selecting a breeder.
            if not breeder_id:
                raise MonitorError("普通用户查看监控时必须传 breeder_id")
            owner = User.objects.filter(id=breeder_id, role=ROLE_BREEDER).first()
            if not owner:
                raise MonitorError("养殖户不存在", code=404, http_status=404)
            owner_id = owner.id

        queryset = MonitorDevice.objects.select_related("owner").all()
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        elif user.role == ROLE_BREEDER:
            queryset = queryset.filter(owner=user)

        queryset = queryset.order_by("-created_at")
        return [MonitorService._serialize_device(item) for item in queryset]

    @staticmethod
    def create_device(user, data):
        MonitorService._assert_breeder_or_admin(user)

        owner_id = data.get("owner_id")
        if user.role == ROLE_BREEDER:
            owner = user
        else:
            if not owner_id:
                raise MonitorError("管理员新增监控时必须传 owner_id")
            owner = User.objects.filter(id=owner_id, role=ROLE_BREEDER).first()
            if not owner:
                raise MonitorError("养殖户不存在", code=404, http_status=404)

        name = (data.get("name") or "").strip()
        device_code = (data.get("device_code") or "").strip()
        stream_url = (data.get("stream_url") or "").strip()
        location = (data.get("location") or "").strip()
        status = (data.get("status") or MonitorDevice.STATUS_OFFLINE).strip()
        is_active = bool(data.get("is_active", True))

        if not name or not device_code or not stream_url:
            raise MonitorError("name、device_code、stream_url 为必填项")
        if status not in dict(MonitorDevice.STATUS_CHOICES):
            raise MonitorError("status 参数不合法")
        if MonitorDevice.objects.filter(device_code=device_code).exists():
            raise MonitorError("设备编号已存在", code=409, http_status=409)

        device = MonitorDevice.objects.create(
            owner=owner,
            name=name,
            device_code=device_code,
            stream_url=stream_url,
            location=location or None,
            status=status,
            is_active=is_active,
        )
        return MonitorService._serialize_device(device)

    @staticmethod
    def update_device(user, device_id, data):
        MonitorService._assert_breeder_or_admin(user)
        device = MonitorDevice.objects.select_related("owner").filter(id=device_id).first()
        if not device:
            raise MonitorError("监控设备不存在", code=404, http_status=404)

        if user.role == ROLE_BREEDER and device.owner_id != user.id:
            raise MonitorError("不能修改其他养殖户的监控设备", code=403, http_status=403)

        if user.role == ROLE_ADMIN and data.get("owner_id"):
            owner = User.objects.filter(id=data.get("owner_id"), role=ROLE_BREEDER).first()
            if not owner:
                raise MonitorError("目标养殖户不存在", code=404, http_status=404)
            device.owner = owner

        name = data.get("name")
        device_code = data.get("device_code")
        stream_url = data.get("stream_url")
        location = data.get("location")
        status = data.get("status")
        is_active = data.get("is_active")

        if name is not None:
            name = name.strip()
            if not name:
                raise MonitorError("name 不能为空")
            device.name = name
        if device_code is not None:
            device_code = device_code.strip()
            if not device_code:
                raise MonitorError("device_code 不能为空")
            duplicated = MonitorDevice.objects.filter(device_code=device_code).exclude(id=device.id).exists()
            if duplicated:
                raise MonitorError("设备编号已存在", code=409, http_status=409)
            device.device_code = device_code
        if stream_url is not None:
            stream_url = stream_url.strip()
            if not stream_url:
                raise MonitorError("stream_url 不能为空")
            device.stream_url = stream_url
        if location is not None:
            device.location = location.strip() or None
        if status is not None:
            status = status.strip()
            if status not in dict(MonitorDevice.STATUS_CHOICES):
                raise MonitorError("status 参数不合法")
            device.status = status
        if is_active is not None:
            device.is_active = bool(is_active)

        device.save()
        return MonitorService._serialize_device(device)

    @staticmethod
    def delete_device(user, device_id):
        MonitorService._assert_breeder_or_admin(user)
        device = MonitorDevice.objects.filter(id=device_id).first()
        if not device:
            raise MonitorError("监控设备不存在", code=404, http_status=404)

        if user.role == ROLE_BREEDER and device.owner_id != user.id:
            raise MonitorError("不能删除其他养殖户的监控设备", code=403, http_status=403)

        device.delete()
        return {"id": device_id}
