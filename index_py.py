# api/index_py.py
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS # Necessário para permitir que o frontend converse com o backend
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
# Habilita CORS para todas as rotas. Em produção, você pode restringir a domínios específicos.
CORS(app) 

# --- Configuração da API Google Sheets ---
# ID da sua planilha (substitua pelo ID real da sua planilha)
SPREADSHEET_ID = '1nxtfwNYNpDkZWmE1gLwHmutmgoBxGlTJ6PURGPTyHCo' 
RANGE_NAME = 'Página1!A2'  # A célula inicial para adicionar os dados
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# --- Dicionário de Regiões (Mantido) ---
REGIONS = {
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
    '321': 'PARANAIBA', '330': 'AQUIDAUANA - ANASTAC', '330': 'DAMASCENO AQUIDAUANA', # Duplicado no REGIONS original, manter para consistência
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
}


# --- Funções de Autenticação e Envio para Google Sheets (Adaptada para Service Account) ---
def autenticar_google_sheets():
    try:
        # Tenta carregar as credenciais da variável de ambiente no Vercel
        service_account_info_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
        if not service_account_info_json:
            raise ValueError("A variável de ambiente GOOGLE_SERVICE_ACCOUNT_KEY não está configurada.")
        
        service_account_info = json.loads(service_account_info_json)
        
    except (TypeError, ValueError, json.JSONDecodeError) as e:
        # Retorna erro se a variável não estiver definida ou não for um JSON válido
        print(f"Erro ao carregar credenciais: {e}") # Log para debug no Vercel
        return None, "Erro de configuração: A variável GOOGLE_SERVICE_ACCOUNT_KEY não foi encontrada ou é inválida."

    try:
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)
        return service, None # Retorna o serviço e nenhum erro
    except Exception as e:
        print(f"Erro ao construir o serviço Sheets: {e}") # Log para debug
        return None, f"Erro ao autenticar com Google Sheets: {e}"

def enviar_para_planilha(dados):
    servico, erro_autenticacao = autenticar_google_sheets()
    if erro_autenticacao:
        return {'status': 'erro', 'mensagem': erro_autenticacao}

    valores = [[
        dados.get('DATA', ''), 
        dados.get('EMP', ''), 
        dados.get('REGIAO', ''), 
        '', # Coluna vazia
        dados.get('ID_CARGA', ''), # Usando ID_CARGA
        '', '', '', '', '', # Colunas vazias
        dados.get('NF', ''), 
        dados.get('VLR_PEDIDOS', '') # Usando VLR_PEDIDOS
    ]]
    corpo = {'values': valores}

    try:
        resultado = servico.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=corpo
        ).execute()
        atualizados = resultado.get('updates', {}).get('updatedCells', 0)
        return {'status': 'sucesso', 'mensagem': f'{atualizados} células atualizadas na planilha.'}
    except Exception as e:
        print(f"Erro ao adicionar linha na planilha: {e}") # Log para debug
        return {'status': 'erro', 'mensagem': f'Erro ao enviar para o Google Sheets: {e}'}

# --- Rota da API para o formulário ---
@app.route('/api/submit', methods=['POST'])
def submeter_dados():
    dados = request.json # Recebe os dados JSON enviados pelo frontend
    
    # Processa a região: Formato "NÚMERO NOME DA REGIÃO"
    regiao_digitada = dados.get('REGIAO', '').strip()
    regiao_final_para_planilha = ""

    if '/' in regiao_digitada:
        regioes_separadas = [r.strip() for r in regiao_digitada.split('/') if r.strip()]
        nomes_regioes_formatados = []
        for num_reg in regioes_separadas:
            if num_reg in REGIONS:
                nomes_regioes_formatados.append(f"{num_reg} {REGIONS[num_reg]}")
            else:
                # Se a região for desconhecida, manter o número digitado
                nomes_regioes_formatados.append(f"Região Desconhecida ({num_reg})")
        regiao_final_para_planilha = ' / '.join(nomes_regioes_formatados)
    elif regiao_digitada in REGIONS:
        regiao_final_para_planilha = f"{regiao_digitada} {REGIONS[regiao_digitada]}"
    else:
        # Se não encontrou e não é múltipla, envia o que foi digitado
        regiao_final_para_planilha = regiao_digitada 

    # Atualiza o campo 'REGIAO' nos dados que serão enviados para a planilha
    dados['REGIAO'] = regiao_final_para_planilha

    # Validação de campos (básica) - Ajustado para os nomes do frontend
    campos_obrigatorios = ['DATA', 'EMP', 'REGIAO', 'ID_CARGA', 'NF', 'VLR_PEDIDOS']
    for campo in campos_obrigatorios:
        if not dados.get(campo, '').strip():
            return jsonify({'status': 'erro', 'mensagem': f'O campo "{campo}" é obrigatório.'}), 400

    # Envia para a planilha
    resultado = enviar_para_planilha(dados)
    if resultado['status'] == 'sucesso':
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 500

# Rota de teste simples para verificar se a API está online
@app.route('/api/saude', methods=['GET']) 
def checar_saude():
    return jsonify({'status': 'ok', 'mensagem': 'API está funcionando!'})

# O Vercel gerencia a execução do Flask; não adicione 'if __name__ == "__main__": app.run()'