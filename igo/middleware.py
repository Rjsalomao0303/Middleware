# Handix 
# Dev: Ricardo J. Salomão 07/04/2025 v1.3
# coding: utf-8

import os
import shutil
import asyncio
from aiohttp import web
import aiohttp
import asyncpg
import logging
from datetime import datetime, timedelta, date, time
from config import DATABASE_CONFIG, LOG_LEVEL, LOG_FILE, TOKEN_BD
import aiofiles
from decimal import Decimal

# Configuração de log
logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

@web.middleware
async def cors_middleware(request, handler):
    # Adiciona suporte para o método OPTIONS
    if request.method == 'OPTIONS':
        # Retorna uma resposta adequada para requisições OPTIONS
        response = web.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '86400'  # Mantém a resposta no cache por 1 dia
        return response

    # Continua o processamento normal para outros métodos HTTP
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

app = web.Application(middlewares=[cors_middleware])

async def init_db(app):
    """Inicializa a conexão com o banco de dados e adiciona ao aplicativo."""
    logging.debug(f"Inicializa a conexão com o banco de dados e adiciona ao aplicativo")
    try:
        # Usa as configurações do arquivo config.py
        app['db'] = await asyncpg.create_pool(dsn=DATABASE_CONFIG['dsn'])
        logging.info("Conexão com o banco de dados inicializada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao inicializar o pool de conexões do banco de dados: {e}")
        raise web.HTTPInternalServerError(reason=f"Erro ao inicializar o pool de conexões: {e}")

async def close_db(app):
    """Fecha o pool de conexões com o banco de dados."""
    logging.error(f"Fecha o pool de conexões com o banco de dados")
    try:
        await app['db'].close()
        logging.info("Conexão com o banco de dados fechada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao fechar o pool de conexões do banco de dados: {e}")

async def verificar_tarefas(db):
    """Verifica se é hora de executar as tarefas para cada cliente."""
    logging.debug("Verifica se é hora de executar as tarefas para cada cliente.")

    now = datetime.now()
    hora_atual = now.hour
    
    async with db.acquire() as connection:
        try:
            # Consulta a tabela tb_disparo para verificar os horários de cada domínio
            query = """
            SELECT dominio_gesthor, cliente_id_gesthor, bearer_gesthor, dominio_omniplus, bearer_omniplus, canal_omniplus, hora_manha, hora_tarde, hora_noite, template_consulta, dias_consulta, template_exame, dias_exame, template_retorno, dias_retorno, template_cirurgia, dias_cirurgia
            FROM tb_cliente
            WHERE ativo = 'sim'            
            """
            rows = await connection.fetch(query)
            
            for row in rows:
                dominio_gesthor = row['dominio_gesthor']
                cliente_id_gesthor = row['cliente_id_gesthor']
                bearer_gesthor = row['bearer_gesthor']
                dominio_omniplus = row['dominio_omniplus']
                bearer_omniplus = row['bearer_omniplus']
                canal_omniplus = row['canal_omniplus']
                hora_manha = row['hora_manha']
                hora_tarde = row['hora_tarde']
                hora_noite = row['hora_noite']
                template_consulta = row['template_consulta']
                dias_consulta = row['dias_consulta']
                template_exame = row['template_exame']
                dias_exame = row['dias_exame']
                template_retorno = row['template_retorno']
                dias_retorno = row['dias_retorno']
                template_cirurgia = row['template_cirurgia']
                dias_cirurgia = row['dias_cirurgia']

                # Verifica se a hora atual corresponde a um dos horários definidos
                if hora_atual == hora_manha:
                    logging.info(f"Executando tarefas da manhã para o domínio: {dominio_gesthor}")
                    # Aqui você chamaria a função que executa as tarefas da manhã
                    await executar_tarefas(connection, dominio_gesthor, 'manhã', cliente_id_gesthor, bearer_gesthor, dominio_omniplus, bearer_omniplus, canal_omniplus, template_consulta, dias_consulta, template_exame, dias_exame, template_retorno, dias_retorno, template_cirurgia, dias_cirurgia)

                elif hora_atual == hora_tarde:
                    logging.info(f"Executando tarefas da tarde para o domínio: {dominio_gesthor}")
                    # Aqui você chamaria a função que executa as tarefas da tarde
                    await executar_tarefas(connection, dominio_gesthor, 'tarde', cliente_id_gesthor, bearer_gesthor, dominio_omniplus, bearer_omniplus, canal_omniplus, template_consulta, dias_consulta, template_exame, dias_exame, template_retorno, dias_retorno, template_cirurgia, dias_cirurgia)

                elif hora_atual == hora_noite:
                    logging.info(f"Executando tarefas da noite para o domínio: {dominio_gesthor}")
                    # Aqui você chamaria a função que executa as tarefas da noite
                    await executar_tarefas(connection, dominio_gesthor, 'noite', cliente_id_gesthor, bearer_gesthor, dominio_omniplus, bearer_omniplus, canal_omniplus, template_consulta, dias_consulta, template_exame, dias_exame, template_retorno, dias_retorno, template_cirurgia, dias_cirurgia)

        except Exception as e:
            logging.error(f"Erro ao verificar as tarefas: {e}")

# Headers da API
headers_gesthor = lambda cliente_id_gesthor, bearer_gesthor: {
    'CLIENT_ID': cliente_id_gesthor,
    'Authorization': f'Bearer {bearer_gesthor}',
    'Content-Type': 'application/json'
}

# Função para realizar a requisição
async def fetch(session, url, headers):
    logging.debug("Função para realizar a requisição.")
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            try:
                data = await response.json()
                return data
            except Exception as e:
                logging.error(f"Erro ao processar a resposta JSON da API: {e}")
                return None
        else:
            logging.error(f"Erro ao conectar à API: status {response.status}")
            return None

