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
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
import db # importa o banco de dados


"""
    Falta criar:
    - Criar um trigger que mande notificação para o celular do usuario
    - Criar um marcador para indicar quando um compromisso já passou
    -- Se possivel: Refatorar para deixa-lo mais performatico
    - excluir window.size
    - passar para android
"""

def formatar_data(data):
    # Convertendo a string de data para um objeto datetime
    data_obj = datetime.strptime(data, '%Y-%m-%d')

    # Formatando a data no formato brasileiro
    data_formatada = data_obj.strftime('%d/%m')

    return data_formatada

Window.size = (500, 900) # tamanho minimo de tela


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
        

        if idUsuario: # passa para uma função externa que vai tratar os dados
            self.ids.email.line_color_normal = (0, 1, 0, 1) # verde
            self.ids.senha.line_color_normal = (0, 1, 0, 1) # verde
            self.manager.current = 'Agendamento'
            self.IdUsuario = idUsuario
            self.manager.get_screen('Agendamento').idUsuario = idUsuario
            self.manager.current = 'Agendamento'
            

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
        self.idUsuario = 1
        self.listaID = []
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
        self.hora = value
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
        self.aviso.open()


    def registrar(self):
        if self.data and self.hora:
            data = f"{self.data} "+ f"{self.hora}"
            self.IdAgenda = db.registrarData(data, self.evento, self.idUsuario)
            self.addDados(self.data, self.hora, self.evento)

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
        self.data_tables.bind(on_check_press=self.pegarIDtable)
        self.add_widget(self.data_tables)

        self.retornarDados()


    
    def pegarIDtable(self, instance, row):
        if row[0] not in self.listaID:
            self.listaID.append(row[0])
        else:
            self.listaID.remove(row[0])
        
        
    def addDados(self, valorData="Não informado", valorHora="Não informado", valorEvento="Não informado"):
        
        valorData = formatar_data(str(valorData))
        
        self.data_tables.add_row([f"{self.IdAgenda}",f"{valorData}", f"{valorHora}", f"{valorEvento}"])
        
        
    def excluirDados(self):
        if self.listaID:
            for id in self.listaID:
                db.excluirData(id)

            self.listaID.clear()
            self.remove_widget(self.data_tables)
            self.tabela()
            
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