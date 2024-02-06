window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        abrir_modal_novo_usr: function (n) {
            if (!n) {
                throw window.dash_clientside.PreventUpdate;
            } else {
                return true;
            }
        },
        iniciar_teste: function (n) {
            if (!n) {
                throw window.dash_clientside.PreventUpdate;
            } else {
                return [true, 0];
            }
        },
        alterar_frase: function (n_next, n_back, ordem_atual) {
            var triggered = window.dash_clientside.callback_context['triggered'].map(t => t['prop_id']);
            switch (triggered[0]) {
                case "btn-next.n_clicks":
                    if (n_next) { return ordem_atual + 1; } else { throw window.dash_clientside.PreventUpdate; }
                case "btn-back.n_clicks":
                    if (n_back) { return ordem_atual - 1; } else { throw window.dash_clientside.PreventUpdate; }
                default:
                    throw window.dash_clientside.PreventUpdate;
            }
        },
        atualizar_componentes_frase: function (ordem_atual, frases, ordem) {
            var frase_atual = frases[String(ordem[ordem_atual])];
            var totalFrases = ordem.length;
            var progresso = 100 * (ordem_atual + 1) / totalFrases;
            var textoProgresso = ((ordem_atual + 1) + '/' + totalFrases);
            if (ordem_atual === null) {
                disable_next = window.dash_clientside.no_update;
                disable_back = window.dash_clientside.no_update;
            } else if (ordem_atual === 0) {
                disable_next = false;
                disable_back = true;
            } else if (ordem_atual === (totalFrases - 1)) {
                disable_next = true;
                disable_back = false;
            } else {
                disable_next = false;
                disable_back = false;
            };
            return [
                frase_atual["frase"], frase_atual["valor"],
                disable_next, disable_back,
                progresso, textoProgresso
            ];
        },
        nota_clicada: function (nota, ordem_atual, ordem, frases) {
            frases[String(ordem[ordem_atual])]['valor'] = nota;
            return frases;
        },
        check_completado: function (frases) {
            if (Object.values(frases).map(t => t['valor']).every(Boolean)) {
                return true;
            } else {
                throw window.dash_clientside.PreventUpdate;
            }
        }
    }
});