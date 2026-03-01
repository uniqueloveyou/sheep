import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Django_backend.settings'
django.setup()

from sheep_management.models import Coupon, User

breeders = User.objects.filter(role=1)
print('Breeders:', [(b.id, b.username) for b in breeders])

coupons = Coupon.objects.filter(owner__isnull=True)
print('Coupons without owner:', coupons.count())

if breeders.exists() and coupons.exists():
    first_breeder = breeders.first()
    updated = coupons.update(owner=first_breeder)
    print(f'Backfilled {updated} coupons with breeder {first_breeder.id} ({first_breeder.username})')
else:
    print('No backfill needed')
