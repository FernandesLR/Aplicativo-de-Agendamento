# importando dependências
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager # importa o gerenciador de telas
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker # interface de agenda
from kivymd.uix.pickers import MDTimePicker # interface de relógio
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from datetime import datetime
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.core.window import Window
import db # importa o banco de dados



Window.size = (500, 920)

def formatar_data(data):
    # Convertendo o formato aa/mm/dd para dd/mm
    data_obj = datetime.strptime(data, '%Y-%m-%d')

    # Formatando a data no formato brasileiro
    data_formatada = data_obj.strftime('%d/%m')

    return data_formatada




class GerenciadorTelas(ScreenManager): # Serve para indicar a ordem de carregamento de telas
    pass

class PrimeiraTela(Screen): # vai ser a tela de login
    def __init__(self, **kw):
        super().__init__(**kw)
        self.IdUsuario = '' # variáveis com self. são atributos da classe
        self.msg = None
        
    def login(self):
        # pega os textos das caixinhas que são o email e a senha
        email = str(self.ids.email.text).strip() # .strip serve para ignorar os espaços
        senha = self.ids.senha.text

        if email == '' or senha == '': # se o email ou a senha estiverem vazias retorna erro
            self.mostrarAviso('Os campos de Email e Senha devem estar preenchidos!')
            return
        
        idUsuario = db.verificarLogin(email, senha) # faz uma consulta no banco de dados

        if idUsuario: # verifica se tem algo dentro da variável e executa o comando abaixo caso seja verdadeiro
            self.ids.email.line_color_normal = [0, 1, 0, 1] # verde
            self.ids.senha.line_color_normal = [0, 1, 0, 1] # verde
            
            # abaixo o atributo da classe recebe o valor da variável
            self.IdUsuario = idUsuario
            self.manager.get_screen('Agendamento').idUsuario = idUsuario # passa o valor da variável id para o atributo da segunda tela
            self.manager.current = 'Agendamento' # troca para a segunda tela
            

        else:
            self.mostrarAviso('Email ou Senha inválido!') # se a condição do if for falsa retorna mensagem de erro

    def mostrarAviso(self, msg):
            self.aviso = MDDialog(
            title="Aviso",
            text= msg,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.fecharAviso
                ),
            ],
            )
            self.aviso.open()

    def mostrarSenha(self):
        if self.ids.senha.password: # verifica se a senha já está oculta
            self.ids.senha.password = False # torna a senha visivel
            self.ids.senha.icon_right = "eye" # troca o icone 
        else:
            self.ids.senha.password = True # oculta a senha
            self.ids.senha.icon_right = "eye-off"

    def fecharAviso(self, *args): # função que ativada assim que o usuário aperta Ok
        if self.aviso:
            self.aviso.dismiss() # fecha o aviso
            self.aviso = None
        

    def cadastrar(self):
        email = self.ids.email.text
        senha = self.ids.senha.text
        if email == '' or senha == '':
            self.mostrarAviso('Os campos de Email e Senha devem estar preenchidos!')
            return

        self.IdUsuario = db.cadastrarUsuario(email, senha)

        if not self.IdUsuario:
            self.mostrarAviso('Essa conta já foi cadastrada')
            return
        elif self.IdUsuario:
            self.mostrarAviso('Conta criada com sucesso!')
            return
        
        