async def insert_controle(connection, dominio_omniplus, numero_contato, codigo_paciente, nome_paciente, tipo_agendamento, codigo_agendamento, data, horario, url_origem, agenda):
    """Insere os dados na tabela tb_controle."""
    logging.debug("Insere os dados na tabela tb_controle.")
    try:
        # Verifica se já existe um registro com o mesmo codigo_agendamento e numero_contato
        existing_record = await connection.fetchrow("""
            SELECT 1 FROM tb_controle 
            WHERE codigo_agendamento = $1 AND numero_contato = $2
        """, int(codigo_agendamento), int(numero_contato))
        
        if existing_record:
            logging.warning(f"Registro já existe para codigo_agendamento {codigo_agendamento} e numero_contato {numero_contato}.")
            return False  # Ou algum outro tipo de feedback
        
        # Se não existir, insere o novo registro
        await connection.execute("""
            INSERT INTO tb_controle (dominio_omniplus, numero_contato, codigo_paciente, nome_paciente, tipo_agendamento, codigo_agendamento, data, horario, url_origem, status, confirmacao, agenda)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 0, 'nao', $10)
        """, dominio_omniplus, int(numero_contato), int(codigo_paciente), nome_paciente, tipo_agendamento, int(codigo_agendamento), data, horario, url_origem, agenda)
        
    except Exception as e:
        logging.error(f"Ocorreu um erro ao inserir na tabela tb_controle: {e}")
        raise

