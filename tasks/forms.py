from django import forms
from .models import Task
from users.models import CustomUser

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status', 
                 'completion_report', 'worked_hours']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'completion_report': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'title': forms.TextInput(attrs={'class': 'input'}),
            'worked_hours': forms.NumberInput(attrs={'class': 'input', 'step': '0.5'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Style all fields with Bulma classes
        for field_name, field in self.fields.items():
            if field_name not in ['description', 'completion_report']:
                field.widget.attrs.update({'class': 'input'})
        
        # Limit assigned_to choices based on user role
        if user and not user.is_superadmin:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(role='USER')
        
        # Only show completion fields if task is being edited and is completed
        if self.instance and self.instance.pk and self.instance.status != 'COMPLETED':
            self.fields.pop('completion_report')
            self.fields.pop('worked_hours')