class SegundaTela(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = ""
        self.hora = ""
        self.evento = ""
        self.IdAgenda = ''
        self.idUsuario = ''
        self.data_tables = None
        self.listaID = []

    def on_enter(self, *args):
        if self.data_tables:
            self.remove_widget(self.data_tables)
        primeira_tela = self.manager.get_screen('login') # acessa as funcionalidades da primeira classe
        self.idUsuario = primeira_tela.IdUsuario # pega o id do usuario que estava na tela de login
        self.tabela() # abre a tabela

    def calendario(self):
        #Abrindo o calendário...
        # essa função é ativada assim que o usuário clica no botão "meu calendario"
        calendario = MDDatePicker()
        calendario.bind(on_save=self.pegarDia) # chama a função responsável por pegar a data escolhida pelo usuário
        calendario.open() # abre o calendario na interface
        

    def pegarDia(self, instance, value, date_range):
        # Função é disparada quando usuario já escolheu a data e clicou em OK
        # Serve para pegar o valor da data escolhida pelo usuário
        self.data = value
        relogio = MDTimePicker()
        relogio.bind(on_save=self.pegarHora) # chama a função responsável por pegar o valor da hora
        relogio.open() # abre o relógio na interface

    def pegarHora(self, instance, value):
        self.hora = value # self.hora recebe valor da hora
        instance.dismiss()  # Fechar o MDTimePicker
        self.pegarEvento()

    def pegarEvento(self):
        self.aviso = MDDialog(
        title="Compromisso para o dia marcado",
        type="custom",
        content_cls=MDTextField(),
        buttons=[
            MDFlatButton(
                text="Cancelar", on_release=self.fecharAviso
            ),
            MDFlatButton(
                text="Continuar", on_release=self.pegarTxt
            ),
        ],
        )
        self.aviso.open() # adiciona na tela esse aviso


    def registrar(self):
        # Essa função é executada quando o usuário termina os processos de: marcar data, hora e fazer a descrição do evento
        # Serve para registrar os dados no banco de dados
        if self.data and self.hora: # verifica se tem alguma coisa dentro dessas variáveis
            data = f"{self.data} "+ f"{self.hora}" # concatena duas variáveis para guardar no atributo de classe datetime no banco
            
            self.IdAgenda = db.registrarData(data, self.evento, self.idUsuario) # Esse atributo recebe o id que é retornado pela função db.registrarData()
            
            self.addDados(self.data, self.hora, self.evento) # adiciona esses dados cadastrados a interface

    def tabela(self):
        # Configurando a tabela de dados
        self.data_tables = MDDataTable(
            size_hint=(1, 0.81),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            elevation=2,
            check = True,
            rows_num = 20,
            column_data=[
                ("ID", dp(30)),
                ("Data", dp(36)),
                ("Hora", dp(36)),
                ("Evento", dp(34)),
            ]
        )
        self.ids.table_container.add_widget(self.data_tables) # adiciona esse componente na tela
        self.data_tables.bind(on_check_press=self.pegarIDtable) # adiciona uma função que dispara toda vez quem uma linha é selecionada
        self.retornarDados() # tenta retornar os dados do banco de dados caso essa pessoa tenha algum registro

    
    def pegarIDtable(self, instance, row):
        if row != self.listaID:
            self.listaID = row # guarda os ids selecionados
        else:
            self.listaID = ''
            
        
        
    def addDados(self, valorData="Não informado", valorHora="Não informado", valorEvento="Não informado"):
        self.diaHora = str(valorData) + ' ' + str(valorHora)
        
        valorData = formatar_data(str(valorData))
        self.data_tables.add_row([f"{self.IdAgenda}",f"{valorData}", f"{valorHora}", f"{valorEvento}"])
        
            

    def excluirDados(self):

        if len(self.listaID) > 0 and self.listaID != '': # executa se o número de linhas selecionada da tabela for maior que 1
            for dado in self.data_tables.row_data:
                if dado == self.listaID:
                    self.data_tables.remove_row(dado)
                    self.listaID = ''
            
        else:
            self.aviso = MDDialog(
            title="Aviso",
            text="É necessário selecionar pelo menos uma linha para excluir.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.fecharAviso
                ),
            ],
            )
            self.aviso.open()

    def fecharAviso(self, *args):
        if self.aviso:
            self.aviso.dismiss()
            self.aviso = None

    def pegarTxt(self, *args): # pega o texto do aviso
        self.evento = self.aviso.content_cls.text
        self.aviso.dismiss()
        self.aviso = None
        self.registrar() # chama a função registrar
        

    def retornarDados(self):
        dados = db.retornarData(self.idUsuario)
        
        if dados: # se tiver algo dentro de dados
            for dado in dados:
                self.IdAgenda = dado[0] # atribui o id ao self.Idagenda
                diahora = str(dado[1]).split(' ') # pega o dia e hora

                # self.diaHora faz parte da função de notificação
                #self.diaHora = diahora[0] +' ' + diahora[1]
                #self.diaHora = self.diaHora[-10]
                
                self.addDados(diahora[0], diahora[1], dado[2])
        else:
            print('essa pessoa não possui dados')

    def sair(self):
        self.stop()



class MeuApp(MDApp):
    def build(self): # função construtora do app que vai renderizar a tela
        self.theme_cls.primary_palette = "Pink"
        Builder.load_file('login.kv')
        Builder.load_file('agendamento.kv') # importa o arquivo de estilização

        return GerenciadorTelas() # retorna o objeto gerenciador de telas
    def sair(self):
        self.stop()

    
    

MeuApp().run() # executa o código