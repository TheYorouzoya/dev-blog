from datetime import datetime

from django import forms

from .models import Article, ArticleImage

class Html5DateInput(forms.DateInput):
    input_type = 'date'

class ArticleForm(forms.ModelForm):
    image_ids = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Article
        fields = ['title', 'status', 'topic', 'tags', 'published_at', 'content', 'excerpt']
        widgets = {
            'published_at': Html5DateInput(attrs={'required': False}),
            'content': forms.HiddenInput,
            'excerpt': forms.HiddenInput,
        }

    def clean_published_at(self):
        published_at = self.cleaned_data['published_at']
        status = self.cleaned_data['status']

        # during editing
        if self.instance and self.instance.pk:
            if status == Article.Status.SCHEDULED:
                original_date = self.instance.published_at
                if published_at.date() < original_date.date():
                    raise forms.ValidationError("Publish date cannot be in the past!")
                return published_at

        # during creation
        if status == Article.Status.PUBLISHED and published_at.date() < datetime.now().date():
            raise forms.ValidationError("Publish date cannot be in the past!")
        return published_at
    

class ArticleImageForm(forms.ModelForm):
    class Meta:
        model = ArticleImage
        fields = ['article', 'image']