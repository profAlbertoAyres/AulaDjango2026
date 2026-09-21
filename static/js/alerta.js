function confirmarAcao(botao) {
    const formId = botao.dataset.form;

    Swal.fire({
        title: botao.dataset.titulo || 'Tem certeza?',
        html: botao.dataset.mensagem || 'Deseja continuar com essa ação?',
        icon: botao.dataset.icone || 'warning',
        showCancelButton: true,
        confirmButtonText: botao.dataset.textoConfirmar || 'Confirmar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: botao.dataset.corConfirmar || '#dc3545',
        cancelButtonColor: '#6c757d',
        reverseButtons: true,
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById(formId).submit();
        }
    });
}