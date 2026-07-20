from django import forms
from .models import Resume


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'accept': '.pdf,.png,.jpg,.jpeg,.docx,.txt,.bmp,.tiff',
                }
            ),
        }


class SearchConfigForm(forms.Form):
    platforms = forms.MultipleChoiceField(
        label='سامانه‌های کاریابی',
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'platform-checkbox'}
        ),
        choices=[
            ('jobvision', 'جاب‌ویژن'),
            ('e_estekhdam', 'ای‌استخدام'),
            ('irantalent', 'ایران‌تلنت'),
        ],
        initial=['jobvision'],
    )

    city = forms.ChoiceField(
        label='شهر',
        widget=forms.Select(attrs={'class': 'form-select'}),
        choices=[
            ('', 'همه شهرها'),
            ('تهران', 'تهران'),
            ('اصفهان', 'اصفهان'),
            ('البرز', 'البرز (کرج)'),
            ('خراسان رضوی', 'خراسان رضوی (مشهد)'),
            ('فارس', 'فارس (شیراز)'),
            ('خوزستان', 'خوزستان (اهواز)'),
            ('گیلان', 'گیلان (رشت)'),
            ('مازندران', 'مازندران (ساری)'),
            ('آذربایجان شرقی', 'آذربایجان شرقی (تبریز)'),
            ('آذربایجان غربی', 'آذربایجان غربی (ارومیه)'),
            ('کرمان', 'کرمان'),
            ('هرمزگان', 'هرمزگان (بندرعباس)'),
            ('یزد', 'یزد'),
            ('مرکزی', 'مرکزی (اراک)'),
            ('گلستان', 'گلستان (گرگان)'),
            ('سمنان', 'سمنان'),
            ('کرمانشاه', 'کرمانشاه'),
            ('همدان', 'همدان'),
            ('لرستان', 'لرستان (خرم‌آباد)'),
            ('بوشهر', 'بوشهر'),
            ('زنجان', 'زنجان'),
            ('اردبیل', 'اردبیل'),
            ('سایر', 'سایر شهرها'),
        ],
        required=False,
    )

    level = forms.ChoiceField(
        label='سطح کاری',
        widget=forms.Select(attrs={'class': 'form-select'}),
        choices=[
            ('all', 'همه سطوح'),
            ('junior', 'جونیور / کارآموز'),
            ('mid', 'می‌لول'),
            ('senior', 'سنیور / ارشد'),
            ('manager', 'مدیر'),
        ],
        initial='all',
    )

    time_range = forms.ChoiceField(
        label='بازه زمانی',
        widget=forms.Select(attrs={'class': 'form-select'}),
        choices=[
            ('1', '۱ روز گذشته'),
            ('3', '۳ روز گذشته'),
            ('7', '۷ روز گذشته'),
            ('14', '۱۴ روز گذشته'),
            ('30', '۳۰ روز گذشته'),
            ('all', 'همه'),
        ],
        initial='7',
    )

    custom_keywords = forms.CharField(
        label='کلمات کلیدی اضافی (اختیاری)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: Python, Django, React',
        }),
        required=False,
    )