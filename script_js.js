// publico/script_js.js
document.addEventListener('DOMContentLoaded', () => {
    const formulario = document.getElementById('formDados');
    const areaMensagem = document.getElementById('mensagem');
    const inputRegiao = document.getElementById('regiao');
    const feedbackRegiao = document.getElementById('feedback_regiao');

    // Mapeamento de regiões para o feedback visual (copia do REGIONS do Python)
    const MAPA_REGIOES = {
        '10': 'REGIAO 1', '12': 'COMPER - CUIABA', '13': 'COMPER - SAO PAULO',
        '14': 'COMPER - SIDROLANDIA', '15': 'COMPER - ROCHEDO', '16': 'COMPER - TRES LAGOAS',
        '20': 'REGIAO 2 - SIDROLANDIA', '22': 'PIRES SID.B', '23': 'PIRES SID.B',
        '24': 'PIRES CENTRO', '25': 'PIRES SAO PAULO.A', '251': 'REDE SAO BENTO SID.A',
        '252': 'REDE SAO BENTO CENTR', '254': 'REDE SAO BENTO SAO.A', '255': 'REDE SAO BENTO SAO.B',
        '26': 'PIRES SAO PAULO.B', '27': 'PIRES ROCHEDO', '28': 'PIRES ITURAMA',
        '29': 'PIRES GUAICURUS', '30': 'REGIAO 3 - CUIABA.A', '300': 'TRES LAGOAS BRASIL',
        '301': 'RIBAS DO RIO PARDO', '302': 'CUIABA', '303': 'TRES LAGOAS - SM NV',
        '304': 'TRES LAGOAS - SM NV', '305': 'TRES LAGOAS - SM NV',
        '306': 'TRES LAGOAS - SM NV', '307': 'SUPERM.THOME - D.LAND',
        '31': 'AMAMBAI - SETE QUEDA', '32': 'PONTA PORA', '320': 'ANDRE RICARDO PONTA',
        '321': 'PARANAIBA', '330': 'AQUIDAUANA - ANASTAC', '330': 'DAMASCENO AQUIDAUANA',
        '331': 'MIRANDA - BODOQUENA', '335': 'ABV DOURADOS', '336': 'ABV C.D.COMERCIO',
        '338': 'OLIVEIRA AQUIDAUANA-CH', '339': 'VERATI COSTA RICA/CH',
        '34': 'CORUMBA - L.ACORBA', '340': 'CORUMBA - QUADRI/FER', '341': 'VERATI CORUMBA',
        '342': 'REDE COMPER DOURADOS', '35': 'DOURADOS', '36': 'NOVA DOURADA',
        '37': 'RIO BRILHANTE', '38': 'SIDROLANDIA RIO BRILH',
        '39': 'CHAPADAO', '390': 'CHAPADAO - COSTA RICA', '391': 'REGIAO 4 - ROCHEDO',
        '40': 'PARANAIBA - SELVIRIA', '41': 'RIO VERDE - SONORA',
        '410': 'BENFICA - SAO GABRIE', '411': 'BENFICA - SAO GABRIE',
        '413': 'COXIM RIO NEGRO', '415': 'REDE CUIABA B', '418': 'REDE CENTRO',
        '419': 'REDE FARMACIA FREIRE', '42': 'NAVIRAI', '421': 'REDE TRAZZI',
        '423': 'REDE TRAZZI SIDRO E', '426': 'REDE L.AGOAS E SAO JO',
        '427': 'OLIVEIRA CARNEIRO', '428': 'SAIDA SIDROLANDIA C',
        '43': 'MUNDO NOVO - J.GUAIR', '44': 'FATIMA DO SUL - DEOD',
        '441': 'ANHEMA NOVA ALIANCA', '45': 'NOVA ANDRADINA - BAT',
        '450': 'BATAGUASSU - SANTA R', '451': 'BELA VISTA - BONITOM',
        '47': 'BONITO - NIOAQUE', '48': 'MARACAJU', '49': 'GRANDES REDES DOURAD',
        '50': 'REGIAO 5 - CENTRO', '51': 'CAMPO PUJA - BANDEI. JAR',
        '60': 'REGIAO 6 - SAO PAULO', '600': 'SAO BENTO', '70': 'REGIAO 7 - SIDROLAND',
        '80': 'REGIAO 8 - CUIABA B', '90': 'REGIAO 9 - SAO PAULO'
    };

    function exibirMensagem(tipo, texto) {
        areaMensagem.textContent = texto;
        areaMensagem.className = 'area_mensagem'; // Limpa classes anteriores
        areaMensagem.classList.add(tipo);
        areaMensagem.style.display = 'block';
    }

    function esconderMensagem() {
        areaMensagem.style.display = 'none';
        areaMensagem.textContent = '';
    }

    // Função para formatar o feedback da região no frontend
    function formatarFeedbackRegiao(valorInput) {
        const partes = valorInput.split('/').map(p => p.trim()).filter(p => p !== '');
        let partesFormatadas = [];
        let temDesconhecido = false;

        if (partes.length > 0) {
            for (const parte of partes) {
                if (MAPA_REGIOES[parte]) {
                    partesFormatadas.push(`${parte} ${MAPA_REGIOES[parte]}`);
                } else {
                    partesFormatadas.push(`Desconhecida (${parte})`);
                    temDesconhecido = true;
                }
            }
            return { texto: partesFormatadas.join(' / '), tipo: temDesconhecido ? 'alerta' : '' };
        }
        return { texto: '', tipo: '' };
    }

    inputRegiao.addEventListener('input', (evento) => {
        const valorInput = evento.target.value;
        const feedback = formatarFeedbackRegiao(valorInput);
        if (feedback.texto) {
            feedbackRegiao.textContent = feedback.texto;
            feedbackRegiao.className = 'mensagem_feedback';
            if (feedback.tipo) {
                feedbackRegiao.classList.add(feedback.tipo);
            }
        } else {
            feedbackRegiao.textContent = '';
            feedbackRegiao.className = 'mensagem_feedback';
        }
    });

    formulario.addEventListener('submit', async (evento) => {
        evento.preventDefault(); 
        esconderMensagem();

        const dadosFormulario = new FormData(formulario);
        const dados = {};
        dadosFormulario.forEach((valor, chave) => {
            dados[chave] = valor;
        });

        try {
            const resposta = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dados)
            });

            const resultado = await resposta.json();

            if (resposta.ok) {
                exibirMensagem('sucesso', resultado.mensagem);
                formulario.reset(); 
                feedbackRegiao.textContent = ''; 
            } else {
                exibirMensagem('erro', resultado.mensagem || 'Erro desconhecido ao enviar dados.');
            }
        } catch (erro) {
            exibirMensagem('erro', `Erro na conexão: ${erro.message}. Verifique sua internet ou a API.`);
        }
    });
});