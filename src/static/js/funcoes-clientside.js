window.dash_clientside = Object.assign({}, window.dash_clientside, {
    graficos: {
        construir_grafico_etapas: async function (data) {
            if (window.grafico_etapas) {
                window.grafico_etapas.data = data
                window.grafico_etapas.update()
            } else {
                const ctx = document.getElementById('adm-results-vela-etapas')

                window.grafico_etapas = new Chart(ctx, {
                    type: 'bar',
                    data: data,
                    options: {
                        scales: {
                            y: {
                                max: 10, min: 0
                            }
                        },
                        plugins: {
                            datalabels: {
                                formatter: function (value, context) {
                                    return value.toLocaleString()
                                },
                                backgroundColor: "#1618ff",
                                color: "#fff"
                            }
                        }
                    }
                });
            }
            throw window.dash_clientside.PreventUpdate;
        },
        construir_grafico_comps: async function (data) {
            if (window.grafico_comps) {
                window.grafico_comps.data = data
                window.grafico_comps.update()
            } else {
                const ctx = document.getElementById('adm-results-vela-comps')

                window.grafico_comps = new Chart(ctx, {
                    type: 'polarArea',
                    data: data,
                    options: {
                        scales: {
                            r: {
                                max: 10, min: 0
                            }
                        },
                        plugins: {
                            datalabels: {
                                formatter: function (value, context) {
                                    return value.toLocaleString()
                                },
                                backgroundColor: "#1618ff",
                                color: "#fff",
                                align: 'end',
                                anchor: 'end'
                            },
                            legend: { display: false }
                        }
                    }
                });
            }
            throw window.dash_clientside.PreventUpdate;
        },

    },
    interacoes: {
        abrir_barra_lateral: async function (opened) {
            const navbar = document.getElementById('navbar');
            const navbar_backdrop = document.getElementById('navbar-backdrop');
            if (opened) {
                navbar.setAttribute('visible', 'true')
                navbar_backdrop.setAttribute('visible', 'true')
            } else {
                navbar.removeAttribute('visible')
                navbar_backdrop.setAttribute('visible', 'false')
            }
            throw window.dash_clientside.PreventUpdate
        },
        alterar_nav_link: async function (_) {
            changeActiveNavLink()
            throw dash_clientside.PreventUpdate
        },
        ativar: async function (x) {
            if (!x) {
                throw window.dash_clientside.PreventUpdate;
            } else {
                return true;
            }
        },
        atualizar_pagina: async function (_) {
            location.reload();
            throw window.dash_clientside.PreventUpdate;
        },
        selecionar_todos: async function (n, data) {
            if (!n) {
                throw window.dash_clientside.PreventUpdate;
            }
            const values = []
            data.forEach((e) => values.push(e['value']))
            return values
        },
    },
    vela: {
        alterar_frase: async function (n_next, n_back, ordem_atual, frases, ordem) {
            const triggered = window.dash_clientside.callback_context['triggered'].map(t => t['prop_id']);
            switch (triggered[0]) {
                case "btn-next-vela.n_clicks":
                    if (n_next) { ordem_atual++; };
                    break
                case "btn-back-vela.n_clicks":
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
        },
        atualizar_info_video: async function (currentTime, id_video) {
            if (currentTime) {
                console.log('tem tempo definido')
                window.localStorage.setItem('v-curtime-' + id_video, currentTime)
                throw window.dash_clientside.PreventUpdate
            } else {
                console.log('não tem tempo definido')
                return window.localStorage.getItem('v-curtime-' + id_video)
            }
        },
    },
    raiox: {
        alterar_passos_raiox_comprou: function (comprou, passos_comprou, passos_ncomprou) {
            const comprou_bool = Boolean(Number(comprou))
            const r_comprou = []
            const r_ncomprou = []
            passos_comprou.forEach((_) => r_comprou.push(!comprou_bool))
            passos_ncomprou.forEach((_) => r_ncomprou.push(comprou_bool))
            return [r_comprou, r_ncomprou]
        }
    },
    clientside: {
        upload_arquivo_usr_batelada: async function (x) {
            document.getElementById('div-usr-massa-arquivo').style.display = x ? 'block' : 'none'
            return x
        },
        upload_arquivo_empresa_unidades: async function (x) {
            document.getElementById('div-empresa-unidades-arquivo').style.display = x ? 'block' : 'none'
            return x
        },
    }
});