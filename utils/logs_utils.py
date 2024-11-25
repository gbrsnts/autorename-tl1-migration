from datetime import datetime


def log_execucao(mensagem):
    agora = datetime.now()
    hora_formatada = agora.strftime('%Y-%m-%d %H:%M:%S')
    data_formatada = agora.date().strftime('%Y-%m-%d')
    log_mensagem = f"{data_formatada} {hora_formatada} - {mensagem}\n"
    try:
        with open(f"./logs/error/{data_formatada}.log", 'a', encoding='utf-8') as log:
            log.write(log_mensagem)
    except Exception as e:
        print(f"Erro ao gravar o log: {e}")
