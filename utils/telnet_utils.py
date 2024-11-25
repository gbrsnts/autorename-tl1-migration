import telnetlib
from time import sleep


def telnet_session(host, port):
    return telnetlib.Telnet(host, port)


def login(tn, username, password):
    command_login = f'LOGIN:::CTAG::UN={username},PWD={password};'
    tn.write(command_login.encode('ascii') + b"\n")


def logout(tn):
    command_logout = f'LOGOUT:::CTAG::;'
    tn.write(command_logout.encode('ascii') + b"\n")


def send_command(tn, command):
    tn.write(command.encode('ascii') + b"\n")
    response = tn.read_until(b";")
    response_str = str(response)
    inicio = response_str.find('ENDESC=')
    alerta = response_str[inicio+6:-6]
    return alerta


def extrair_dados(tn, command, timeout=90):
    tn.write(command.encode('ascii') + b"\n")
    response = b""
    contador_final = 0
    tn.sock.settimeout(timeout)

    while contador_final < 2:
        chunk = tn.read_very_eager()
        if chunk:
            response += chunk
            contador_final += chunk.decode('utf-8', errors='ignore').count(";")
        else:
            sleep(1)

    return response.decode('utf-8', errors='ignore')
