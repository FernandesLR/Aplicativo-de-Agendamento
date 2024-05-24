# importando dependências
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager # importa o grenciador de telas
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker # interface de agenda
from kivy.core.window import Window
from kivy.uix.label import Label # apagar depois
import db # importa o banco de dados


Window.size = (490, 900) # tamanho minimo de tela
class GerenciadorTelas(ScreenManager):
    pass

class PrimeiraTela(Screen): # vai ser a tela de login
    def login(self):
        # pega os textos das caixinhas que são o email e a senha
        email = self.ids.email.text
        senha = self.ids.senha.text
        if db.verificarLogin(email, senha): # passa para uma função externa que vai tratar os dados
            self.ids.email.line_color_normal = (0, 1, 0, 1) # verde
            self.ids.senha.line_color_normal = (0, 1, 0, 1) # verde
            self.manager.current = 'Agendamento'

        else:
            self.ids.email.line_color_normal = (1, 0, 0, 1)  # Vermelho
            self.ids.senha.line_color_normal = (1, 0, 0, 1)  # Vermelho
            msgDeErro = Label(text="Email ou Senha inválidos!", color=[1, 0, 0, 1])
            self.add_widget(msgDeErro)

    def cadastrar(self):
        email = self.ids.email.text
        senha = self.ids.senha.text
        db.cadastrarUsuario(email, senha)
        





class SegundaTela(Screen):
    def calendario(self):
        calendario = MDDatePicker()
        calendario.open()
    def registrarDia(self):
        pass # esse pass serve para a função ser ignorada pq ainda não tem comandos nela
    def excluirDia(self):
        pass
    def trocar(self):
        pass




class MeuApp(MDApp):
    def build(self): # função construtora do app que vai renderizar a tela
        self.theme_cls.primary_palette = "Red"
        Builder.load_file('login.kv')
        Builder.load_file('agendamento.kv') # importa o arquivo de estilização
        return GerenciadorTelas() # retorna o objeto gerenciador de telas

    

# Testes

#email = 'pedrinho123@gmail.com'
#senha = '2412@'


MeuApp().run() # executa o código