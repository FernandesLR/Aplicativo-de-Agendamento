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
    if email == '' or ('@gmail.com' not in email and '@hotmail.com' not in email):
        return False
    cnx = conectar() # inicializa a função conectar
    task = cnx.cursor() # Objeto cursor para poder executar comandos SQL

    task.execute("SELECT * FROM usuario WHERE email = %s AND senha = %s", (email, senha)) # Consulta se o email está registrado no banco de dados

    select = task.fetchone() # Retorna o resultado da consulta

    task.close()
    cnx.close() # Finaliza o banco de dados
    
    if select: # Verifica se é verdadeiro
        id = select[0]
        print('email e senha encontrado')
        return True, id
    else:
        print('email e senha não encontrado')
        return False


def cadastrarUsuario(email, senha):
    if email == '' or ('@gmail.com' not in email and '@hotmail.com' not in email):
        return False
    
    elif verificarLogin(email, senha) == False: # se for igual a false é porque a conta não existe
        cnx = conectar()
        task = cnx.cursor()
        try:
            task.execute('INSERT INTO usuario(email, senha) VALUES(%s, %s)', (email, senha))
        except ValueError as e:
            print(e)
        finally:
            id = task.lastrowid
            cnx.commit()
            task.close()
            cnx.close() # Finaliza o banco de dados
            return id
        
    else: # isso impede que o usuário tente cadastrar várias vezes a mesma conta
        return False 
        


def registrarData(data, evento='', fk=0):
    try:
        fk = fk[1]
    except ValueError as e:
        fk = fk[0]
        print(e)
    finally:
        cnx = conectar()
        task = cnx.cursor()
        task.execute('INSERT INTO agenda(diaHora, evento, IdUsuario) VALUES(%s, %s, %s)', (data, evento, fk))
        cnx.commit()
        id = task.lastrowid
        task.close()
        cnx.close()
        return id



def excluirData(idAgenda):
    cnx = conectar()
    task = cnx.cursor()
    task.execute('DELETE FROM agenda WHERE agendaID = %s', (idAgenda,))
    cnx.commit()
    task.close()
    cnx.close()


def retornarData(idUsuario):
    try:
        idUsuario = idUsuario[1]
    except ValueError as e:
        idUsuario = [0]
        print(e)
    finally:
        cnx = conectar() 
        task = cnx.cursor()

        task.execute("SELECT agendaID, diaHora, evento FROM agenda WHERE IdUsuario = %s", (idUsuario,))
        
        select = task.fetchall() # Retorna o resultado da consulta

        if select:
            return select
        else:
            return False
