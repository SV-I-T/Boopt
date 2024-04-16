window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        abrir_barra_lateral: function (opened) {
            const navbar = document.getElementById('navbar');
            if (opened) {
                navbar.style.visibility = "visible";
                navbar.style.opacity = 1;
            } else {
                navbar.style = "";
            }
            throw window.dash_clientside.PreventUpdate;
        },
        alterar_nav_link: function (_) {
            changeActiveNavLink();
            throw dash_clientside.PreventUpdate;
        },
        bind_valor: function (x) {
            return x;
        },
        ativar: function (x) {
            if (!x) {
                throw window.dash_clientside.PreventUpdate;
            } else {
                return true;
            }
        },
        atualizar_pagina: function (_) {
            location.reload();
            throw window.dash_clientside.PreventUpdate;
        },
        alterar_frase: async function (n_next, n_back, ordem_atual, frases, ordem) {
            const triggered = window.dash_clientside.callback_context['triggered'].map(t => t['prop_id']);
            switch (triggered[0]) {
                case "btn-next.n_clicks":
                    if (n_next) { ordem_atual++; };
                    break
                case "btn-back.n_clicks":
                    if (n_back) { ordem_atual--; };
                    break
            };

            let frase_atual = frases[String(ordem[ordem_atual])];
            let totalFrases = ordem.length;
            let progresso = 100 * (ordem_atual + 1) / totalFrases;
            switch (ordem_atual) {
                case null:
                    disable_next = window.dash_clientside.no_update;
                    disable_back = window.dash_clientside.no_update;
                    break;
                case 0:
                    disable_next = false;
                    disable_back = true;
                    break;
                case (totalFrases - 1):
                    disable_next = true;
                    disable_back = false;
                    break;
                default:
                    disable_next = false;
                    disable_back = false;
                    break;
            }
            document.querySelector('.progress-bar').lastChild.style.width = progresso + "%";

            return [
                ordem_atual,
                frase_atual["frase"],
                frase_atual["valor"],
                disable_next,
                disable_back
            ]
        },
        nota_clicada: async function (nota, ordem_atual, ordem, frases) {
            frases[String(ordem[ordem_atual])]['valor'] = nota;
            return frases;
        },
        check_completado: async function (frases) {
            if (Object.values(frases).map(t => t['valor']).every(Boolean)) {
                return true;
            } else {
                throw window.dash_clientside.PreventUpdate;
            }
        }
    }
});