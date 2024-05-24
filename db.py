import mysql.connector # api para conectar no banco de dados
import env
def conectar(): 
    try:
        coneccao = mysql.connector.connect(user= env.user, # usuario para acessar o banco de dados
                                    password= env.password, # senha
                                    port= env.port, # a porta
                                    host= env.host, # dominio do banco de dados
                                    database= env.database # nome do banco de dados
                                    )
        return coneccao # retorna a variavel que faz conecção caso esteja tud ok
    except mysql.connector.Error as err:
        print(err)
    




# Verificar login e senha
def verificarLogin(email, senha):
    cnx = conectar() # inicializa a função conectar
    task = cnx.cursor() # Objeto cursor para poder executar comandos SQL

    task.execute("SELECT * FROM usuario WHERE email = %s AND senha = %s", (email, senha)) # Consulta se o email está registrado no banco de dados

    select = task.fetchone() # Retorna o resultado da consulta

    task.close()
    cnx.close() # Finaliza o banco de dados
    
    if select: # Verifica se é verdadeiro
        print('email e senha encontrado')
        return True
    else:
        print('email e senha não encontrado')
        return False


def confirmar(email):
    cnx = conectar()
    task = cnx.cursor()
    task.execute("SELECT * FROM usuario WHERE email = %s", (email,))
    select = task.fetchone()
    task.close()
    cnx.close()
    if select:
        return True
    else:
        return False
    
#----------- Testes

#verificarLogin('ana123@gmail.com', '23356') # Retorna verdadeiro
#verificarLogin('ana123@gmail.com', 23356) # Retorna verdadeiro

#verificarLogin('aaana123@gmail.com', 45646542) # Retorna falso


def cadastrarUsuario(email, senha):
    if confirmar(email) == False: # se for igual a false é porque a conta não existe
        cnx = conectar()
        task = cnx.cursor()
        task.execute('INSERT INTO usuario(email, senha) VALUES(%s, %s)', (email, senha))
        cnx.commit()
        task.close()
        cnx.close() # Finaliza o banco de dados
    else: # isso impede que o usuário tente cadastrar várias vezes a mesma conta
        return False 
        


#----------- Testes

cadastrarUsuario('FernandoPedro@Hotmail.com', 54451)

