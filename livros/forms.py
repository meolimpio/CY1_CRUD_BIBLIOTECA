"""Formulários do app livros."""

from django import forms

from .models import Livro


class LivroForm(forms.ModelForm):
    """Formulário usado tanto para cadastro quanto para edição de livros."""

    class Meta:
        model = Livro
        fields = [
            'titulo',
            'autor',
            'editora',
            'categoria',
            'quantidade_exemplares',
            'status',
            'capa',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Ex.: Dom Casmurro',
                'autocomplete': 'off',
            }),
            'autor': forms.TextInput(attrs={
                'placeholder': 'Ex.: Machado de Assis',
                'autocomplete': 'off',
            }),
            'editora': forms.TextInput(attrs={
                'placeholder': 'Ex.: Editora Ática',
                'autocomplete': 'off',
            }),
            'categoria': forms.TextInput(attrs={
                'placeholder': 'Ex.: Romance, Ficção, Didático',
                'autocomplete': 'off',
            }),
            'quantidade_exemplares': forms.NumberInput(attrs={
                'min': '0',
                'placeholder': 'Ex.: 5',
            }),
            'status': forms.Select(),
            'capa': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'data-preview-input': 'true',
            }),
        }
        labels = {
            'titulo': 'Título',
            'autor': 'Autor',
            'editora': 'Editora',
            'categoria': 'Gênero/Categoria',
            'quantidade_exemplares': 'Quantidade de exemplares',
            'status': 'Status do livro',
            'capa': 'Capa do livro',
        }
        help_texts = {
            'capa': 'Envie uma imagem nos formatos mais comuns, como JPG ou PNG. O envio é opcional.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = 'campo-formulario'
            if field_name == 'capa':
                css_class = 'campo-formulario campo-upload'
            field.widget.attrs['class'] = css_class

    def clean_quantidade_exemplares(self):
        quantidade = self.cleaned_data.get('quantidade_exemplares')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError('A quantidade de exemplares não pode ser negativa.')
        return quantidade
