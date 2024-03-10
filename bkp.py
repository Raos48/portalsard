import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import requests
from datetime import datetime
import mysql.connector
from datetime import datetime, timedelta



pasta_raiz = os.getcwd()
headers_file_path = os.path.join(pasta_raiz, 'headers.txt')

# # Caminho para o seu certificado .pem baixado
# custom_certificate_path = "./meu_certificado.pem"

class TokenFetcher:
    def __init__(self):
        self.setup_driver()
        self.process_tasks()

    def setup_driver(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(headers_file_path, 'r') as file:
                self.headers = json.loads(file.read())
            print("Headers carregados com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar headers: {e}")

        try:
            requisicao = requests.get("https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/888296716",verify=False, headers=self.headers)
            if requisicao.status_code != 200:
                print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                print(f"API Offline - Data e hora: {current_time}")
                options = webdriver.ChromeOptions()
                options.add_argument('--ignore-certificate-errors-spki-list')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument("--log-level=3")
                options.add_argument("--disable-logging")
                options.page_load_strategy = 'normal'
                programa_pasta_raiz = os.path.dirname(os.path.abspath(__file__))
                os.environ["PATH"] += os.pathsep + programa_pasta_raiz
                driver = webdriver.Chrome(options=options)
                driver.maximize_window()
                driver.get("https://www-atendimento/")
                driver.implicitly_wait(10)
                driver.find_element(By.ID, "details-button").click()
                driver.find_element(By.ID, "proceed-link").click()

                time.sleep(3)
                print()
                print("Robô para Distribuição de Tarefas.")
                print()
                print("Aguardando Login no sistema PAT...")
                print()
                time.sleep(3)
                wait = WebDriverWait(driver, 120)  # Aguarda até 10 segundos
                element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/header/div[1]/span")))
                for i in range(30, 0, -1):
                    print(f"Aguardando: {i} segundos")
                    time.sleep(1)
                print("Tempo encerrado!")
                js_script = "return localStorage.getItem('ifs_auth');"
                js_script2 = "return localStorage.getItem('srv_auth');"
                resultado = driver.execute_script(js_script)
                token = driver.execute_script(js_script2)
                urllib3.disable_warnings()
                self.headers = {'Authorization': 'Bearer ' + resultado, 'Content-type': 'application/json',
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                                'tokenservidor': token, 'Accept': 'application/json'}

                # self.headers = {
                #     'Accept': 'application/json',
                #     'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                #     'Authorization': 'Bearer ' + resultado,
                #     'Connection': 'keep-alive',
                #     'Content-Type': 'application/json',
                #     'Cookie': '_pk_id.31.9ff2=44f8034a34099fa2.1709990667.; _pk_ref.31.9ff2=%5B%22%22%2C%22%22%2C1710081789%2C%22https%3A%2F%2Fgeridinss.dataprev.gov.br%3A8443%2F%22%5D; _pk_ses.31.9ff2=1',
                #     'DNT': '1',
                #     'Origin': 'https://atendimento.inss.gov.br',
                #     'Referer': 'https://atendimento.inss.gov.br/',
                #     'Sec-Fetch-Dest': 'empty',
                #     'Sec-Fetch-Mode': 'cors',
                #     'Sec-Fetch-Site': 'same-origin',
                #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                #     'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                #     'sec-ch-ua-mobile': '?0',
                #     'sec-ch-ua-platform': '"Windows"',
                #     'tokenServidor': token,
                # }

                driver.quit()
                with open('headers.txt', 'w') as file:
                    file.write(json.dumps(self.headers))
                return self.headers
            else:
                print(f"API Online - Data e hora: {current_time}")
        except Exception as e:
            print(f"Erro de conexão: {e}")

    def verifica_API(self):
        connection = None
        cursor = None
        try:
            connection = self.connect_to_database()
            cursor = connection.cursor(buffered=True)
            url = "https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/304776827?servidor=true"
            resposta = requests.get(url, verify=False, headers=self.headers)
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if resposta.status_code == 200:
                status = "Online"
            else:
                status = "Offline"
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "Offline"
        except mysql.connector.Error as err:
            print(f"Erro no banco de dados: {err}")
            return
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return
        finally:
            if cursor and connection:
                try:
                    sql_insert = "INSERT INTO status_api (status, data) VALUES (%s, %s)"
                    cursor.execute(sql_insert, (status, data))
                    connection.commit()
                    print(f"A API está {status} em {data}")
                except Exception as e:
                    print(f"Erro ao inserir no banco de dados: {e}")
                finally:
                    cursor.close()
                    connection.close()

    def process_tasks(self):
        while True:
            self.process_single_task()
            time.sleep(10)
            self.verifica_API()
            print("Buscando solicitações....")
            print()

    def process_single_task(self):
        try:
            with self.connect_to_database() as connection:
                with connection.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, tipo, protocolo FROM solicitacoes WHERE status IS NULL OR status = ''")
                    registros = cursor.fetchall()
                    if not registros:
                        print("Nenhum registro para processar.")
                        return
                    print(f"Processando {len(registros)} registros...")
                    for id_linha, tipo, protocolo in registros:
                        print()
                        with open('servidores.json', 'r') as file:
                            servidores = json.load(file)

                        if (tipo == "Atribuir responsável" or tipo == "Excluir responsável") and protocolo is None:
                            status = "Favor informar o Numero do Protocolo"
                            dt_conclusao = datetime.now()
                            sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                            cursor.execute(sql_update, (status, dt_conclusao, id_linha))
                            connection.commit()
                            print(f"Registro {id_linha} processado com sucesso.")
                            break

                        if protocolo is not None:
                            url = f"https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}?servidor=true"
                            resposta = requests.get(url, verify=False, headers=self.headers)
                            sard_gex_anp = "14409"

                            if resposta.status_code == 200:
                                cursor.execute(
                                    "SELECT id, protocolo, tipo, matricula, unidade, status, dt_solicitacao, dt_conclusao, solicitante FROM solicitacoes WHERE protocolo = %s AND (status IS NULL OR status = '')",
                                    (protocolo,))
                                resultado = cursor.fetchone()

                                if resultado:
                                    id_solicitacao, protocolo_solicitacao, tipo, matricula, unidade, status, dt_solicitacao, dt_conclusao, solicitante = resultado
                                    print(
                                        f"ID: {id_solicitacao}, Protocolo: {protocolo_solicitacao}, Tipo: {tipo}, Matrícula: {matricula}, Unidade: {unidade}, Status: {status}, Data Solicitação: {dt_solicitacao}, Data Conclusão: {dt_conclusao}, Solicitante: {solicitante}")
                                else:
                                    print(f"Nenhum registro encontrado para o protocolo {protocolo}")
                            else:
                                print(f"Erro requisição")

                            print(f"Tipo para protocolo {protocolo}: {tipo}")

                            if tipo == "Transferir tarefa":
                                payload = "{'justificativa':'Transferencia para unidade responsavel.'}"
                                requisicao = requests.put(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}/transferencia/{sard_gex_anp}?retornarTarefa=true',
                                    verify=False, headers=self.headers, data=payload)
                                resposta = requisicao.json()
                                mensagem = resposta['mensagem']
                                status = mensagem
                                print(status)
                                sql_update = "UPDATE solicitacoes SET status = %s WHERE id = %s"
                                cursor.execute(sql_update, (status, id_solicitacao))
                                connection.commit()


                            elif tipo == "Atribuir responsável":
                                siape_procurado = matricula
                                id_responsavel = None
                                for id_, info in servidores.items():
                                    if info['SIAPE'] == siape_procurado:
                                        id_responsavel = str(id_)
                                        break
                                servidor = '{"responsaveis":[{"id":' + id_responsavel + '}]}'
                                requisicao = requests.post(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}',verify=False, headers=self.headers, data=servidor)
                                if requisicao.status_code != 200:
                                    print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                                    continue
                                status = "Responsável incluído com sucesso."
                                dt_conclusao = datetime.now()
                                sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                cursor.execute(sql_update, (status, dt_conclusao, id_solicitacao))
                                connection.commit()
                                print(f"Registro {id_solicitacao} processado com sucesso.")

                            elif tipo == 'Excluir responsável':
                                requisicao_get = requests.get(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}', verify=False, headers=self.headers)
                                if requisicao_get.status_code == 200:
                                    tarefa = requisicao_get.json()
                                    responsaveis = tarefa['responsaveis']['responsaveis']
                                    print("=============================================")
                                    print(f"Responsáveis:",responsaveis)
                                    print("=============================================")

                                    if len(responsaveis) == 0:
                                        print("Não há responsáveis na tarefa.")
                                        status = "Não há responsáveis na tarefa."
                                        dt_conclusao = datetime.now()
                                        sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                        cursor.execute(sql_update, (status, dt_conclusao, id_solicitacao))
                                        connection.commit()
                                        print(f"Registro {id_solicitacao} processado com sucesso.")
                                        break

                                    for responsavel in responsaveis:
                                        if responsavel['siape'] == int(solicitante):
                                            id_responsavel = responsavel['id']
                                            break

                                    requisicao_delete = requests.delete( f'https://atendimento.inss.gov.br/apis/tarefasApi/responsaveis/{id_responsavel}/tarefa/{protocolo}',verify=False, headers=self.headers)
                                    if requisicao_delete.status_code == 200:
                                        print(f"Exclusão do responsável efetuada com sucesso")
                                        status = "Exclusão do responsável efetuada com sucesso"
                                        dt_conclusao = datetime.now()
                                        sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                        cursor.execute(sql_update, (status, dt_conclusao, id_solicitacao))
                                        connection.commit()
                                        print(f"Registro {id_solicitacao} processado com sucesso.")
                                    else:
                                        print( f"Erro na requisição DELETE para o responsável {id_responsavel}. Código de status: {requisicao_delete.status_code}")

                                    # if len(responsaveis) != 0:
                                    #     for responsavel in responsaveis:
                                    #         id_responsavel = responsavel['id']
                                    #         requisicao_delete = requests.delete( f'https://atendimento.inss.gov.br/apis/tarefasApi/responsaveis/{id_responsavel}/tarefa/{protocolo}',verify=False, headers=self.headers)
                                    #         if requisicao_delete.status_code == 200:
                                    #             print(f"Exclusão do responsável efetuada com sucesso")
                                    #             status = "Exclusão do responsável efetuada com sucesso"
                                    #             dt_conclusao = datetime.now()
                                    #             sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                    #             cursor.execute(sql_update, (status, dt_conclusao, id_solicitacao))
                                    #             connection.commit()
                                    #             print(f"Registro {id_solicitacao} processado com sucesso.")
                                    #         else:
                                    #             print( f"Erro na requisição DELETE para o responsável {id_responsavel}. Código de status: {requisicao_delete.status_code}")
                                    # else:
                                    #     print("Não há responsáveis na tarefa.")
                                    #     status = "Não há responsáveis na tarefa."
                                    #     dt_conclusao = datetime.now()
                                    #     sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                    #     cursor.execute(sql_update, (status, dt_conclusao, id_solicitacao))
                                    #     connection.commit()
                                    #     print(f"Registro {id_solicitacao} processado com sucesso.")

                                else:
                                    print(f"Erro na requisição GET. Código de status: {requisicao_get.status_code}")
                                    status = "Erro na requisição GET. Código de status: {requisicao_get.status_code}"
                                    dt_conclusao = datetime.now()
                                    sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                    cursor.execute(sql_update, (status, dt_conclusao, id_solicitacao))
                                    connection.commit()

                        if protocolo is None:
                            cursor.execute("SELECT tipo FROM solicitacoes WHERE status IS NULL OR status = ''")
                            tipo = cursor.fetchone()

                            if tipo and tipo[0] == "Solicitar Tarefas BI":
                                sql_query = """
                                SELECT solicitante
                                FROM solicitacoes
                                WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas BI' AND (status IS NULL OR status = '')
                                """
                                cursor.execute(sql_query)
                                resultado = cursor.fetchone()

                                # CASO POSSUA TAREFAS de Solicitar BI execute
                                if resultado:
                                    siape_procurado = resultado[0]
                                    id_responsavel = None
                                    for id_, info in servidores.items():
                                        if info['SIAPE'] == siape_procurado:
                                            id_responsavel = str(id_)
                                            break
                                    url = "https://atendimento.inss.gov.br/apis/tarefasApi/profissional/dashboard"

                                    params = {
                                        "indexVisao": 2,
                                        "limit": 5,
                                        "offset": 0,
                                        "sort_by": "DATA_ENTRADA_REQUERIMENTO",
                                        "order_by": "ASCENDING"
                                    }

                                    # data = {
                                    #     "status": "PENDENTE_E_CUMPRIMENTO_DE_EXIGENCIA",
                                    #     "grupoServicos": [
                                    #         {"label": "Benefício por Incapacidade", "value": "123", "id": 123}],
                                    #     "servicos": [
                                    #         {"label": "Auxílio-Doença - Rural (Acerto Pós-perícia) - TADR",
                                    #          "value": "5473",
                                    #          "id": 5473}
                                    #     ]
                                    # }

                                    data = {
                                        "status": "PENDENTE_E_CUMPRIMENTO_DE_EXIGENCIA",
                                        "grupoServicos": [
                                            {"label": "Benefício por Incapacidade", "value": "123", "id": 123}],
                                        "servicos": [
                                            {"label": "Auxílio-Doença - Rural (Acerto Pós-perícia) - TADR", "value": "5473",
                                             "id": 5473},
                                            {"label": "Auxílio-Doença - Urbano (Acerto Pós-perícia) - TADU",
                                             "value": "5474", "id": 5474}
                                        ]
                                    }

                                    response = requests.post(url, json=data, headers=self.headers, params=params)

                                    if response.status_code == 204:
                                        try:
                                            # Prepara a query SQL para selecionar o ID
                                            sql_query = """
                                            SELECT id
                                            FROM solicitacoes
                                            WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas BI' AND (status IS NULL OR status = '')
                                            """
                                            cursor.execute(sql_query)
                                            resultado = cursor.fetchone()

                                            # Verifica se um resultado foi encontrado
                                            if resultado:
                                                id_distribuir = resultado[0]
                                                dt_conclusao = datetime.now()
                                                status = "Não há tarefas na fila da Unidade Gerencial"
                                                sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                                cursor.execute(sql_update, (status, dt_conclusao, id_distribuir))
                                                connection.commit()
                                                print("Não há mais tarefas na fila da Unidade")
                                                break
                                            else:
                                                print("Nenhuma solicitação correspondente encontrada.")
                                        except Exception as e:
                                            print(f"Ocorreu um erro: {e}")
                                            connection.rollback()
                                        finally:
                                            cursor.close()
                                            connection.close()
                                            pass

                                    response_json = response.json()
                                    protocolos = [item['numeroProtocolo'] for item in response_json]

                                    for protocolo in protocolos:
                                        servidor = '{"responsaveis":[{"id":' + id_responsavel + '}]}'
                                        sucesso = False
                                        while not sucesso:
                                            try:
                                                requisicao_get = requests.get(
                                                    f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}',
                                                    verify=False, headers=self.headers)
                                                if requisicao_get.status_code == 200:
                                                    tarefa = requisicao_get.json()
                                                    responsaveis = tarefa['responsaveis']['responsaveis']
                                                    if len(responsaveis) == 0:
                                                        requisicao = requests.post(
                                                            f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}',
                                                            verify=False, headers=self.headers, data=servidor)
                                                        if requisicao.status_code != 200:
                                                            print(
                                                                f"Erro na requisição. Código de status: {requisicao.status_code}")
                                                            sucesso = True
                                                            continue
                                                        else:
                                                            print(
                                                                f"Erro na requisição. Código de status: {requisicao.status_code}")
                                                    else:
                                                        print("Tarefa já possui responsável..")
                                                        sucesso = True
                                                        pass
                                                else:
                                                    print("Requisição falhou - looping - tentar novamente.")
                                                    continue
                                            except Exception as e:
                                                print(f"Erro ao fazer a requisição: {e}")

                                        tipo = 'Solicitar Tarefas BI'
                                        matricula = siape_procurado
                                        solicitante = siape_procurado
                                        status = "Responsável incluído com sucesso."

                                        sql_insert = """
                                        INSERT INTO solicitacoes (protocolo, matricula, solicitante, tipo, status, dt_solicitacao, dt_conclusao)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """

                                        valores = (
                                            protocolo, matricula, solicitante, tipo, status, datetime.now(),
                                            datetime.now())
                                        cursor.execute(sql_insert, valores)
                                        connection.commit()
                                        print(
                                            f"Tarefa Distribuída com sucesso:{protocolo}, {matricula}, {solicitante}, {tipo}, {status}, {datetime.now()}, {datetime.now()}")

                                    # Finalizou Distribuição
                                    sql_query = """
                                    SELECT id
                                    FROM solicitacoes
                                    WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas BI' AND (status IS NULL OR status = '')
                                    """
                                    cursor.execute(sql_query)
                                    resultado = cursor.fetchone()
                                    id_distribuir = resultado[0]
                                    dt_conclusao = datetime.now()
                                    status = "Tarefas Distribuídas com sucesso."
                                    sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                    cursor.execute(sql_update, (status, dt_conclusao, id_distribuir))
                                    connection.commit()
                                    print("Distribuição Finalizada")
                                    print()
                            if tipo and tipo[0] == "Solicitar Tarefas de Análise de Acordão":
                                sql_query = """
                                SELECT solicitante,especie
                                FROM solicitacoes
                                WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Análise de Acordão' AND (status IS NULL OR status = '')
                                """
                                cursor.execute(sql_query)
                                resultado = cursor.fetchone()
                                if resultado:
                                    siape_procurado = resultado[0]
                                    especie = resultado[1]
                                else:
                                    print("Nenhum resultado encontrado.")
                                    especie = None

                                id_responsavel = None
                                for id_, info in servidores.items():
                                    if info['SIAPE'] == siape_procurado:
                                        id_responsavel = str(id_)
                                        break

                                limite = 0

                                while limite != 5:

                                    sql_query_estoque = """
                                    SELECT id, subtarefa, especie
                                    FROM estoque
                                    WHERE (status IS NULL OR status = '') AND especie = %s
                                    LIMIT 1
                                    """

                                    cursor.execute(sql_query_estoque, (especie,))
                                    registro = cursor.fetchone()

                                    if not registro:
                                        print("Não há tarefas para processar.")
                                        break

                                    id, subtarefa, especie = registro
                                    protocolo = subtarefa

                                    # verificar responsáveis
                                    requisicao = requests.get(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}', verify=False, headers=self.headers)
                                    if requisicao.status_code != 200:
                                        print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                                        continue
                                    tarefa = requisicao.json()
                                    responsaveis = tarefa['responsaveis']['responsaveis']
                                    if len(responsaveis) != 0:
                                        status = "Tarefa já possui responsável"
                                        sql_update_estoque = "UPDATE estoque SET status = %s WHERE subtarefa = %s"
                                        cursor.execute(sql_update_estoque, (status, protocolo))
                                        connection.commit()
                                        print(f"tarefa já possui responsável atribuído.")
                                        print(protocolo, status)
                                        continue

                                    # identificar Unidade
                                    requisicao = requests.get(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}',
                                        verify=False, headers=self.headers)
                                    if requisicao.status_code != 200:
                                        print(requisicao.text)
                                        time.sleep(2)
                                        continue
                                    tarefa = requisicao.json()
                                    codigo_unidade = tarefa['codigoUnidade']
                                    status_tarefa = tarefa['status']
                                    print(protocolo, codigo_unidade, status_tarefa)
                                    if status_tarefa != "PENDENTE" and status_tarefa != "CUMPRIMENTO_DE_EXIGENCIA":
                                        status = "CONCLUÍDA"
                                        sql_update_estoque = "UPDATE estoque SET status = %s WHERE subtarefa = %s"
                                        cursor.execute(sql_update_estoque, (status, protocolo))
                                        connection.commit()
                                        print(f"tarefa já encontra-se{status_tarefa}")
                                        time.sleep(2)
                                        continue

                                    if codigo_unidade == '23150520' or codigo_unidade == '23150513':
                                        payload = "{'justificativa':'Transferencia para unidade responsavel.'}"
                                        requisicao = requests.put(
                                            f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}/transferencia/9958?retornarTarefa=true',
                                            verify=False, headers=self.headers, data=payload)
                                        if requisicao.status_code != 200:
                                            print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                                            time.sleep(2)
                                            continue
                                        resposta = requisicao.json()
                                        mensagem = resposta['mensagem']
                                        print(mensagem)

                                    servidor = '{"responsaveis":[{"id":' + str(id_responsavel) + '}]}'
                                    url_da_api = f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}'
                                    requisicao = requests.post(url_da_api, verify=False, headers=self.headers,
                                                               data=servidor)
                                    if requisicao.status_code != 200:
                                        print(
                                            f"Erro na requisição para o protocolo {protocolo}. Código de status: {requisicao.status_code}")
                                        time.sleep(2)
                                        continue
                                    else:
                                        status = "Responsável incluído com sucesso."
                                        sql_update_estoque = "UPDATE estoque SET status = %s WHERE subtarefa = %s"
                                        cursor.execute(sql_update_estoque, (status, protocolo))
                                        connection.commit()
                                        matricula = siape_procurado
                                        solicitante = siape_procurado
                                        tipo = "Solicitar Tarefas de Análise de Acordão"
                                        sql_insert = """
                                        INSERT INTO solicitacoes (protocolo, matricula, solicitante, tipo, status, dt_solicitacao, dt_conclusao)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """
                                        valores = (
                                            protocolo, matricula, solicitante, tipo, status, datetime.now(),
                                            datetime.now())
                                        cursor.execute(sql_insert, valores)
                                        connection.commit()
                                        print(
                                            f"Tarefa Distribuída com sucesso:{protocolo}, {matricula}, {solicitante}, {tipo}, {status}, {datetime.now()}, {datetime.now()}")
                                        limite += 1

                                sql_query = """
                                SELECT id
                                FROM solicitacoes
                                WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Análise de Acordão' AND (status IS NULL OR status = '')
                                """
                                cursor.execute(sql_query)
                                resultado = cursor.fetchone()
                                id_distribuir = resultado[0]
                                dt_conclusao = datetime.now()
                                status = "Tarefas Distribuídas com sucesso."
                                sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                cursor.execute(sql_update, (status, dt_conclusao, id_distribuir))
                                connection.commit()
                                print("Distribuição Finalizada")
                                print()
                            if tipo and tipo[0] == "Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO":
                                sql_query = """
                                SELECT solicitante
                                FROM solicitacoes
                                WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO' AND (status IS NULL OR status = '')
                                """
                                cursor.execute(sql_query)
                                resultado = cursor.fetchone()


                                if resultado:
                                    siape_procurado = resultado[0]


                                data_hoje = datetime.now().date()

                                # Verificar se já tem solicitação na data de hoje
                                sql_query_verificacao = """
                                SELECT COUNT(*)
                                FROM solicitacoes
                                WHERE tipo = 'Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO'
                                AND status = 'Tarefas Distribuídas com sucesso.'
                                AND solicitante = %s
                                AND DATE(dt_solicitacao) = %s
                                """
                                cursor.execute(sql_query_verificacao, (siape_procurado, data_hoje))
                                resultado_verificacao = cursor.fetchone()

                                if resultado_verificacao[0] > 0:
                                    # Caso já exista um registro com as condições especificadas, executar este bloco
                                    sql_query_distribuicao_finalizada = """
                                    SELECT id
                                    FROM solicitacoes
                                    WHERE protocolo IS NULL
                                    AND tipo = 'Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO'
                                    AND (status IS NULL OR status = '')
                                    AND solicitante = %s
                                    LIMIT 1
                                    """
                                    cursor.execute(sql_query_distribuicao_finalizada, (siape_procurado,))
                                    resultado_distribuicao = cursor.fetchone()

                                    if resultado_distribuicao:
                                        id_distribuir, = resultado_distribuicao
                                        dt_conclusao = datetime.now()
                                        status = "Limite de Solicitações diárias de Análise de Acordão Não Provido atingido."
                                        sql_update_distribuicao = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                        cursor.execute(sql_update_distribuicao, (status, dt_conclusao, id_distribuir))
                                        connection.commit()
                                        print("Distribuição Finalizada")
                                        print()
                                else:
                                    sql_query = """
                                    SELECT solicitante
                                    FROM solicitacoes
                                    WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO' AND (status IS NULL OR status = '')
                                    """
                                    cursor.execute(sql_query)
                                    resultado = cursor.fetchone()
                                    if resultado:
                                        siape_procurado = resultado[0]
                                    else:
                                        print("Nenhum resultado encontrado.")

                                    id_responsavel = None
                                    for id_, info in servidores.items():
                                        if info['SIAPE'] == siape_procurado:
                                            id_responsavel = str(id_)
                                            break

                                    limite = 0

                                    while limite != 5:

                                        sql_query_estoque = """
                                        SELECT id, subtarefa, situacao
                                        FROM estoque
                                        WHERE (status IS NULL OR status = '') AND situacao = 'NÃO PROVIDO'
                                        LIMIT 1
                                        """

                                        cursor.execute(sql_query_estoque)
                                        registro = cursor.fetchone()
                                        sit_estoque = False
                                        if not registro:
                                            print("Não há tarefas para processar.")
                                            sit_estoque = True
                                            break

                                        id, subtarefa, situacao = registro
                                        protocolo = subtarefa

                                        #verificar responsáveis
                                        requisicao = requests.get(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}',verify=False, headers=self.headers)
                                        if requisicao.status_code != 200:
                                            print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                                            continue
                                        tarefa = requisicao.json()
                                        responsaveis = tarefa['responsaveis']['responsaveis']
                                        if len(responsaveis) != 0:
                                            status = "Tarefa já possui responsável"
                                            sql_update_estoque = "UPDATE estoque SET status = %s WHERE subtarefa = %s"
                                            cursor.execute(sql_update_estoque, (status, protocolo))
                                            connection.commit()
                                            print(f"tarefa já possui responsável atribuído.")
                                            print(protocolo,status)
                                            continue


                                        # identificar Unidade
                                        requisicao = requests.get( f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}',verify=False, headers=self.headers)
                                        if requisicao.status_code != 200:
                                            print(requisicao.text)
                                            time.sleep(2)
                                            continue
                                        tarefa = requisicao.json()
                                        codigo_unidade = tarefa['codigoUnidade']
                                        status_tarefa = tarefa['status']
                                        print(protocolo, codigo_unidade, status_tarefa)
                                        if status_tarefa != "PENDENTE" and status_tarefa != "CUMPRIMENTO_DE_EXIGENCIA":
                                            status = "CONCLUÍDA"
                                            sql_update_estoque = "UPDATE estoque SET status = %s WHERE subtarefa = %s"
                                            cursor.execute(sql_update_estoque, (status, protocolo))
                                            connection.commit()
                                            print(f"tarefa já encontra-se{status_tarefa}")
                                            time.sleep(2)
                                            continue

                                        if codigo_unidade == '23150520' or codigo_unidade == '23150513':
                                            payload = "{'justificativa':'Transferencia para unidade responsavel.'}"
                                            requisicao = requests.put(
                                                f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}/transferencia/9958?retornarTarefa=true',
                                                verify=False, headers=self.headers, data=payload)
                                            if requisicao.status_code != 200:
                                                print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                                                time.sleep(2)
                                                continue
                                            resposta = requisicao.json()
                                            mensagem = resposta['mensagem']
                                            print(mensagem)

                                        servidor = '{"responsaveis":[{"id":' + str(id_responsavel) + '}]}'
                                        url_da_api = f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}'
                                        requisicao = requests.post(url_da_api, verify=False, headers=self.headers,
                                                                   data=servidor)
                                        if requisicao.status_code != 200:
                                            print(
                                                f"Erro na requisição para o protocolo {protocolo}. Código de status: {requisicao.status_code}")
                                            time.sleep(2)
                                            continue
                                        else:
                                            status = "Responsável incluído com sucesso."
                                            sql_update_estoque = "UPDATE estoque SET status = %s WHERE subtarefa = %s"
                                            cursor.execute(sql_update_estoque, (status, protocolo))
                                            connection.commit()
                                            matricula = siape_procurado
                                            solicitante = siape_procurado
                                            tipo = "Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO"
                                            sql_insert = """
                                            INSERT INTO solicitacoes (protocolo, matricula, solicitante, tipo, status, dt_solicitacao, dt_conclusao)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                                            """
                                            valores = (protocolo, matricula, solicitante, tipo, status, datetime.now(),
                                                       datetime.now())
                                            cursor.execute(sql_insert, valores)
                                            connection.commit()
                                            print(
                                                f"Tarefa Distribuída com sucesso:{protocolo}, {matricula}, {solicitante}, {tipo}, {status}, {datetime.now()}, {datetime.now()}")
                                            limite += 1

                                    if sit_estoque:
                                        sql_query = """
                                        SELECT id
                                        FROM solicitacoes
                                        WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO' AND (status IS NULL OR status = '')
                                        """
                                        cursor.execute(sql_query)
                                        resultado = cursor.fetchone()
                                        id_distribuir = resultado[0]
                                        dt_conclusao = datetime.now()
                                        status = "Não há mais tarefas Análise de Acordão - NÃO PROVIDO para distribuição"
                                        sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                        cursor.execute(sql_update, (status, dt_conclusao, id_distribuir))
                                        connection.commit()
                                        print("Distribuição Finalizada")
                                        print()
                                    else:
                                        sql_query = """
                                        SELECT id
                                        FROM solicitacoes
                                        WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Análise de Acordão - NÃO PROVIDO' AND (status IS NULL OR status = '')
                                        """
                                        cursor.execute(sql_query)
                                        resultado = cursor.fetchone()
                                        id_distribuir = resultado[0]
                                        dt_conclusao = datetime.now()
                                        status = "Tarefas Distribuídas com sucesso."
                                        sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                        cursor.execute(sql_update, (status, dt_conclusao, id_distribuir))
                                        connection.commit()
                                        print("Distribuição Finalizada")
                                        print()

                            if tipo and tipo[0] == "Solicitar Tarefas de Instrução de Recurso":
                                sql_query = """
                                SELECT solicitante
                                FROM solicitacoes
                                WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Instrução de Recurso' AND (status IS NULL OR status = '')
                                """
                                cursor.execute(sql_query)
                                resultado = cursor.fetchone()
                                if resultado:
                                    siape_procurado = resultado[0]
                                else:
                                    print("Nenhum resultado encontrado.")

                                id_responsavel = None
                                for id_, info in servidores.items():
                                    if info['SIAPE'] == siape_procurado:
                                        id_responsavel = str(id_)
                                        break

                                limite = 0

                                while limite != 5:
                                    print()
                                    sql_query_instrucao = """
                                    SELECT id, subtarefa
                                    FROM instrucao
                                    WHERE (status IS NULL OR status = '')
                                    LIMIT 1
                                    """

                                    cursor.execute(sql_query_instrucao)
                                    registro = cursor.fetchone()

                                    if not registro:
                                        print("Não há tarefas para processar.")
                                        break

                                    id, subtarefa = registro
                                    protocolo = subtarefa

                                    # verificar responsáveis
                                    requisicao = requests.get(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}', verify=False, headers=self.headers)
                                    if requisicao.status_code != 200:
                                        print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                                        continue
                                    tarefa = requisicao.json()
                                    responsaveis = tarefa['responsaveis']['responsaveis']
                                    if len(responsaveis) != 0:
                                        status = "Tarefa já possui responsável"
                                        sql_update_estoque = "UPDATE instrucao SET status = %s WHERE subtarefa = %s"
                                        cursor.execute(sql_update_estoque, (status, protocolo))
                                        connection.commit()
                                        print(f"tarefa já possui responsável atribuído.")
                                        print(protocolo, status)
                                        continue

                                    # identificar Unidade
                                    requisicao = requests.get(f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}',
                                        verify=False, headers=self.headers)
                                    if requisicao.status_code != 200:
                                        print(requisicao.text)
                                        time.sleep(2)
                                        continue
                                    tarefa = requisicao.json()
                                    codigo_unidade = tarefa['codigoUnidade']
                                    status_tarefa = tarefa['status']
                                    print(protocolo, codigo_unidade, status_tarefa)
                                    if status_tarefa != "PENDENTE" and status_tarefa != "CUMPRIMENTO_DE_EXIGENCIA":
                                        status = "CONCLUÍDA"
                                        sql_update_instrucao = "UPDATE instrucao SET status = %s WHERE subtarefa = %s"
                                        cursor.execute(sql_update_instrucao, (status, protocolo))
                                        connection.commit()
                                        print(f"tarefa já encontra-se{status_tarefa}")
                                        time.sleep(2)
                                        continue

                                    if codigo_unidade == '23150520' or codigo_unidade == '23150513':
                                        payload = "{'justificativa':'Transferencia para unidade responsavel.'}"
                                        requisicao = requests.put(
                                            f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/tarefas/{protocolo}/transferencia/9958?retornarTarefa=true',
                                            verify=False, headers=self.headers, data=payload)
                                        if requisicao.status_code != 200:
                                            print(f"Erro na requisição. Código de status: {requisicao.status_code}")
                                            time.sleep(2)
                                            continue
                                        resposta = requisicao.json()
                                        mensagem = resposta['mensagem']
                                        print(mensagem)

                                    if codigo_unidade == '23150515':
                                        status = "23150515"
                                        sql_update_instrucao = "UPDATE instrucao SET status = %s WHERE subtarefa = %s"
                                        cursor.execute(sql_update_instrucao, (status, protocolo))
                                        connection.commit()
                                        continue

                                    servidor = '{"responsaveis":[{"id":' + str(id_responsavel) + '}]}'
                                    url_da_api = f'https://vip-pportalspaapr01.inss.prevnet/apis/tarefasApi/responsaveis/{protocolo}'
                                    requisicao = requests.post(url_da_api, verify=False, headers=self.headers,
                                                               data=servidor)
                                    if requisicao.status_code != 200:
                                        print(
                                            f"Erro na requisição para o protocolo {protocolo}. Código de status: {requisicao.status_code}")
                                        time.sleep(2)
                                        continue
                                    else:
                                        status = "Responsável incluído com sucesso."
                                        sql_update_instrucao = "UPDATE instrucao SET status = %s WHERE subtarefa = %s"
                                        cursor.execute(sql_update_instrucao, (status, protocolo))
                                        connection.commit()

                                        matricula = siape_procurado
                                        solicitante = siape_procurado
                                        tipo = "Solicitar Tarefas de Instrução de Recurso"
                                        sql_insert = """
                                        INSERT INTO solicitacoes (protocolo, matricula, solicitante, tipo, status, dt_solicitacao, dt_conclusao)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """
                                        valores = (
                                            protocolo, matricula, solicitante, tipo, status, datetime.now(),
                                            datetime.now())
                                        cursor.execute(sql_insert, valores)
                                        connection.commit()
                                        print(
                                            f"Tarefa Distribuída com sucesso:{protocolo}, {matricula}, {solicitante}, {tipo}, {status}, {datetime.now()}, {datetime.now()}")
                                        limite += 1

                                sql_query = """
                                SELECT id
                                FROM solicitacoes
                                WHERE protocolo IS NULL AND tipo = 'Solicitar Tarefas de Instrução de Recurso' AND (status IS NULL OR status = '')
                                """
                                cursor.execute(sql_query)
                                resultado = cursor.fetchone()
                                id_distribuir = resultado[0]
                                dt_conclusao = datetime.now()
                                status = "Tarefas Distribuídas com sucesso."
                                sql_update = "UPDATE solicitacoes SET status = %s, dt_conclusao = %s WHERE id = %s"
                                cursor.execute(sql_update, (status, dt_conclusao, id_distribuir))
                                connection.commit()
                                print("Distribuição Finalizada")
                                print()

                    cursor.close()
                    connection.close()

        except mysql.connector.Error as err:
            print(f"Erro no banco de dados: {err}")
        except Exception as e:
            print(f"Erro: {e}")

    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='db_sard'
            )
            return connection
        except mysql.connector.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            exit()

if __name__ == "__main__":
    PATDistributor = TokenFetcher()
