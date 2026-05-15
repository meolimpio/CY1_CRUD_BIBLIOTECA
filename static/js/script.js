document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.navbar-toggle');
    const menu = document.querySelector('.navbar-menu');
    const usuario = document.querySelector('.usuario-navbar');

    if (toggle && menu) {
        toggle.addEventListener('click', () => {
            const aberto = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', String(!aberto));
            menu.classList.toggle('aberto');
            if (usuario) usuario.classList.toggle('aberto');
        });
    }

    document.querySelectorAll('.mensagem-fechar').forEach((botao) => {
        botao.addEventListener('click', () => {
            const mensagem = botao.closest('.mensagem');
            if (mensagem) mensagem.remove();
        });
    });

    document.querySelectorAll('[data-confirm-delete="true"]').forEach((formulario) => {
        formulario.addEventListener('submit', (event) => {
            const confirmado = window.confirm('Tem certeza de que deseja excluir este livro? Essa ação não poderá ser desfeita.');
            if (!confirmado) event.preventDefault();
        });
    });

    const campoBusca = document.querySelector('input[type="search"]');
    if (campoBusca) {
        campoBusca.addEventListener('input', () => {
            campoBusca.classList.toggle('campo-destacado', campoBusca.value.trim().length > 0);
        });
        campoBusca.classList.toggle('campo-destacado', campoBusca.value.trim().length > 0);
    }

    document.querySelectorAll('select[data-auto-submit="true"]').forEach((select) => {
        select.addEventListener('change', () => {
            const form = select.closest('form');
            if (form) form.submit();
        });
    });

    const inputCapa = document.querySelector('input[type="file"][data-preview-input="true"]');
    const imagemPreview = document.querySelector('[data-preview-image]');
    const placeholderPreview = document.querySelector('[data-preview-placeholder]');

    if (inputCapa && imagemPreview) {
        inputCapa.addEventListener('change', () => {
            const arquivo = inputCapa.files && inputCapa.files[0];
            if (!arquivo) return;

            if (!arquivo.type.startsWith('image/')) {
                inputCapa.value = '';
                window.alert('Selecione um arquivo de imagem válido.');
                return;
            }

            const leitor = new FileReader();
            leitor.addEventListener('load', () => {
                imagemPreview.src = leitor.result;
                imagemPreview.hidden = false;
                if (placeholderPreview) placeholderPreview.hidden = true;
            });
            leitor.readAsDataURL(arquivo);
        });
    }
});
