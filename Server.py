import socket
import threading
import time
from random import randint

clients = {}
groups = {}
HEADER = 64
PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
guest_count = 0

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Decorator para invocar função como thread
def threaded(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper

class Client:

    connected = True
    s = threading.Semaphore(0)

    def __init__(self, conn, addr):
        global guest_count
        self.conn = conn
        self.addr = addr
        guest_count+=1
        self.name = f'guest{guest_count}'
        self.handle_client()
        self.send(self.name, type='name')

    @threaded
    def handle_client(self):
        conn = self.conn
        addr = self.addr
        print(f"[Server] Nova conexão estabelecida com {addr}\nNome: {self.name}\n")
        while self.connected:
            header = conn.recv(HEADER).decode('utf-8').split()
            if not header: continue
            print(f'{self.name}: {header}') #debug
            msg_len = int(header[0])
            type = header[1]
            target = header[2]
            group = header[3]
            if msg_len:
                self.send(type='OK')
                msg = conn.recv(msg_len).decode('utf-8')
                print(f'{self.name}: {msg}') # debug
                if target != 'None':
                    self.send(msg=msg, type=type, target=target, origin=self.name)
                    continue
                if type == 'name':
                    new_name = msg
                    if new_name in clients.keys():
                        self.send("Este nome já existe!")
                        continue
                    clients[new_name] = clients.pop(self.name)
                    self.send(new_name, type='name')
                    print(f"[Server] Usuário {self.name} mudou para {new_name}\n")
                    self.name = new_name
                    continue
                if type == 'accept':
                    self.send(msg, 'accept', target=target, origin=self.name)
                    continue
                if type == 'start_game':
                    self.start_game(msg)
                    continue
                if group != 'None':
                    for client in groups[group]:
                        if client != self.name:
                            self.send(msg, type='group', target=client, origin=self.name)
                    continue
                else:    
                    print(f"{self.name}: {msg}\n")
                    continue
            elif type == 'OK':
                self.s.release()
                continue
            elif type == 'list_clients':
                client_list = ''
                for key in clients.items():
                    client_list += f'{key[0]}: {key[1].addr} '
                self.send(msg=client_list, type='list_clients')
                continue
            elif type == 'game_invite':
                # Cria um grupo com nome 'group_name' e manda o nome para o alvo
                if target == self.name:
                    self.send("Você não pode convidar a sí mesmo!")
                    continue
                groups['group_name'] = [self.name, target]
                self.send(msg='group_name', type='game_invite', target=target, origin=self.name)
                continue
            elif type == 'refuse':
                self.send(type='refuse', target=target, origin=self.name)
                del groups[group]
                continue
            elif type == 'closed_chat':
                for client in groups[group]:
                    if client != self.name:
                        self.send(type='closed_chat', target=client, origin=self.name)
                continue
            elif type == 'disconnect':
                print(f'[Server] {self.name} encerrou conexão!\n')
                self.connected = False
                del clients[self.name]
                conn.close()
                break
            elif target != 'None':
                self.send(type=type, origin=self.name, target=target)

    # Função para envio de mensagems encapsuladas com o cabeçalho
    @threaded
    def send(self, msg=None, type=None, origin=None, target=None):
        client = self.conn
        if target:
            try:
                target_conn = clients[target].conn
            except:
                self.send('Usuário não encontrado!')
                return
        if msg:
            msg = msg.encode('utf-8')
            msg_len = str(len(msg))
        else:
            msg_len = '0'
        header = msg_len + f' {type} {origin}'
        header = header + ' ' * (HEADER - len(header))
        print(f'Enviando: {header.encode("utf-8").split()} alvo: {target} origem: {self.name}') # debug
        if target:
            target_conn.send(header.encode('utf-8'))
        else:
            client.send(header.encode('utf-8'))
        if msg_len != '0':
            print(msg)
            if target:
                # O alvo manda a confirmação para a classe Client dele
                # a qual eu não tenho acesso, logo, fazemos de forma assíncrona
                time.sleep(0.01)
                target_conn.send(msg)
            else:
                self.s.acquire()
                client.send(msg)

    @threaded
    def start_game(self, group):
        x = randint(1,100)
        for client in groups[group]:
            if client != self.name:
                if x > 50:
                    # Manda o nome do oponente junto com a marca pois mandar em origin ou target direcionado a sí interfere na lógica do sistema
                    self.send(msg=f'X {client}', type='start_game')
                    self.send(msg='O', type='start_game', origin=self.name, target=client)
                else:
                    self.send(msg=f'O {client}', type='start_game')
                    self.send(msg='X', type='start_game', origin=self.name, target=client)


def runserver():
    # Define processo como servidor
    server.listen()
    while(True):
        print("[Server] Aguardando conexão...\n")
        conn, addr = server.accept()
        client = Client(conn, addr)
        clients[client.name] = client
        print(f"[Server] Número de conexões: {threading.active_count() - 1}\n")


print("[Server] Servidor inicializando...\n")
runserver()