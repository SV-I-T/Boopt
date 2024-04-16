window.addEventListener('keyup', function (e) {
    if (e.key === "Enter") {
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

function changeActiveNavLink() {
    document.querySelectorAll('.mantine-NavLink-root').forEach(el => {
        (document.location.pathname.startsWith(el.getAttribute('href'))) ? el.setAttribute('data-active', true) : el.removeAttribute('data-active');
    });
}

const observeUrlChange = () => {
    let oldPath = document.location.pathname;
    const body = document.querySelector("body");
    const observer = new MutationObserver(mutations => {
        if (oldPath !== document.location.pathname) {
            oldPath = document.location.pathname;
            changeActiveNavLink();
        }
    });
    observer.observe(body, { childList: true, subtree: true });
};

window.onload = observeUrlChange;