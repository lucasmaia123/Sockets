import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from copy import deepcopy
from numpy import array
import socket
import threading
import time

# Define endereço e tamanho do cabeçalho
HEADER = 64
PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
s = threading.Semaphore(0)
group = None
name = None
game = None

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
connected_server = True

# Decorator para invocar função como thread
def threaded(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper

class Game(tk.Toplevel):

    global name, game
    tab = None
    window = None

    def __init__(self, master, chat_id):
        menu.screen.insert(tk.END, 'Jogo iniciado!')
        super().__init__(master)
        self.geometry('400x600')

        self.game_screen = tk.Canvas(self, height=600, width=200)
        self.game_screen.pack(side='left')

        self.chat_frame = tk.Frame(self, height=600, width=200)
        self.chat_frame.pack(side='right')

        self.id = chat_id
        self.protocol('WM_DELETE_WINDOW', self.window_closed)

        tk.Label(self.chat_frame, text=f'Usuário: {name}').pack(side='top')

        self.chat_view = ScrolledText(self.chat_frame, wrap=tk.WORD, height=20, width=50, state='disabled')
        self.chat_view.pack(padx=10, pady=5)

        self.chat_label = tk.Label(self.chat_frame, text='Chat:')
        self.chat_label.pack(padx=10, pady=5, side='left')

        self.entry = tk.Entry(self.chat_frame, width=50)
        self.entry.pack(padx=10, pady=5, side='right')

        self.game_screen.create_line(50, 0, 50, 150, width=3)
        self.game_screen.create_line(100, 0, 100, 150, width=3)
        self.game_screen.create_line(0, 50, 150, 50, width=3)
        self.game_screen.create_line(0, 100, 150, 100, width=3)

        self.game_screen.create_line(50, 200, 50, 350, width=3)
        self.game_screen.create_line(100, 200, 100, 350, width=3)
        self.game_screen.create_line(0, 250, 150, 250, width=3)
        self.game_screen.create_line(0, 300, 150, 300, width=3)

        self.game_screen.create_line(50, 400, 50, 550, width=3)
        self.game_screen.create_line(100, 400, 100, 550, width=3)
        self.game_screen.create_line(0, 450, 150, 450, width=3)
        self.game_screen.create_line(0, 500, 150, 500, width=3)

        self.label = tk.Label(self, text="Text area!", font=("Arial", 10))
        self.label.place(x=50, y=550)

        self.button = tk.Button(self, text='Desistir', command=self.desistir)
        self.button.place(x=300, y=550)

        self.bind('<Button-1>', self.get_mouse)
        self.entry.bind('<Return>', self.input_entry)
        self.focus()

    def game_start(self, mark, oponent):
        self.mark = mark
        self.oponent = oponent
        self.tab = self.gera_tabuleiro()
        self.over = False

        if self.mark == 'X':
            self.turn = True
            self.label['text'] = 'Você começa!'
        elif self.mark == 'O':
            self.turn = False
            self.label['text'] = 'Oponente começa!'
        
    def gera_tabuleiro(self):
        return [[[None, None, None] for i in range(3)] for j in range(3)]

    def draw(self, tab, p1, p2, oponent = False):
        dis_x = p1 * 50
        dis_y = p2 * 50 + tab * 200
        if (self.mark == 'X' and not oponent) or (self.mark == 'O' and oponent):
            self.game_screen.create_line(dis_x+5, dis_y+5, dis_x+45, dis_y+45, width=3, tags="game")
            self.game_screen.create_line(dis_x+45, dis_y+5, dis_x+5, dis_y+45, width=3, tags="game")
        elif (self.mark == 'O' and not oponent) or (self.mark == 'X' and oponent):
            self.game_screen.create_oval(dis_x+5, dis_y+5, dis_x+45, dis_y+45, width=3, tags="game")

    def pos_livres(self):
        return [[k,i,j] for k in range(3) for i in range(3) for j in range(3) if self.tab[k][i][j] == None]

    def pos_mark(self):
        return [[k,i,j] for k in range(3) for i in range(3) for j in range(3) if self.tab[k][i][j] != None]

    def tab_cheio(self):
        for k in range(3):
            for i in range(3):
                for j in range(3):
                    if self.tab[k][i][j] == None:
                        return False
        return True

    def avalia(self):
        visitados = []
        for pos in self.pos_mark():
            atual = [pos[0], pos[1], pos[2]]
            mark = self.tab[pos[0]][pos[1]][pos[2]]
            visitados.append(atual)
            vizinhos = self.neighbors(atual, visitados)
            # Analisa os elementos vizinhos e checa se eles formam uma reta
            for v in vizinhos:
                if self.tab[v[0]][v[1]][v[2]] == mark:
                    passo = array(v) - array(atual)
                    next = array(v) + array(passo)
                    print(f'atual: {atual}, v: {v}, next: {next}, mark: {mark}')
                    try:
                        if self.tab[next[0]][next[1]][next[2]] == mark:
                            if mark == 'X':
                                return 1
                            elif mark == 'O':
                                return -1
                    except:
                        pass
        return 0

    # Algoritimo para criar uma lista de possiveis vetores de n dimenções com tamanho definido 
    # Exemplo: (1, 0, 0) <- primeiro vetor de 3 dimenções com tamanho 1
    def permutations(self, val, size):
        aux = []
        perms = []
        for i in range(size):
            aux.append(0)
        perms.append(aux)
        for i in range(size):
            for k in range(len(perms)):
                aux = self.permute(val, perms[k])
                for j in aux:
                    if j not in perms:
                        perms.append(j)
        perms.pop(0)
        return perms

    # Gera novos vetores baseado em um vetor inicial ao adicionar o vetor de possíveis permutações vetoriais
    # Usado como auxiliar para o algoritimo acima
    def permute(self, val, lista):
        perms = []
        # Insere o tamanho do vetor normal e invertido em cada dimenção do vetor para gerar novos vetores
        for i in range(len(lista)):
            if lista[i] != val:
                lista[i] = val
                perms.append(deepcopy(lista))
                lista[i] = val * -1
                perms.append(deepcopy(lista))
                lista[i] = 0
        return perms
        
    # Pega os possiveis elementos vizinhos de um espaço no tabuleiro
    def neighbors(self, pos, visitados):
        n = []
        moves = self.permutations(1, 3) # Utiliza vetores de tamanho 1 para encontrar elementos vizinhos
        for move in moves:
            n_pos = array(pos) + array(move)
            if list(n_pos) not in visitados and (n_pos >= 0).all() and (n_pos < 3).all():
                n.append(n_pos)
        return n

    def fim(self):
        if self.avalia() == 1:
            if self.mark == 'X':
                self.label['text'] = 'Você venceu!'
            else:
                self.label['text'] = 'Você perdeu!'
            return True
        if self.avalia() == -1:
            if self.mark == 'O':
                self.label['text'] = 'Você venceu!'
            else:
                self.label['text'] = 'Você perdeu!'
            return True
        if self.tab_cheio():
            self.label['text'] = 'Empate!'
            return True
        return False

    def desistir(self, oponent = False):
        if not self.over:
            if not oponent:
                send(type='forfeit', target=self.oponent)
                self.over = True
                self.label['text'] = 'Você perdeu!'
                self.button.config(text='Rematch', command=self.send_rematch)
            else:
                self.over = True
                self.label['text'] = 'Oponente desistiu!'
                self.button.config(text='Rematch', command=self.send_rematch)

    def get_mouse(self, event):
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        print(x, y) # debug
        if not self.over and self.turn:
            for pos in self.pos_livres():
                if x > pos[1] * 50 and x < (pos[1] + 1) * 50:
                    if y > (pos[0] * 200) + pos[2] * 50 and y < (pos[0] * 200) + (pos[2] + 1) * 50:
                        self.draw(pos[0], pos[1], pos[2])
                        self.tab[pos[0]][pos[1]][pos[2]] = self.mark
                        send(msg=str([pos[0], pos[1], pos[2]]), type='game', target=self.oponent)
                        self.over = self.fim()
                        if not self.over:
                            self.label['text'] = 'Vez do oponente!'
                            self.turn = False
                        else:
                            self.button.config(text='Rematch', command=self.send_rematch)
                        break

    def oponent_play(self, pos):
        pos = eval(pos)
        self.draw(pos[0], pos[1], pos[2], oponent=True)
        if self.mark == 'X':
            self.tab[pos[0]][pos[1]][pos[2]] = 'O'
        else:
            self.tab[pos[0]][pos[1]][pos[2]] = 'X'
        self.over = self.fim()
        if not self.over:
            self.label['text'] = 'Sua vez!'
            self.turn = True
        else:
            self.button.config(text='Rematch', command=self.send_rematch)

    def send_rematch(self):
        send(type='rematch', target=self.oponent)

    def rematch(self):
        if self.window:
            self.window.destroy()
        self.window = tk.Toplevel(self.master)
        self.window.geometry('200x100')
        tk.Label(self.window, text=f'{self.oponent} está requisitando um novo jogo!').pack()
        tk.Button(self.window, text='Aceitar', command=lambda: self.restart(oponent=False)).pack(side='left', padx=10)
        tk.Button(self.window, text='Recusar', command=self.refuse).pack(side='right', padx=10)
        self.window.focus()
        self.window.lift()

    def refuse(self):
        send(type='refuse_rematch', target=self.oponent)
        self.window.destroy()
        self.window_closed()

    def restart(self, oponent=False):
        if self.window:
            self.window.destroy()
        if not oponent:
            send(type='restart', target=self.oponent)
        self.tab = self.gera_tabuleiro()
        self.game_screen.delete('game')
        self.over = False
        self.button.config(text='Desistir', command=self.desistir)
        if self.mark == 'X':
            self.turn = True
            self.label['text'] = 'Você começa!'
        elif self.mark == 'O':
            self.turn = False
            self.label['text'] = 'Oponente começa!'

    def input_entry(self, event):
        msg = self.entry.get()
        self.entry.delete(0, tk.END)
        if msg:
            send(msg, group=self.id)
            self.chat_view.configure(state='normal')
            self.chat_view.insert(tk.INSERT, f'\n{name}: {msg}')
            self.chat_view.see('end')
            self.chat_view.configure(state='disabled')

    def window_closed(self):
        send(type='closed_chat', group=self.id)
        game = None
        self.destroy()

class Main_menu(tk.Frame):

    window_open = False

    def __init__(self, master):
        global name
        super().__init__(master)
        self.pack(side='top')
        self.master = master

        tk.Label(self, text="Chat TicTacToe-3D", height=10, width=50).pack()

        self.welcome = tk.Label(self, text='')
        self.welcome.pack(padx=10, pady=10)

        self.screen = tk.Text(self, width=50, height=10, state='disabled')
        self.screen.pack(padx=10, pady=10)

        self.buttons = [None, None, None, None]
        self.buttons[0] = tk.Button(self, text='Iniciar jogo', command=self.game_start)
        self.buttons[0].pack(padx=10)

        self.buttons[1] = tk.Button(self, text='Listar usuários', command=self.list_users)
        self.buttons[1].pack(padx=10)

        self.buttons[2] = tk.Button(self, text='Mudar nome', command=self.new_name)
        self.buttons[2].pack(padx=10)

        self.buttons[3] = tk.Button(self, text='Sair', command=self.disconnect)
        self.buttons[3].pack(padx=10)

    def insert(self, text):
        self.screen.configure(state='normal')
        self.screen.insert(tk.END, text + '\n')
        self.screen.configure(state='disabled')

    def clear_screen(self):
        self.screen.configure(state='normal')
        self.screen.delete('1.0', tk.END)
        self.screen.configure(state='disabled')

    def list_users(self):
        send(type='list_clients')

    def new_name(self):
        if not self.window_open:
            self.window_open = True
            self.window = tk.Toplevel(self.master)
            self.window.protocol('WM_DELETE_WINDOW', self.window_closed)
            self.window.title('Change name')
            self.window.geometry('200x50')

            tk.Label(self.window, text='Digite o seu novo nome', width=100).pack(side='top')
            entry = tk.Entry(self.window, width=50)
            entry.pack(side='top')
            entry.focus()
            entry.bind('<Return>', lambda event: self.change_name(event, entry.get()))

    def change_name(self, event, new_name):
        if new_name:
            send(new_name, type='name')
            self.insert(f'\nSeu novo nome é {new_name}')
            self.window_closed()

    def game_start(self):
        if not self.window_open:
            self.window_open = True
            self.window = tk.Toplevel(self.master)
            self.window.protocol('WM_DELETE_WINDOW', self.window_closed)
            self.window.title('Chat interface')
            self.window.geometry('250x100')

            tk.Label(self.window, text='Digite o nome do usuário a convidar', width=150).pack(padx=10, side='top')

            entry = tk.Entry(self.window, width=60)
            entry.pack(padx=10, side='top')
            entry.focus()
            entry.bind('<Return>', lambda event: self.game_invite(event, entry.get()))

    def accept(self, target):
        # Manda confirmação para a origem do convite com o nome do grupo
        global group, game
        send(msg=group, type='accept', target=target)
        game = Game(self.master, group)
        self.popup.destroy()

    def refuse(self, target):
        # Manda mensagem de recusa para a origem do convite
        global group
        send(type='refuse', target=target, group=group)
        group = None
        self.popup.destroy()

    def game_invite(self, event, target):
        # Manda convite para o alvo
        send(type='game_invite', target=target)
        self.window_closed()
        self.clear_screen()
        self.insert('Aguardando resposta...\n')
        
    def receive_answer(self, target):
        global game
        if group:
            self.insert('Iniciando chat box...\n')
            game = Game(self.master, group)
            time.sleep(0.01)
            send(msg=group, type='start_game')
        else:
            self.insert(f'{target} recusou iniciar um chat com você!')
            return

    def receive_invite(self, origin, group_name):
        global group
        group = group_name
        self.popup = tk.Toplevel(root)
        self.popup.title('Chat invite')
        self.popup.geometry('250x100')
        tk.Label(self.popup, text=f'{origin} está o convidando para um jogo!').pack(side='top', padx=10)
        tk.Button(self.popup, text='Aceitar', command=lambda: self.accept(origin)).pack(side='left', padx=20, pady=10)
        tk.Button(self.popup, text='Recusar', command=lambda: self.refuse(origin)).pack(side='right', padx=20, pady=10)
        self.popup.focus()
        self.popup.lift()

    def window_closed(self):
        self.window.destroy()
        self.window_open = False

    def disconnect(self):
        send(type='disconnect')
        self.master.destroy()


# Thread responsável por receber mensagems do servidor
@threaded
def listen2server():
    global group, name, game
    while connected_server:
        header = client.recv(HEADER).decode('utf-8').split()
        if not header: continue
        msg_len = int(header[0])
        type = header[1]
        origin = header[2]
        if type == "OK":
            s.release()
            continue
        if type == 'refuse':
            group = None
            menu.receive_answer(origin)
            continue
        if type == 'rematch':
            if game:
                game.rematch()
            else:
                send(type='refuse_rematch', target=origin)
        if type == 'refuse_rematch':
            game.window_closed()
            menu.insert(f'{origin} recusou seu convite!')
            continue
        if type == 'closed_chat':
            menu.insert(f'{origin} encerrou a conexão')
            game.destroy()
            continue
        if type == 'restart':
            game.restart(oponent=True)
            continue
        if type == 'forfeit':
            game.desistir(oponent=True)
            continue
        if msg_len:
            # Checa se mensagem veio do socket local
            if origin == 'None':
                time.sleep(0.01)
                send(type='OK')
            msg = client.recv(msg_len).decode('utf-8')
            if type == 'list_clients':
                menu.clear_screen()
                for user in msg.split():
                    menu.insert(user)
            elif type == 'name':
                name = msg
                menu.welcome.configure(text=f'Bem vindo {name}')
            elif type == 'game_invite':
                menu.receive_invite(origin, msg)
            elif type == 'accept':
                group = msg
                menu.receive_answer(origin)
                continue
            elif type == 'start_game':
                if origin != 'None':
                    game.game_start(msg, oponent=origin)
                else:
                    msg = msg.split()
                    game.game_start(msg[0], oponent=msg[1])
            elif type == 'game':
                game.oponent_play(msg)
            elif type == 'group':
                # print in group chat window
                game.chat_view.configure(state='normal')
                game.chat_view.insert(tk.INSERT, f'\n{origin}: {msg}')
                game.chat_view.see('end')
                game.chat_view.configure(state='disabled')
            else:
                menu.clear_screen()
                menu.insert(msg)

# Função para enviar mensagems encapsuladas com o cabeçalho
@threaded
def send(msg=None, type=None, target=None, group=None):
    if msg:
        msg = msg.encode('utf-8')
        msg_len = str(len(msg))
    else:
        msg_len = '0'
    header = msg_len + f' {type} {target} {group}'
    header = header + ' ' * (HEADER - len(header))
    client.send(header.encode('utf-8'))
    if msg_len != '0':
        s.acquire()
        client.send(msg)


print("[Client] Conectado ao servidor!")
root = tk.Tk()
menu = Main_menu(root)
listen2server()
menu.welcome.configure(text=f'Bem vindo {name}')
root.mainloop()