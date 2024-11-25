import pandas as pd
from threading import Thread
import queue
from tqdm import tqdm
from time import sleep
from utils.telnet_utils import login, logout, telnet_session, extrair_dados
from utils.logs_utils import log_execucao


def trata_origem(retorno, olt_origem, slot_origem):
    filtered_lines = [line for line in retorno.splitlines()
                      if line.startswith(olt_origem)]

    data = [line.split('\t') for line in filtered_lines]

    df = pd.DataFrame(data, columns=['OLTID', 'PONID', 'ONU_ID', 'NOVO_NOME',
                                     'DESC', 'ONUTYPE', 'IP', 'AUTHTYPE', 'MAC', 'LOID', 'PWD', 'SWVER'])

    df[['NUMERO1', 'NUMERO2', 'SLOT', 'PON']
       ] = df['PONID'].str.split('-', expand=True)

    df = df.query('SLOT == @slot_origem')

    df = df.drop(columns=['OLTID', 'DESC', 'ONUTYPE', 'IP',
                          'AUTHTYPE', 'LOID', 'PWD', 'SWVER', 'PONID', 'ONU_ID', 'NUMERO1', 'NUMERO2'])

    df['MAC'] = df['MAC'].str.strip()
    df = df[['MAC', 'NOVO_NOME']]
    return df


def trata_destino(retorno, olt_destino, slot_destino, pon_destino):
    filtered_lines = [line for line in retorno.splitlines()
                      if line.startswith(olt_destino)]

    data = [line.split('\t') for line in filtered_lines]

    # Defino as colunas e monto o dataframe
    df = pd.DataFrame(data, columns=['OLTID', 'PONID', 'ONU_ID', 'ANTIGO_NOME',
                                     'DESC', 'ONUTYPE', 'IP', 'AUTHTYPE', 'MAC', 'LOID', 'PWD', 'SWVER'])

    # Splita o PONID em 4
    df_split = df['PONID'].str.split('-', expand=True)
    # Verifique se a divisão gerou exatamente 4 colunas
    if df_split.shape[1] == 4:
        df[['NUMERO1', 'NUMERO2', 'SLOT', 'PON']] = df_split
    else:
        print(f"Erro: PONID com formato inesperado:\n{df['PONID']}")
        raise ValueError("Formato inconsistente em PONID.")

    # Dropo colunas desnecessárias para o processo
    df = df.drop(columns=['DESC', 'ONUTYPE', 'IP',
                          'AUTHTYPE', 'LOID', 'PWD', 'SWVER', 'NUMERO1', 'NUMERO2', 'PONID'])

    # Removo espaçmentos antes e depois do MAC
    df['MAC'] = df['MAC'].str.strip()

    # Reorganizo as colunas
    df = df[['MAC', 'OLTID', 'ANTIGO_NOME', 'SLOT', 'PON', 'ONU_ID']]

    # Aplicar filtro de SLOT
    df = df.query('SLOT == @slot_destino')

    # Aplicar filtro de PON
    if pon_destino != '0':
        df = df.query('PON == @pon_destino')
    return df


def conecta_extrai(username, password, host_unm, host_olt):
    with telnet_session(host_unm, 3337) as tn:
        login(tn, username, password)
        command_extract = f"LST-ONU::OLTID={host_olt}:CTAG::;"
        retorno = extrair_dados(tn, command_extract)
        logout(tn)
    return retorno


def extrair(host_unm, username, password, host_origem, slot_origem, host_destino, slot_destino, pon_destino):

    # Extrai os dados da OLT origem
    def extrair_origem():
        retorno_origem = conecta_extrai(
            username, password, host_unm, host_origem)
        resultado_origem.put(retorno_origem)

    # Extrai os dados da OLT destino
    def extrair_destino():
        retorno_destino = conecta_extrai(
            username, password, host_unm, host_destino)
        resultado_destino.put(retorno_destino)

    with tqdm(total=70, desc="Extraindo dados GPON", unit="%", dynamic_ncols=True) as barra_progresso:

        # Cria as filas
        resultado_origem = queue.Queue()
        resultado_destino = queue.Queue()

        # Cria as threads pra execução
        thread_origem = Thread(target=extrair_origem)
        thread_destino = Thread(target=extrair_destino)

        # Iniciar as threads
        thread_origem.start()
        thread_destino.start()
        while thread_destino.is_alive() or thread_origem.is_alive():
            barra_progresso.update(1)
            sleep(1)
        else:
            barra_progresso.update(100 - barra_progresso.n)

    # Esperar as threads terminarem
    thread_origem.join()
    thread_destino.join()

    retorno_origem = resultado_origem.get()
    retorno_destino = resultado_destino.get()

    print("Dados GPON extraídos com sucesso!")

    # Processa os dados extraídos
    df_destino = trata_destino(
        retorno_destino, host_destino, slot_destino, pon_destino)
    df_origem = trata_origem(retorno_origem, host_origem, slot_origem)

    print("Dados processados com sucesso!")

    df = pd.merge(df_destino, df_origem, on='MAC', how='left')
    df = df.dropna(subset=['NOVO_NOME'])
    return df
