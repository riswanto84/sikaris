from django import forms

class ImportFileForm(forms.Form):
    file = forms.FileField(
        label='Upload file Excel/CSV',
        help_text='Format yang didukung: .xlsx, .xlsm, .csv',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xlsm,.csv',
        })
    )