async def insert_log(connection, dominio_omniplus, numero_contato, codigo_paciente, nome_paciente, tipo_agendamento, codigo_agendamento, status, confirmacao, agenda):
    """Insere os dados na tabela tb_log."""
    logging.debug("Insere os dados na tabela tb_log.")
    try:
        await connection.execute("""
        INSERT INTO tb_log (time, dominio_omniplus, numero_contato, codigo_paciente, nome_paciente, tipo_agendamento, codigo_agendamento, status, confirmacao, agenda)
        VALUES (now(), $1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, dominio_omniplus, int(numero_contato), int(codigo_paciente), nome_paciente, tipo_agendamento, int(codigo_agendamento), status, confirmacao, agenda)
    except Exception as e:
        logging.error(f"Ocorreu um erro ao inserir na tabela tb_log: {e}")
        raise

# Função para buscar o número de contato do paciente via API
async def buscar_contato_paciente(session, base_url, paciente_id, headers):
    """Busca o número de contato do paciente usando o PACIENTE_ID."""
    logging.debug(f"Busca o número de contato do paciente usando o PACIENTE_ID.")
    paciente_url = f"{base_url}/paciente/getId?ID={paciente_id}"
    logging.debug(f"paciente_url ===> {paciente_url}")
    try:
        async with session.get(paciente_url, headers=headers) as response:
            if response.status == 200:
                paciente_data = await response.json()
                return paciente_data.get('TELEFONE', None)  # Retorna o número de telefone ou None se não encontrado
            else:
                logging.error(f"Erro ao buscar informações do paciente {paciente_id}. Status: {response.status}")
                return None
    except Exception as e:
        logging.error(f"Erro ao conectar à API para buscar o contato do paciente {paciente_id}: {e}")
        return None

async def executar_tarefas(connection, dominio_gesthor, periodo, cliente_id_gesthor, bearer_gesthor, dominio_omniplus, bearer_omniplus, canal_omniplus, template_consulta, dias_consulta, template_exame, dias_exame, template_retorno, dias_retorno, template_cirurgia, dias_cirurgia):
    """Executa as tarefas de acordo com o domínio e o período."""
    logging.debug("Executa as tarefas de acordo com o domínio e o período.")
    base_url = f"http://{dominio_gesthor}/gthWS"  # URL dinâmica
    headers = headers_gesthor(cliente_id_gesthor, bearer_gesthor)

    try:
        async with aiohttp.ClientSession() as session:
            logging.debug(f"Buscar convênios.")
            convenio_url = f"{base_url}/convenio/getAll"
            convenios = await fetch(session, convenio_url, headers)

            if isinstance(convenios, list) and len(convenios) > 0:
                # Encontra o primeiro convênio válido e segue com o processo
                convenio_id = convenios[0]['ID']
                logging.debug(f"Primeiro convenio encontrado: {convenio_id}")
                    
                logging.debug(f"Buscar agendas para o convênio.")
                agenda_url = f"{base_url}/agenda/getAll?CONVENIO_ID={convenio_id}"
                agendas = await fetch(session, agenda_url, headers)

                if isinstance(agendas, list) and len(agendas) > 0:
                    for agenda in agendas:
                        agenda_id = agenda['ID']  

                        # Deixar essa opção habilitada apenas se for fazer teste de validação
                        if agenda_id != 33 and dominio_gesthor == 'hospitalolhos.gesthor.falehandix.com.br':
                             continue  # Pula para a próxima iteração se o ID não for 33
                        
                        logging.debug(f"Buscar agendamentos com o AGENDA_ID e intervalo de datas.")
                        data_ini = datetime.now().strftime('%Y-%m-%d')
                        data_fim = (datetime.now() + timedelta(days=max(dias_consulta, dias_exame, dias_retorno, dias_cirurgia))).strftime('%Y-%m-%d')
                        status = 'A'

                        agendamento_url = (f"{base_url}/agendamento/getPeriod"
                                            f"?AGENDA_ID={agenda_id}&DATA_INI={data_ini}&DATA_FIM={data_fim}&STATUS={status}")

                        logging.debug(f"agendamento_url ===> {agendamento_url}")

                        agendamentos = await fetch(session, agendamento_url, headers)
                        
                        if isinstance(agendamentos, list) and len(agendamentos) > 0:
                            for agendamento in agendamentos:
                                tipo = agendamento.get('TIPO')
                                if tipo == "C":
                                    # Ajustar data_ini e data_fim para consulta
                                    data_ini = (datetime.now() + timedelta(days=dias_consulta)).strftime('%Y-%m-%d')
                                    data_fim = (datetime.now() + timedelta(days=dias_consulta)).strftime('%Y-%m-%d')
                                elif tipo == "E":
                                    # Ajustar data_ini e data_fim para exame
                                    data_ini = (datetime.now() + timedelta(days=dias_exame)).strftime('%Y-%m-%d')
                                    data_fim = (datetime.now() + timedelta(days=dias_exame)).strftime('%Y-%m-%d')
                                elif tipo == "R":
                                    # Ajustar data_ini e data_fim para retorno
                                    data_ini = (datetime.now() + timedelta(days=dias_retorno)).strftime('%Y-%m-%d')
                                    data_fim = (datetime.now() + timedelta(days=dias_retorno)).strftime('%Y-%m-%d')
                                elif tipo == "P":
                                    # Ajustar data_ini e data_fim para cirurgia
                                    data_ini = (datetime.now() + timedelta(days=dias_cirurgia)).strftime('%Y-%m-%d')
                                    data_fim = (datetime.now() + timedelta(days=dias_cirurgia)).strftime('%Y-%m-%d')
                                else:
                                    continue  # Ignora se o tipo não for reconhecido
                                
                                # String de data original
                                data_original = agendamento.get('DATA', 'N/A')

                                # Converter a string para o objeto datetime
                                data_formatada = datetime.strptime(data_original, "%Y-%m-%d")
                                
                                # Verificar se a data do agendamento está dentro do intervalo
                                data_ini_dt = datetime.strptime(data_ini, "%Y-%m-%d")
                                data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
                                
                                if not (data_ini_dt <= data_formatada <= data_fim_dt):
                                    logging.debug(f"Data do agendamento {data_original} fora do intervalo {data_ini} - {data_fim}, pulando registro.")
                                    continue  # Pula para o próximo agendamento se estiver fora do intervalo
                                
                                # Formatar a data para o novo formato
                                data = data_formatada.strftime("%d/%m/%Y")

                                codigo_paciente = agendamento.get('PACIENTE_ID', 'N/A')

                                if codigo_paciente == 'N/A':
                                    continue # Ignora se não houver codigo paciente
                                
                                numero_contato = await buscar_contato_paciente(session, base_url, codigo_paciente, headers)
                                if numero_contato:
                                    numero_contato = numero_contato.lstrip('+').replace(' ', '')
                                else:
                                    continue  # Ignora se não houver numero de contato

                                if numero_contato == '':
                                    continue  # Ignora se numero de contato for em branco

                                nome_paciente = agendamento.get('PACIENTE', 'N/A')
                                tipo_agendamento = agendamento.get('TIPO')
                                codigo_agendamento = agendamento.get('AGD_ID', 'N/A')
                                horario = f"{agendamento.get('HORA', 'N/A')}h"
                                url_origem = dominio_gesthor
                                
                                # Log para verificação
                                logging.debug(f"Agendamento TIPO: {tipo}, Data Inicial: {data_ini}, Data Final: {data_fim}")

                                # Exibir os dados relevantes do agendamento (último laço)
                                logging.debug("Dados do último laço:")
                                logging.debug(f"Agendamento ID: {agendamento.get('AGD_ID', 'N/A')}")
                                logging.debug(f"Data do Agendamento: {agendamento.get('DATA', 'N/A')}")
                                logging.debug(f"Hora do Agendamento: {agendamento.get('HORA', 'N/A')}")
                                logging.debug(f"Confirmado: {agendamento.get('CONFIRMADO', 'N/A')}")
                                logging.debug(f"Tipo do Agendamento: {agendamento.get('TIPO', 'N/A')}")
                                logging.debug(f"Status do Agendamento: {agendamento.get('STATUS', 'N/A')}")
                                logging.debug(f"Paciente ID: {agendamento.get('PACIENTE_ID', 'N/A')}")
                                logging.debug(f"Telefone Paciente: {numero_contato}")
                                logging.debug(f"Paciente: {agendamento.get('PACIENTE', 'N/A')}")
                                logging.debug(f"Local ID: {agendamento.get('LOCAL_ID', 'N/A')}")
                                logging.debug(f"Nome do Local: {agendamento.get('LOCAL_NOME', 'N/A')}")
                                logging.debug(f"Telefone do Local: {agendamento.get('LOCAL_TELEFONE', 'N/A')}")
                                logging.debug(f"Endereço do Local: {agendamento.get('LOCAL_ENDERECO', 'N/A')}")
                                logging.debug(f"Agenda ID: {agendamento.get('AGENDA_ID', 'N/A')}")
                                logging.debug(f"Agenda Tipo: {agendamento.get('AGENDA_TIPO', 'N/A')}")
                                logging.debug(f"Agenda Código: {agendamento.get('AGENDA_CODIGO', 'N/A')}")
                                logging.debug(f"Agenda Descrição: {agendamento.get('AGENDA_DESCRICAO', 'N/A')}")
                                logging.debug(f"Procedimento ID: {agendamento.get('PROCEDIMENTO_ID', 'N/A')}")
                                logging.debug(f"Procedimento Nome: {agendamento.get('PROCEDIMENTO_NOME', 'N/A')}")
                                logging.debug(f"Plano ID: {agendamento.get('PLANO_ID', 'N/A')}")
                                logging.debug(f"Plano Nome: {agendamento.get('PLANO_NOME', 'N/A')}")
                                logging.debug(f"Exame: {agendamento.get('EXAME', 'N/A')}")
                                logging.debug("===========================================================================================")

                                await insert_controle(connection, dominio_omniplus, numero_contato, codigo_paciente, nome_paciente, tipo_agendamento, codigo_agendamento, data, horario, url_origem, agenda_id)
                                await insert_log(connection, dominio_omniplus, numero_contato, codigo_paciente, nome_paciente, tipo_agendamento, codigo_agendamento, 0, 'nao', agenda_id)

                            else:
                                logging.debug(f"Nenhuma agenda encontrada para o Convênio ID {convenio_id}.")
            else:
                logging.debug("Nenhum convênio encontrado.")

    except Exception as e:
        logging.error(f"Erro ao executar as tarefas para o domínio {dominio_gesthor}: {e}")

async def update_status_to_sent(connection, record):
    """Atualiza o status para 1 (enviado Omniplus)."""
    logging.debug("Atualiza o status para 1 (enviado Omniplus).")
    await connection.execute("UPDATE tb_controle SET status = 1 WHERE id = $1", record['id'])
    await insert_log(connection, record['dominio_omniplus'], record['numero_contato'], record['codigo_paciente'], record['nome_paciente'], record['tipo_agendamento'], record['codigo_agendamento'], 1, 'nao', record['agenda'])

async def send_data_to_omniplus(record):
    """Envia dados para a API Omniplus."""
    logging.debug("Envia dados para a API Omniplus.")
    tipo = str(record['tipo_agendamento'])
    if tipo == "C":
        template = str(record['template_consulta'])
    elif tipo == "E":
        template = str(record['template_exame'])
    elif tipo == "R":
        template = str(record['template_retorno'])
    elif tipo == "P":
        template = str(record['template_cirurgia'])
    
    payload = {
        "contato": {
            "canalCliente": f"+{str(record['numero_contato'])}"
        },
        "template": {
            "_id": template,
            "variaveis": [
                str(record['nome_paciente']),
                str(record['codigo_paciente']),
                str(record['codigo_agendamento']),
                str(record['data']),
                str(record['horario'])
            ]
        },
        "canal": str(record.get('canal_omniplus', ''))
    }

    dominio = record.get('dominio_omniplus', '')
    if not dominio:
        logging.error(f"Domínio está vazio para o registro ID: {record['id']}")
        return False

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {str(record['bearer_omniplus'])}"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"https://{str(dominio)}/api/v1/template/send", json=payload, headers=headers) as response:
                response_text = await response.text()
                if response.status == 200:
                    logging.info(f"Dados enviados para o Omniplus com sucesso. ID do registro: {record['id']}. Resposta: {response_text}")
                    return True
                else:
                    logging.error(f"Erro ao enviar dados para o Omniplus. ID do registro: {record['id']}. Status: {response.status}. Resposta: {response_text}")
                    return False
        except Exception as e:
            logging.error(f"Erro ao enviar dados para o Omniplus: {e}")
            return False

async def fetch_records_to_send(connection):
    """Busca registros com status 0, sem duplicatas de domínio e número com status 1."""
    logging.debug("Busca registros com status 0, sem duplicatas de domínio e número com status 1.")
    query = """
    SELECT a.id, a.dominio_omniplus, a.numero_contato, a.codigo_paciente, a.nome_paciente, a.tipo_agendamento, a.codigo_agendamento, a.data, a.horario, a.url_origem, a.agenda, b.bearer_omniplus, b.canal_omniplus, b.template_consulta, b.template_exame, b.template_retorno, b.template_cirurgia
    FROM tb_controle a
    JOIN tb_cliente b ON a.url_origem = b.dominio_gesthor
    WHERE a.status = 0
    AND b.ativo = 'sim'
    AND TO_DATE(a.data, 'DD/MM/YYYY') >= CURRENT_DATE
    AND NOT EXISTS (
        SELECT 1
        FROM tb_controle AS c
        WHERE c.numero_contato = a.numero_contato
        AND c.dominio_omniplus = a.dominio_omniplus
        AND TO_DATE(c.data, 'DD/MM/YYYY') >= CURRENT_DATE
        AND c.status = 1
    )
    """
    return await connection.fetch(query)

async def process_queue(app):
    """Processa a fila de registros para enviar dados ao Omniplus."""
    logging.debug("Processa a fila de registros para enviar dados ao Omniplus.")
    while True:
        
        # Tratar o middleware.log
        await tratar_middleware_log()
        
        async with app['db'].acquire() as connection:
            try:
                records = await fetch_records_to_send(connection)
                logging.debug(f"Lendo o banco")
                for record in records:
                    success = await send_data_to_omniplus(record)
                    if success:
                        await update_status_to_sent(connection, record)
                        logging.info("Processamento da fila concluído.")
            except Exception as e:
                logging.error(f"Erro ao processar a fila: {e}")
        await asyncio.sleep(60)

async def start_background_tasks(app):
    """Inicia tarefas em segundo plano ao iniciar o servidor."""
    logging.debug("Inicia tarefas em segundo plano ao iniciar o servidor.")
    app['queue_task'] = asyncio.create_task(process_queue(app))

async def cleanup_background_tasks(app):
    """Encerra tarefas em segundo plano ao parar o servidor."""
    logging.debug("Encerra tarefas em segundo plano ao parar o servidor.")
    app['queue_task'].cancel()
    await app['queue_task']

async def send_to_gesthor(record, confirma):
    """Envia os dados para a API Gesthor e lida com a confirmação."""
    logging.debug("Envia os dados para a API Gesthor e lida com a confirmação.")
    # URL com parâmetros na query string
    paciente_id = int(record['codigo_paciente'])
    agd_id = int(record['codigo_agendamento'])
    dominio = record.get('dominio_gesthor', '')

    if not dominio:
        logging.error(f"Domínio está vazio para o registro ID: {record['id']}")
        return False

    headers = {
        'CLIENT_ID': record['cliente_id_gesthor'],
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Bearer {record['bearer_gesthor']}"
    }

    url_path = "confirm" if confirma.lower() == "sim" else "notConfirm"

    # Formatar a URL como no exemplo do Postman
    url = f"http://{dominio}/gthWS/agendamento/{url_path}?PACIENTE_ID={paciente_id}&AGD_ID={agd_id}"

    logging.debug(f"URL: {url}")
    logging.debug(f"Headers: {headers}")
    logging.debug(f"PACIENTE_ID  ==>> {record['codigo_paciente']}")
    logging.debug(f"AGD_ID ==>> {record['codigo_agendamento']}")
    logging.debug(f"dominio ==>> {dominio}")
    logging.debug(f"Bearer gestor ==>> {record['bearer_gesthor']}")
    logging.debug(f"CLIENT_ID ==>> {record['cliente_id_gesthor']}")
    logging.debug(f"url_path ==>> {url_path}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, data='') as response:
                response_text = await response.text()
                if response.status == 200:
                    logging.info(f"Dados enviados para o Gesthor com sucesso. ID do registro: {record['id']}. Resposta: {response_text}")
                    return True
        except Exception as e:
            logging.error(f"Erro ao enviar dados para o Gesthor: {e}")
            return False

async def handle_return(request):
    """Processa a requisição de retorno e lida com o banco de dados e o Gesthor."""
    logging.debug("Processa a requisição de retorno e lida com o banco de dados e o Gesthor.")

    try:
        # Extrai dados do JSON recebido
        data = await request.json()
        numero = data.get('numero', '').lstrip('+')
        confirma = data.get('confirma')
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        logging.debug(f"Requisição recebida - numero: {numero}, Confirmação: {confirma}")
        logging.debug(f"Token: {token}")

        # Verificação básica de dados
        if not numero or not confirma or not token:
            logging.debug("Campos obrigatórios ausentes ou token inválido.")
            return web.json_response({
                "status": "error",
                "code": 400,
                "message": "Missing required fields or invalid token."
            }, status=400)

        # Conexão com o banco de dados
        async with request.app['db'].acquire() as connection:
            # Consulta para buscar o registro relevante
            logging.debug("Consulta para buscar o registro relevante.")
            query = """
            SELECT a.id, a.dominio_omniplus, a.numero_contato, a.codigo_paciente, a.nome_paciente, a.tipo_agendamento, a.codigo_agendamento, a.agenda,
                   b.dominio_gesthor, b.cliente_id_gesthor, b.bearer_gesthor
            FROM tb_controle a
            JOIN tb_cliente b ON a.url_origem = b.dominio_gesthor
            WHERE a.numero_contato = $1
              AND b.bearer_gesthor = $2
              AND a.status = 1
            """
            record = await connection.fetchrow(query, int(numero), str(token))

            # Verifica se o registro foi encontrado
            if not record:
                logging.debug("Nenhum registro correspondente encontrado.")
                return web.json_response({
                    "status": "error",
                    "code": 404,
                    "message": "No matching record found."
                }, status=404)

            # Atualiza o status do controle
            update_query = "UPDATE tb_controle SET status = 2, confirmacao = $1 WHERE id = $2"
            await connection.execute(update_query, confirma, record['id'])

            # Insere o log
            await insert_log(connection, record['dominio_gesthor'], int(record['numero_contato']), str(record['codigo_paciente']), 
                             record['nome_paciente'], record['tipo_agendamento'], int(record['codigo_agendamento']), 2, confirma, int(record['agenda']))

            # Envia os dados para o Gesthor
            success = await send_to_gesthor(record, confirma)
            logging.debug(f"Retorno da função em success: {success}")

            # Retorna resposta para o cliente, independentemente do sucesso
            if success:
                # Insere o log
                await insert_log(connection, record['dominio_gesthor'], int(record['numero_contato']), str(record['codigo_paciente']), 
                             record['nome_paciente'], record['tipo_agendamento'], int(record['codigo_agendamento']), 3, confirma, int(record['agenda']))
                return web.json_response({
                    "status": "success",
                    "code": 200,
                    "message": "Status updated and log inserted successfully. Data sent to Gesthor."
                }, status=200)
            else:
                return web.json_response({
                    "status": "error",
                    "code": 500,
                    "message": "Failed to send data to Gesthor."
                }, status=500)

    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return web.json_response({
            "status": "error",
            "code": 500,
            "message": "Internal server error."
        }, status=500)

# Função de login
async def login(request):
    """Valida a requisição de leitura de login e senha."""
    logging.debug("Valida a requisição de leitura de login e senha.")

    # Adiciona suporte para requisições OPTIONS diretamente no endpoint
    if request.method == 'OPTIONS':
        return web.Response(headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        })

    try:
        # Extrai dados do JSON recebido
        data = await request.json()
        email = data.get('email', '')
        password = data.get('password')
        auth_header = request.headers.get('Authorization', '')

        # Verifica se o token está presente e no formato correto
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        logging.debug(f"Requisição recebida - email: {email}, Password: {password}")

        # Verificação básica de dados
        if not email or not password or not token:
            logging.debug("Campos obrigatórios ausentes ou token inválido.")
            return web.json_response({
                "status": "error",
                "code": 400,
                "message": "Missing required fields or invalid token."
            }, status=400)

        # Verificação de token
        if token != TOKEN_BD:
            logging.debug("Token inválido.")
            return web.json_response({
                "status": "error",
                "code": 401,
                "message": "Invalid token."
            }, status=401)

        # Conexão com o banco de dados
        try:
            async with request.app['db'].acquire() as connection:
                # Consulta para buscar o registro relevante
                logging.debug("Consulta para buscar o registro relevante.")
                query = """
                SELECT id, nome, nivel
                FROM tb_usuarios
                WHERE login = $1
                  AND senha = $2
                """
                user = await connection.fetchrow(query, email, password)

                # Se o registro foi encontrado, extrai os dados
                if user:
                    # Extrai os valores da linha retornada
                    user_id = user['id']
                    nome = user['nome']
                    nivel = user['nivel']

                    logging.debug(f"Login bem-sucedido - ID: {user_id}, Nome: {nome}")

                    return web.json_response({
                        "status": "success",
                        "code": 200,
                        "message": "Login successfully.",
                        "data": {
                            "id": user_id,
                            "nome": nome,
                            "nivel": nivel
                        }
                    }, status=200)
                else:
                    logging.debug("Nenhum registro correspondente encontrado.")
                    return web.json_response({
                        "status": "success",
                        "code": 404,
                        "message": "No matching record found.",
                    }, status=404)
        except Exception as db_error:
            logging.error(f"Erro ao acessar o banco de dados: {db_error}")
            return web.json_response({
                "status": "error",
                "code": 500,
                "message": "Database error."
            }, status=500)

    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return web.json_response({
            "status": "error",
            "code": 500,
            "message": "Internal server error."
        }, status=500)

# Função de consulta clientes com parametros
async def consultaClientes(request):
    """Consulta clientes com parâmetros cadastrados."""
    logging.debug("Consulta clientes com parâmetros cadastrados.")

    # Suporte para requisições OPTIONS
    if request.method == 'OPTIONS':
        return web.Response(headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        })

    try:
        # Obter o cabeçalho de autorização
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        logging.debug("Requisição de consulta recebida.")

        # Verificação de token
        if token != TOKEN_BD:
            logging.debug("Token inválido.")
            return web.json_response({
                "status": "error",
                "code": 401,
                "message": "Invalid token."
            }, status=401)

        # Conexão com o banco de dados
        async with request.app['db'].acquire() as connection:
            logging.debug("Consulta no banco de dados dos clientes com parâmetros cadastrados.")

            query = """
            SELECT dominio_gesthor, cliente_id_gesthor, bearer_gesthor, dominio_omniplus, bearer_omniplus,
                   canal_omniplus, hora_manha, hora_tarde, hora_noite, template_consulta, dias_consulta,
                   template_exame, dias_exame, template_retorno, dias_retorno, template_cirurgia,
                   dias_cirurgia, ativo
            FROM tb_cliente
            ORDER BY cliente_id_gesthor DESC
            LIMIT 50;
            """
            results = await connection.fetch(query)

            # Se o registro foi encontrado, extrai os dados
            if results:
                logging.debug("Consulta realizada com sucesso.")
                # Transformar os resultados em uma lista de dicionários
                response_data = [{key: result[key] for key in result.keys()} for result in results]
                
                return web.json_response({
                    "status": "success",
                    "code": 200,
                    "message": "Client parameters retrieved successfully.",
                    "data": response_data  # Agora é um array
                }, status=200)

            logging.debug("Nenhum registro encontrado.")
            return web.json_response({
                "status": "success",
                "code": 404,
                "message": "No client parameters found.",
            }, status=404)

    except Exception as db_error:
        logging.error(f"Erro inesperado: {db_error}")
        return web.json_response({
            "status": "error",
            "code": 500,
            "message": "Internal server error."
        }, status=500)

# Função de consulta logs com parâmetros
async def consultaLogs(request):
    """Consulta logs com parâmetros de filtros."""
    logging.debug("Consulta logs com parâmetros de filtros.")

    # Suporte para requisições OPTIONS (CORS)
    if request.method == 'OPTIONS':
        return web.Response(headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        })

    try:
        # Obter o cabeçalho de autorização
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        logging.debug("Requisição de consulta recebida.")

        # Verificação de token
        if token != TOKEN_BD:
            logging.debug("Token inválido.")
            return web.json_response({
                "status": "error",
                "code": 401,
                "message": "Invalid token."
            }, status=401)

        # Obter parâmetros de consulta (query parameters)
        params = request.rel_url.query
        data_inicio = params.get('dataInicio')
        data_fim = params.get('dataFim')
        dominio = params.get('dominio')
        agenda = params.get('agenda')
        numero_contato = params.get('numeroContato')
        nome_paciente = params.get('nomePaciente')
        limit = int(params.get('limit', 100))

        # Converte as strings em datas (datetime.date)
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()

        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

        # Converte as datas para datetime combinando com os horários
        if data_inicio:
            # Começar à meia-noite do dia de início (00:00:00)
            data_inicio = datetime.combine(data_inicio, time.min)

        if data_fim:
            # Terminar no final do dia (23:59:59.999999)
            data_fim = datetime.combine(data_fim, time.max)

        # Conexão com o banco de dados
        async with request.app['db'].acquire() as connection:
            logging.debug(
                "Consulta no banco de dados logs com parâmetros de filtros.")

            # Montagem da query com parâmetros dinâmicos
            query = """ WITH UltimosRegistros AS (
                SELECT
                    a.codigo_paciente,
                    a.nome_paciente,
                    CASE
                        WHEN LENGTH(a.numero_contato::TEXT) = 13 AND a.numero_contato::TEXT LIKE '55%' THEN
                            SUBSTRING(a.numero_contato::TEXT FROM 1 FOR 2) || ' ' ||
                            SUBSTRING(a.numero_contato::TEXT FROM 3 FOR 2) || ' ' ||
                            SUBSTRING(a.numero_contato::TEXT FROM 5 FOR 1) || '.' ||
                            SUBSTRING(a.numero_contato::TEXT FROM 6 FOR 4) || '-' ||
                            SUBSTRING(a.numero_contato::TEXT FROM 10 FOR 4)
                        WHEN LENGTH(a.numero_contato::TEXT) = 12 AND a.numero_contato::TEXT LIKE '55%' THEN
                            SUBSTRING(a.numero_contato::TEXT FROM 1 FOR 2) || ' ' ||
                            SUBSTRING(a.numero_contato::TEXT FROM 3 FOR 2) || ' ' ||
                            SUBSTRING(a.numero_contato::TEXT FROM 5 FOR 4) || '-' ||
                            SUBSTRING(a.numero_contato::TEXT FROM 9 FOR 4)
                        ELSE
                            a.numero_contato::TEXT
                    END AS numero_contato_formatado,
                    a.agenda,
                    a.codigo_agendamento,
                    a.tipo_agendamento,
                    CASE
                        WHEN a.tipo_agendamento = 'C' THEN 'Consulta'
                        WHEN a.tipo_agendamento = 'E' THEN 'Exame'
                        WHEN a.tipo_agendamento = 'R' THEN 'Retorno'
                        WHEN a.tipo_agendamento = 'P' THEN 'Cirurgia'
                        ELSE '*'
                    END AS descricao_tipo_agendamento,
                    TO_CHAR(a.time, 'DD/MM/YYYY HH24:MI') || 'h' AS time_formatado,
                    a.status,
                    a.confirmacao,
                    CASE
                        WHEN a.status = '0' THEN 'A enviar'
                        WHEN a.status = '1' THEN 'Enviado'
                        WHEN a.status = '2' THEN 'Recebido'
                        WHEN a.status = '3' THEN 'Respondido'
                        ELSE '*'
                    END AS descricao_status,
                    a.time,
                    ROW_NUMBER() OVER(PARTITION BY a.codigo_agendamento ORDER BY a.time DESC) as rn
                FROM
                    tb_log a
                WHERE 1=1
            """
            query_params = []  # Lista para armazenar os parâmetros da query
            where_clauses = [] # Lista para armazenar as cláusulas WHERE dinâmicas

            # Adiciona condições dinâmicas conforme os parâmetros recebidos
            if data_inicio:
                where_clauses.append("a.time >= $1")
                query_params.append(data_inicio)

            if data_fim:
                where_clauses.append(f"a.time <= ${len(query_params) + 1}")
                query_params.append(data_fim)

            if dominio:
                where_clauses.append(f"a.dominio_omniplus ILIKE ${len(query_params) + 1}")
                query_params.append(f"%{dominio}%")
                
            # Verificação e conversão do número de contato para int
            if agenda:
                try:
                    agenda = int(agenda)
                    where_clauses.append(f"a.agenda = ${len(query_params) + 1}")
                    query_params.append(agenda)
                except ValueError:
                    logging.error(
                        f"Erro: agenda '{agenda}' não é um número inteiro válido.")
                    return web.json_response({
                        "status": "error",
                        "code": 400,
                        "message": "Invalid agenda format. Must be an integer."
                    }, status=400)

            # Verificação e conversão do número de contato para int
            if numero_contato:
                try:
                    numero_contato = int(numero_contato)
                    where_clauses.append(f"a.numero_contato = ${len(query_params) + 1}")
                    query_params.append(numero_contato)
                except ValueError:
                    logging.error(
                        f"Erro: numero_contato '{numero_contato}' não é um número inteiro válido.")
                    return web.json_response({
                        "status": "error",
                        "code": 400,
                        "message": "Invalid numero_contato format. Must be an integer."
                    }, status=400)

            if nome_paciente:
                where_clauses.append(f"a.nome_paciente ILIKE ${len(query_params) + 1}")
                query_params.append(f"%{nome_paciente}%")

            # Adiciona as cláusulas WHERE à query da CTE
            if where_clauses:
                query += " AND " + " AND ".join(where_clauses)

            # Finaliza a query principal para selecionar os últimos registros
            query += f"""
            )
            SELECT
                codigo_paciente,
                nome_paciente,
                numero_contato_formatado,
                agenda,
                codigo_agendamento,
                tipo_agendamento,
                descricao_tipo_agendamento,
                time_formatado,
                status,
                confirmacao,
                descricao_status
            FROM
                UltimosRegistros
            WHERE
                rn = 1
            ORDER BY
                nome_paciente,
                time,
                codigo_agendamento ASC
            LIMIT ${len(query_params) + 1}
            """
            query_params.append(limit)

            # Função para formatar a query com os parâmetros reais (para depuração)
            def format_query_with_params(query, params):
                for i, param in enumerate(params, start=1):
                    # Verifica se o parâmetro é uma string e coloca entre aspas simples
                    if isinstance(param, str):
                        param = f"'{param}'"
                    query = query.replace(f"${i}", str(param))
                return query

            # Exibir a consulta formatada com os parâmetros reais
            formatted_query = format_query_with_params(query, query_params)
            logging.debug(f"Query final para teste: {formatted_query}")

            # Executar a consulta
            results = await connection.fetch(query, *query_params)

            # Se o registro foi encontrado, extrai os dados
            if results:
                logging.debug("Consulta realizada com sucesso.")
                # Transformar os resultados em uma lista de dicionários, convertendo datetime para string
                response_data = []
                for result in results:
                    row = {}
                    for key, value in result.items():
                        if isinstance(value, datetime):
                            row[key] = value.isoformat()
                        elif isinstance(value, Decimal):  # conversão do decimal
                            row[key] = float(value)  # ou str(value)
                        else:
                            row[key] = value
                    response_data.append(row)

                return web.json_response({
                    "status": "success",
                    "code": 200,
                    "data": response_data
                }, status=200)

            logging.debug("Nenhum registro encontrado.")
            return web.json_response({
                "status": "success",
                "code": 404,
                "message": "No logs found."
            }, status=404)

    except asyncpg.exceptions.PostgresError as db_error:
        logging.error(f"Erro de banco de dados: {db_error}")
        return web.json_response({
            "status": "error",
            "code": 500,
            "message": "Erro de banco de dados."
        }, status=500)
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return web.json_response({
            "status": "error",
            "code": 500,
            "message": "Internal server error."
        }, status=500)

# Função Grava ou altera parametros do cliente
async def parametros(request):
    """Grava ou altera parametros do cliente."""
    logging.debug("Grava ou altera parametros do cliente.")

    # Adiciona suporte para requisições OPTIONS diretamente no endpoint
    if request.method == 'OPTIONS':
        return web.Response(headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        })

    try:
        # Extrai dados do JSON recebido
        data = await request.json()
        dominio_gesthor = data.get('dominio_gesthor', '')
        cliente_id_gesthor = data.get('cliente_id_gesthor', '')
        token_gesthor = data.get('token_gesthor', '')
        hora_manha = int(data.get('hora_manha', '0'))
        hora_tarde = int(data.get('hora_tarde', '0'))
        hora_noite = int(data.get('hora_noite', '0'))
        dominio_omniplus = data.get('dominio_omniplus', '')
        token_omniplus = data.get('token_omniplus', '')
        canal_omniplus = data.get('canal_omniplus', '')
        consulta = data.get('consulta', '')
        exame = data.get('exame', '')
        retorno = data.get('retorno', '')
        cirurgia = data.get('cirurgia', '')
        dias_consulta = int(data.get('dias_consulta', '0'))
        dias_exame = int(data.get('dias_exame', '0'))
        dias_retorno = int(data.get('dias_retorno', '0'))
        dias_cirurgia = int(data.get('dias_cirurgia', '0'))
        ativo = data.get('ativo', 'sim')
        auth_header = request.headers.get('Authorization', '')

        # Verifica se o token está presente e no formato correto
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        logging.debug(f"Requisição de parametros recebida - dominio_gesthor: {dominio_gesthor}")

        # Verificação de token
        if token != TOKEN_BD:
            logging.debug("Token inválido.")
            return web.json_response({
                "status": "error",
                "code": 401,
                "message": "Invalid token."
            }, status=401)

        # Conexão com o banco de dados
        try:
            async with request.app['db'].acquire() as connection:
                # Cadastra ou altera registro dos parametros do cliente
                logging.debug("Cadastra ou altera registro dos parametros do cliente.")
                query = """
                INSERT INTO tb_cliente (
                    dominio_gesthor, cliente_id_gesthor, bearer_gesthor,
                    dominio_omniplus, bearer_omniplus, canal_omniplus,
                    hora_manha, hora_tarde, hora_noite,
                    template_consulta, dias_consulta, template_exame,
                    dias_exame, template_retorno, dias_retorno,
                    template_cirurgia, dias_cirurgia, ativo
                )
                VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9,
                    $10, $11, $12, $13, $14, $15, $16, $17, $18
                )
                ON CONFLICT (dominio_gesthor)
                DO UPDATE SET
                    cliente_id_gesthor = EXCLUDED.cliente_id_gesthor,
                    bearer_gesthor = EXCLUDED.bearer_gesthor,
                    dominio_omniplus = EXCLUDED.dominio_omniplus,
                    bearer_omniplus = EXCLUDED.bearer_omniplus,
                    canal_omniplus = EXCLUDED.canal_omniplus,
                    hora_manha = EXCLUDED.hora_manha,
                    hora_tarde = EXCLUDED.hora_tarde,
                    hora_noite = EXCLUDED.hora_noite,
                    template_consulta = EXCLUDED.template_consulta,
                    dias_consulta = EXCLUDED.dias_consulta,
                    template_exame = EXCLUDED.template_exame,
                    dias_exame = EXCLUDED.dias_exame,
                    template_retorno = EXCLUDED.template_retorno,
                    dias_retorno = EXCLUDED.dias_retorno,
                    template_cirurgia = EXCLUDED.template_cirurgia,
                    dias_cirurgia = EXCLUDED.dias_cirurgia,
                    ativo = EXCLUDED.ativo;
                """
                success = await connection.execute(
                    query, dominio_gesthor, cliente_id_gesthor, token_gesthor,
                    dominio_omniplus, token_omniplus, canal_omniplus,
                    hora_manha, hora_tarde, hora_noite,
                    consulta, dias_consulta, exame, dias_exame,
                    retorno, dias_retorno, cirurgia, dias_cirurgia, ativo
                )

                # Se o registro foi encontrado, extrai os dados
                if success:
                    
                    logging.debug(f"Registro cadastrado ou atualizado com sucesso.")

                    return web.json_response({
                        "status": "success",
                        "code": 200,
                        "message": "Client parameters updated successfully."
                    }, status=200)
                else:
                    logging.debug("Nenhum registro gravado.")
                    return web.json_response({
                        "status": "success",
                        "code": 404,
                        "message": "Failed to update client parameters.",
                    }, status=404)
        except Exception as db_error:
            logging.error(f"Erro ao acessar o banco de dados: {db_error}")
            return web.json_response({
                "status": "error",
                "code": 500,
                "message": "Database error."
            }, status=500)

    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return web.json_response({
            "status": "error",
            "code": 500,
            "message": "Internal server error."
        }, status=500)

async def tratar_middleware_log():
    """Função que arquiva e apaga logs antigos."""
    log_dir_base = os.path.abspath("/app/igo/")  # Diretório base onde está o middleware.log
    log_dir = os.path.abspath("/app/igo/log/")  # Diretório de arquivamento middleware.log_aaaa-mm-dd
    log_file = os.path.join(log_dir_base, "middleware.log")
    log_archive_prefix = "middleware.log_"

    # Verifica se os diretórios existem, e cria se não existirem
    if not os.path.exists(log_dir_base):
        os.makedirs(log_dir_base)
        logging.info(f"Diretório base {log_dir_base} criado.")
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        logging.info(f"Diretório de arquivamento {log_dir} criado.")

    # Verifica se é o horário desejado (ex: 23:59)
    now = datetime.now()
    if now.hour == 23 and now.minute == 59:  # Mude para o horário real
        logging.info(f"Processo de arquivamento de log iniciado às {now.hour}:{now.minute}.")

        # Verifica se o arquivo middleware.log existe antes de arquivar
        if os.path.exists(log_file):
            try:
                if os.path.getsize(log_file) > 0:
                    # Arquiva o log atual com a data de hoje
                    archive_name = log_archive_prefix + now.strftime('%Y-%m-%d')
                    archive_file = os.path.join(log_dir, archive_name)
                    
                    # Realiza a cópia do arquivo de log de forma assíncrona
                    async with aiofiles.open(log_file, mode='r') as log_f, aiofiles.open(archive_file, mode='w') as archive_f:
                        async for line in log_f:
                            await archive_f.write(line)
                    logging.info(f"Arquivo de log arquivado como {archive_name}")
                    
                    # Limpa o conteúdo do middleware.log de forma assíncrona
                    async with aiofiles.open(log_file, mode='w') as log_f:
                        await log_f.write("")  # Isso irá limpar o arquivo
                    logging.info("Arquivo middleware.log zerado.")
                else:
                    logging.warning(f"O arquivo {log_file} está vazio, arquivamento não realizado.")
            
            except Exception as e:
                logging.error(f"Erro ao arquivar o log: {e}")
        else:
            logging.warning(f"O arquivo {log_file} não foi encontrado para arquivamento.")

        # Apagar logs com mais de 30 dias
        try:
            logging.info("Verificando arquivos antigos para exclusão.")
            thirty_days_ago = now - timedelta(days=30)
            for filename in os.listdir(log_dir):
                if filename.startswith(log_archive_prefix):
                    file_date_str = filename[len(log_archive_prefix):]
                    try:
                        file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                        if file_date < thirty_days_ago:
                            os.remove(os.path.join(log_dir, filename))
                            logging.info(f"Arquivo de log antigo {filename} apagado.")
                    except ValueError:
                        # Se a data no nome do arquivo não for válida, ignora o arquivo
                        logging.warning(f"Arquivo de log com nome inválido ignorado: {filename}")
        except Exception as e:
            logging.error(f"Erro ao verificar ou remover arquivos antigos: {e}")

# Função principal que roda a cada hora cheia
async def main_scheduler(app):
    """Função que roda a cada hora cheia para verificar tarefas agendadas."""
    logging.debug(f"Função que roda a cada hora cheia para verificar tarefas agendadas.")
    try:
        while True:
            # Passa o app['db'] para verificar_tarefas
            await verificar_tarefas(app['db'])

            # Aguarda até a próxima hora cheia
            now = datetime.now()
            minutos_faltando = 60 - now.minute
            segundos_faltando = 60 - now.second
            tempo_espera = minutos_faltando * 60 + segundos_faltando
            logging.info(f"Aguardando {tempo_espera} segundos até a próxima execução.")
            await asyncio.sleep(tempo_espera)
    except Exception as e:
        logging.error(f"Erro no scheduler principal: {e}")
    finally:
        await close_db(app)

async def start_scheduler(app):
    """Inicia o scheduler que roda a cada hora cheia como uma tarefa de segundo plano."""
    logging.debug(f"Inicia o scheduler que roda a cada hora cheia como uma tarefa de segundo plano.")
    app['scheduler_task'] = asyncio.create_task(main_scheduler(app))

async def stop_scheduler(app):
    """Encerra o scheduler ao finalizar o aplicativo."""
    logging.debug(f"Encerra o scheduler ao finalizar o aplicativo.")
    app['scheduler_task'].cancel()
    await app['scheduler_task']

async def cleanup_background_tasks(app):
    """Encerra as tarefas em segundo plano ao parar o servidor."""
    logging.debug(f"Encerra as tarefas em segundo plano ao parar o servidor.")
    await stop_scheduler(app)

async def init_app():
    """Inicialização do aplicativo web"""
    logging.debug(f"Inicialização do aplicativo web.")
    app = web.Application(middlewares=[cors_middleware])

    # Inicialização do banco de dados
    app.on_startup.append(init_db)
    app.on_cleanup.append(close_db)

    # Adiciona rotas
    app.router.add_post('/api/v1/template/return', handle_return)   # Rota para retorno da confirmação ou não do Omniplus interação do usuário.
    app.router.add_post('/login', login)                            # Rota para busca do login da aplicação web.
    app.router.add_post('/parametros', parametros)                  # Rota para gravação/alteração paramentors aplicação web.
    app.router.add_get('/consultaClientes', consultaClientes)       # Rota para consulta de clientes/dominios aplicação web.
    app.router.add_get('/consultaLogs', consultaLogs)               # Rota para consulta de log´s da aplicação na aplicação web.

    # Inicia o scheduler de tarefas
    app.on_startup.append(start_scheduler)          # Inicia o scheduler que roda a cada hora cheia responsável por buscar as agendas do Gesthor em uma tarefa de segundo plano.
    app.on_startup.append(start_background_tasks)   # Inicia tarefas em segundo plano/filas ao iniciar o servidor responsavél pelo envio dos templates ao contato.
    app.on_cleanup.append(cleanup_background_tasks) # Encerra tarefas em segundo plano ao parar o servidor.

    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(init_app(), host='0.0.0.0', port=8080)
    
