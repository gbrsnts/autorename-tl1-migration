import configparser
import pandas as pd
from utils.script_extracao import extrair
from utils.script_rename import rename_dataframe
from utils.logs_utils import log_execucao
from time import sleep

# LER ARQUIVO CONFIG.INI
config = configparser.ConfigParser()
config.read('./config/config.ini')

# INFORMAÇÕES DO UNM
USERNAME = config['UNM']['username']
PASSWORD = config['UNM']['password']
HOST_UNM = config['UNM']['host']

# INFORMAÇÕES DA OLT DE ORIGEM
HOST_ORIGEM = config['OLT_ORIGEM']['host']
SLOT_ORIGEM = config['OLT_ORIGEM']['slot']

# INFORMAÇÕES DA OLT DE DESTINO
HOST_DESTINO = config['OLT_DESTINO']['host']
SLOT_DESTINO = config['OLT_DESTINO']['slot']


if __name__ == '__main__':
    # Extracao dos dados
    pon_destino = "0"
    print("Iniciando programa para renomear ONUs...")
    sleep(1.5)
    print("1 - Renomear um SLOT\n2 - Renomar uma PON")
    opcao = int(input("Digite uma opção: "))
    if opcao == 2:
        pon_destino = str(
            input("Qual PON de destino que deseja renomear? "))
    sleep(1.5)
    # df = extrair(HOST_UNM, USERNAME, PASSWORD, HOST_ORIGEM, SLOT_ORIGEM, HOST_DESTINO, SLOT_DESTINO, pon_destino)

    nome_arquivo = f"./files/{HOST_DESTINO}_SLOT_{SLOT_DESTINO}"
    nome_arquivo += ".xlsx" if pon_destino == "0" else f"_PON_{pon_destino}.xlsx"
    # df.to_excel(nome_arquivo, index=False)

    df = pd.read_excel(nome_arquivo)
    # Renomear os clientes com os dados já estraídos
    rename_dataframe(df, HOST_UNM, USERNAME, PASSWORD)
