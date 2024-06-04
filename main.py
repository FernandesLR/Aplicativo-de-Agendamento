# importando dependências
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager # importa o gerenciador de telas
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker # interface de agenda
from kivymd.uix.pickers import MDTimePicker # interface de relógio
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from datetime import datetime # apagar caso não tenha marcardor
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
import db # importa o banco de dados

#from plyer import notification

#from jnius import autoclass


def formatar_data(data):
    # Convertendo a string de data para um objeto datetime
    data_obj = datetime.strptime(data, '%Y-%m-%d')

    # Formatando a data no formato brasileiro
    data_formatada = data_obj.strftime('%d/%m')

    return data_formatada




class GerenciadorTelas(ScreenManager):
    pass

# FernandoPedro@Hotmail.com 54451

class PrimeiraTela(Screen): # vai ser a tela de login
    def __init__(self, **kw):
        super().__init__(**kw)
        self.IdUsuario = ''
        self.msg = None
        
    def login(self):
        # pega os textos das caixinhas que são o email e a senha
        email = str(self.ids.email.text).strip()
        senha = self.ids.senha.text
        if email == '' or senha == '':
            self.mostrarAviso('Os campos de Email e Senha devem estar preenchidos!')
            return
        idUsuario = db.verificarLogin(email, senha)
        
        self.manager.current = 'Agendamento'

        if idUsuario: # passa para uma função externa que vai tratar os dados
            self.ids.email.line_color_normal = [0, 1, 0, 1] # verde
            self.ids.senha.line_color_normal = [0, 1, 0, 1] # verde
            
            self.IdUsuario = idUsuario
            self.manager.get_screen('Agendamento').idUsuario = idUsuario
            

        else:
            self.mostrarAviso('Email ou Senha inválido!')

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

    def fecharAviso(self, *args):
        if self.aviso:
            self.aviso.dismiss()
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
        primeira_tela = self.manager.get_screen('login')  # Substitua 'nome_da_primeira_tela' pelo nome da sua PrimeiraTela
        self.idUsuario = primeira_tela.IdUsuario
        self.tabela()

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
        if self.data and self.hora: # verifica se tem alguma coisa dentro dessas variáveis

            data = f"{self.data} "+ f"{self.hora}" # concatena duas variáveis para guardar no banco

            # self.IdAgenda recebe o id desse novo registro que é retornado dessa função db.registrarData
            self.IdAgenda = db.registrarData(data, self.evento, self.idUsuario) 
            
            self.addDados(self.data, self.hora, self.evento) # adiciona esses dados cadastrados a interface

        else:
            print("Data ou hora não foram selecionadas.")

    def tabela(self):
        # Configurando a tabela de dados
        self.data_tables = MDDataTable(
            size_hint=(1, 0.81),
            pos_hint={"center_x": 0.5, "center_y": 0.48},
            check = True,
            rows_num = 20,
            column_data=[
                ("ID", dp(30)),
                ("Data", dp(36)),
                ("Hora", dp(36)),
                ("Evento", dp(34)),
            ]
        )
        self.add_widget(self.data_tables) # adiciona esse componente na tela
        self.data_tables.bind(on_check_press=self.pegarIDtable) # adiciona uma função que dispara toda vez quem uma linha é selecionada
        self.retornarDados() # tenta retornar os dados do banco de dados caso essa pessoa tenha algum registro


    
    def pegarIDtable(self, instance, row):
        self.id = row
        
        
    def addDados(self, valorData="Não informado", valorHora="Não informado", valorEvento="Não informado"):
        self.diaHora = str(valorData) + ' ' + str(valorHora)
        self.diaHora = self.diaHora[:-3]
        
        valorData = formatar_data(str(valorData))
        self.data_tables.add_row([f"{self.IdAgenda}",f"{valorData}", f"{valorHora}", f"{valorEvento}"])

        # Lógica dos marcadores (destacar eventos concluídos)
        
            

    def excluirDados(self):
        c = 0
        if len(self.data_tables.row_data) > 1:
            for dado in self.data_tables.row_data:
                if dado == self.id:
                    self.data_tables.remove_row(self.data_tables.row_data[c])
                    db.excluirData(dado[0])
                c += 1

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

    def pegarTxt(self, *args):
        self.evento = self.aviso.content_cls.text
        self.aviso.dismiss()
        self.aviso = None
        self.registrar()
        

    def retornarDados(self):
        dados = db.retornarData(self.idUsuario)
        
        if dados:
            for dado in dados:
                self.IdAgenda = dado[0]
                diahora = str(dado[1]).split(' ')
                self.diaHora = diahora[0] +' ' + diahora[1]
                self.diaHora = self.diaHora[-10]
                
                self.addDados(diahora[0], diahora[1], dado[2])
        else:
            print('essa pessoa não possui dados')
    
    #def dispararNotificacao(self, titulo, msg):
        #try:
            #notification.notify(
     #           title= titulo,
      #          message= msg,
        #        app_name= 'Agendamento'
       #     )
       # except ValueError as e:
          #  print(e)
        #finally:
         #   pass

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