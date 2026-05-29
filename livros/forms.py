"""Formulários do app livros."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from django.utils import timezone

from .models import Emprestimo, Livro, Reserva


class LoginForm(AuthenticationForm):
    """Formulário personalizado para login."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'campo-formulario',
            'placeholder': 'Digite seu usuário',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'campo-formulario',
            'placeholder': 'Digite sua senha',
            'autocomplete': 'current-password',
        })


class LivroForm(forms.ModelForm):
    """Formulário usado tanto para cadastro quanto para edição de livros."""

    class Meta:
        model = Livro
        fields = [
            'titulo',
            'autor',
            'editora',
            'categoria',
            'quantidade_total',
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
            'quantidade_total': forms.NumberInput(attrs={
                'min': '0',
                'placeholder': 'Ex.: 5',
            }),
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
            'quantidade_total': 'Quantidade total',
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

    def clean_quantidade_total(self):
        quantidade = self.cleaned_data.get('quantidade_total')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError('A quantidade total não pode ser negativa.')
        return quantidade


class EmprestimoForm(forms.ModelForm):
    """Formulário para registrar empréstimos."""

    class Meta:
        model = Emprestimo
        fields = ['livro', 'nome_leitor', 'data_prevista_devolucao']
        widgets = {
            'livro': forms.Select(),
            'nome_leitor': forms.TextInput(attrs={
                'placeholder': 'Nome do leitor',
                'autocomplete': 'off',
            }),
            'data_prevista_devolucao': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'livro': 'Livro',
            'nome_leitor': 'Leitor',
            'data_prevista_devolucao': 'Previsão de devolução',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['livro'].queryset = Livro.objects.all()
        for field in self.fields.values():
            field.widget.attrs['class'] = 'campo-formulario'

    def clean_data_prevista_devolucao(self):
        data_prevista = self.cleaned_data.get('data_prevista_devolucao')
        if data_prevista and data_prevista < timezone.localdate():
            raise forms.ValidationError('A previsão de devolução não pode estar no passado.')
        return data_prevista

    def clean_livro(self):
        livro = self.cleaned_data.get('livro')
        if livro and not livro.tem_disponibilidade:
            raise forms.ValidationError('Este livro não possui exemplares disponíveis para empréstimo.')
        return livro


class ReservaForm(forms.ModelForm):
    """Formulário para registrar reservas."""

    class Meta:
        model = Reserva
        fields = ['livro', 'nome_leitor']
        widgets = {
            'livro': forms.Select(),
            'nome_leitor': forms.TextInput(attrs={
                'placeholder': 'Nome do leitor',
                'autocomplete': 'off',
            }),
        }
        labels = {
            'livro': 'Livro',
            'nome_leitor': 'Leitor',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['livro'].queryset = Livro.objects.all()
        for field in self.fields.values():
            field.widget.attrs['class'] = 'campo-formulario'

    def clean_livro(self):
        livro = self.cleaned_data.get('livro')
        if livro and not livro.tem_disponibilidade:
            raise forms.ValidationError('Este livro não possui exemplares disponíveis para reserva.')
        return livro
