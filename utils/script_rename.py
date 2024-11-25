from time import sleep, time
from utils.telnet_utils import send_command, login, logout, telnet_session
from utils.logs_utils import log_execucao
from tqdm import tqdm


def rename_dataframe(dataframe, unm_ip, username, password):
    with telnet_session(unm_ip, 3337) as tn:
        login(tn, username, password)
        inicio = time()
        barra_progresso = tqdm(dataframe.iterrows(
        ), desc="Renomeando ONUs", unit="%", total=len(dataframe), dynamic_ncols=True, leave=False)
        try:
            for index, row in barra_progresso:
                if '.' in row.NOVO_NOME or ',' in row.NOVO_NOME:
                    row.NOVO_NOME = row.NOVO_NOME.replace(
                        '.', '').replace(',', '')
                command_rename = f"CFG-ONUNAMEANDDESC::OLTID={row.OLTID},PONID=NA-NA-{row.SLOT}-{row.PON},ONUIDTYPE=ONU_NUMBER,ONUID={row.ONU_ID}:CTAG::ONUNAME={row.NOVO_NOME};"
                alerta = send_command(tn, command_rename)
                if 'No error' not in alerta:
                    log_execucao(alerta)
        finally:
            tempo = time() - inicio
            media = 100/tempo
            barra_progresso.clear()
            minutos, segundos_restantes = divmod(int(tempo), 60)
            tempo = f"{minutos:02}:{segundos_restantes:02}"
            print(f"Renomeando ONUs: 100% [{tempo},  {media:.2f}%/s]")
        logout(tn)
