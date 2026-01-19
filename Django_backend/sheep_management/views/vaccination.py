"""疫苗接种记录管理视图"""
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Sheep, VaccinationHistory


def vaccination_list(request):
    """疫苗接种记录列表"""
    sheep_id = request.GET.get('sheep_id', '')
    vaccination_records = VaccinationHistory.objects.all().select_related('sheep')
    
    if sheep_id:
        vaccination_records = vaccination_records.filter(sheep_id=sheep_id)
    
    context = {'vaccination_records': vaccination_records, 'sheep_id': sheep_id}
    return render(request, 'sheep_management/vaccination/list.html', context)


def vaccination_create(request):
    """创建疫苗接种记录"""
    if request.method == 'POST':
        vaccination = VaccinationHistory.objects.create(
            vaccination_id=int(request.POST.get('vaccination_id')),
            sheep_id=int(request.POST.get('sheep_id')),
            vaccination_date=request.POST.get('vaccination_date'),
            expiry_date=request.POST.get('expiry_date'),
            dosage=float(request.POST.get('dosage')),
            administered_by=request.POST.get('administered_by'),
            notes=request.POST.get('notes') or None,
            vaccine_type=request.POST.get('vaccine_type') or None,
        )
        messages.success(request, '疫苗接种记录创建成功！')
        return redirect('vaccination_list')
    
    sheep_list = Sheep.objects.all()
    return render(request, 'sheep_management/vaccination/form.html', {'title': '创建疫苗接种记录', 'sheep_list': sheep_list})

