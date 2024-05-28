# importando dependências
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager # importa o grenciador de telas
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker # interface de agenda
from kivymd.uix.pickers import MDTimePicker
from kivy.core.window import Window
from kivy.uix.label import Label # apagar depois
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from datetime import datetime
from kivymd.uix.dialog import MDDialog
import db # importa o banco de dados


def formatar_data(data):
    # Convertendo a string de data para um objeto datetime
    data_obj = datetime.strptime(data, '%Y-%m-%d')

    # Formatando a data no formato brasileiro
    data_formatada = data_obj.strftime('%d/%m')

    return data_formatada

Window.size = (490, 900) # tamanho minimo de tela
class GerenciadorTelas(ScreenManager):
    pass

class PrimeiraTela(Screen): # vai ser a tela de login
    def __init__(self, **kw):
        super().__init__(**kw)
        self.IdUsuario = ''
 
        
    def login(self):
        # pega os textos das caixinhas que são o email e a senha
        email = self.ids.email.text
        senha = self.ids.senha.text
        idUsuario = db.verificarLogin(email, senha)

        if idUsuario: # passa para uma função externa que vai tratar os dados
            self.ids.email.line_color_normal = (0, 1, 0, 1) # verde
            self.ids.senha.line_color_normal = (0, 1, 0, 1) # verde
            self.manager.current = 'Agendamento'
            self.IdUsuario = idUsuario
            self.manager.get_screen('Agendamento').idUsuario = idUsuario
            self.manager.current = 'Agendamento'
            

        else:
            self.ids.email.line_color_normal = (1, 0, 0, 1)  # Vermelho
            self.ids.senha.line_color_normal = (1, 0, 0, 1)  # Vermelho
            msgDeErro = Label(text="Email ou Senha inválidos!", color=[1, 0, 0, 1])
            self.add_widget(msgDeErro)
        

    def cadastrar(self):
        email = self.ids.email.text
        senha = self.ids.senha.text
        self.IdUsuario = db.cadastrarUsuario(email, senha)
        self.login()
        
        


class SegundaTela(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = ""
        self.hora = ""
        self.evento = ""
        self.IdAgenda = ''
        self.idUsuario = ''
        self.tabela()
        
    def on_enter(self):
        self.retornarDados()

    def calendario(self):
        print("Abrindo o calendário...")
        calendario = MDDatePicker()
        calendario.bind(on_save=self.pegarDia)
        calendario.open()
        

    def pegarDia(self, instance, value, date_range):
        self.data = value
        
        relogio = MDTimePicker()
        relogio.bind(on_save=self.pegarHora)
        relogio.open()

    def pegarHora(self, instance, value):
        self.hora = value
        instance.dismiss()  # Fechar o MDTimePicker
        self.pegarEvento()

    def pegarEvento(self):
        self.evento = self.ids.evento.text
        if self.evento == '':
            self.ids.card.opacity = 1 
        else:
            self.ids.card.opacity = 0
            self.registrar()


    def registrar(self):
        if self.data and self.hora:
            data = f"{self.data} "+ f"{self.hora}"
            self.ids.evento.text = '' # remove o texto do input
            self.IdAgenda = db.registrarData(data, self.evento, self.idUsuario)
            self.addDados(self.data, self.hora, self.evento)

        else:
            print("Data ou hora não foram selecionadas.")

    def tabela(self):
        # Configurando a tabela de dados
        self.data_tables = MDDataTable(
            size_hint=(0.9, 0.6),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            check = True,
            column_data=[
                ("ID", dp(15)),
                ("Data", dp(25)),
                ("Hora", dp(18)),
                ("Evento", dp(20)),
            ]
        )
        self.add_widget(self.data_tables)

    

    def addDados(self, valorData="Não informado", valorHora="Não informado", valorEvento="Não informado"):
        
        valorData = formatar_data(str(valorData))
        
        self.data_tables.add_row([f"{self.IdAgenda}",f"{valorData}", f"{valorHora}", f"{valorEvento}"])
        
        

    def excluirDados(self): # essa função esta com bug preciso arrumar a forma em que pego os ids selecionados da lista
        selected_rows = self.data_tables.get_row_checks() 
        if selected_rows:
            selected_rows.sort(reverse=True)
            for row_index in selected_rows:
                antigoID = row_index[0][0]
                self.data_tables.remove_row(row_index)
                print(antigoID)
                db.excluirData(antigoID)
            
        else:
            print("Nenhuma linha selecionada para exclusão.")

    def retornarDados(self):
        dados = db.retornarData(self.idUsuario)
        if dados:
            for dado in dados:
                self.IdAgenda = dado[0]
                diahora = str(dado[1]).split(' ')
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
    

# Testes

#email = 'pedrinho123@gmail.com'
#senha = '2412@'

# FernandoPedro@Hotmail.com  54451

MeuApp().run() # executa o código