window.addEventListener('keyup', function (e) {
    if (e.key === "Enter") {
        console.log(e.target.id);
        switch (e.target.id) {
            case 'usuario-filtro-input':
                clicar_botao('usuario-filtro-btn');
                break;
            case 'empresa-filtro-input':
                clicar_botao('empresa-filtro-btn');
                break;
            case 'login-usr':
            case 'login-senha':
                clicar_botao('login-btn');
                break;
        };
    };
});

clicar_botao = function (id) {
    this.document.getElementById(id).click();
};