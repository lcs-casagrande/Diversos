##Imports necessários para raspar os dados da página
import requests
from bs4 import BeautifulSoup
##Import necessário para criação dos dataframes para análise
import pandas as pd
##Import necessário para criar o Profiling
import pandas_profiling as pp
from pandas_profiling import ProfileReport
##Import necessário para criação de gráficos
import matplotlib.pyplot as plt
##Import necessário para trabalhar com data e hora.
import datetime as dtm
from datetime import date as dt
##Import necessário para tratar acentuação
from unicodedata import normalize as nm
#Esta função captura o número do jogo e a Rodada conforme determinado pela CBF
def numJogoRodada(numJogo):
    ##Tratando a requisição que contém o número do jogo
    num_jogo = int(numJogo.get_text().strip().replace('Jogo: ','').replace('<font color="red">(W.O. Duplo)</font>', ''))

    ##if para calcular a rodada a que o jogo pertence
    '''
        1) A cada rodada ocorrem 10 jogos, sendo assim quando o número do jogo dividido por 10 tiver 0 como resto, a rodada será o quociente.
        Ex: 200 / 10 = 20 - sendo assim a rodada a que pertence o jodo de nº 200 é a 20
        2) Caso o **resto da divisão** do número do jogo for **diferente de 0** então a rodada corresponderá ao quociente (inteiro) + 1
        Ex: 201 / 10 = 20,1 - sendo assim a rodada será 21, pois o resto é 1 e o quociente inteiro é 20.
    '''
    if (num_jogo%10 == 0):
        rodada = int(int(num_jogo)/10)
    else:
        rodada = int((int(num_jogo)//10)+1)

    ##if para calcular o turno ao qual o jogo pertence
    '''
       O Campeonato tem 380 jogos ao todo, sendo:
       - 1º turno: do jogo 1 ao 190
       - 2º turno: do jogo 191 ao 380
    '''
    if int(num_jogo) <= 190:
      turno = 1
    else:
      turno = 2
    ##lista para armazenar o numero do jogo, rodada e turno
    listaResult = [num_jogo, rodada, int(turno)]
    return listaResult

##Remover acentos das strings
def remove_acentos(str):
  str_sem_acentos = nm('NFKD', str).encode('ASCII', 'ignore').decode('ASCII')
  return str_sem_acentos

#Esta função captura o estádio em que ocorreu o jogo
def estadio(localJogo):
    estadio = localJogo[0].get_text().split(" - ")[0].strip()
    estadio_jogo = remove_acentos(estadio)
    return estadio_jogo

#Esta função captura a cidade em que ocorreu o jogo
def cidade(localJogo):
    cidade = localJogo[0].get_text().split(" - ")[1].strip()
    cidade_jogo = remove_acentos(cidade)
    return cidade_jogo

#Esta função captura o estado em que ocorreu o jogo
def uf(localJogo):
    uf_jogo = localJogo[0].get_text().split(" - ")[2].strip()
    return uf_jogo

#Esta função captura o dia da semana em que ocorreu o jogo
def diaSemana(dataJogo):
    diasemana_origem = dataJogo[1].get_text().split(",")[0].strip()
    diasemana = remove_acentos(diasemana_origem)
    return diasemana

##Padronizar mês da data do Jogo.
def retMes(mes):
    if mes == 'Janeiro':
        return '01'
    elif mes == 'Fevereiro':
        return '02'
    elif mes == 'Março':
        return '03'
    elif mes == 'Abril':
        return '04'
    elif mes == 'Maio':
        return '05'
    elif mes == 'Junho':
        return '06'
    elif mes == 'Julho':
        return '07'
    elif mes == 'Agosto':
        return '08'
    elif mes == 'Setembro':
        return '09'
    elif mes == 'Outubro':
        return '10'
    elif mes == 'Novembro':
        return '11'
    elif mes == 'Dezembro':
        return '12'

#Esta função captura a data em que ocorreu o jogo
def dataJogo(dataJogo):
    data_origem = dataJogo[1].get_text().split(",")[1].strip()
    lstData = data_origem.split(" de ")                        ##Separar os elementos que compõe a data
    dia = lstData[0]                                           ##Extrai o dia da data
    mes = retMes(lstData[1])                                   ##Extrai o mês da data
    ano = lstData[2]                                           ##Extrai o ano da data
    dtjg = dt(int(ano), int(mes), int(dia)).isoformat()      ##Concatena os elementos da data para o formato AAAA-MM-DD
    return dtjg

#Esta função captura o horário em que ocorreu o jogo
def horaJogo(dataJogo):
    hora_jogo = dataJogo[2].get_text().strip()
    return hora_jogo

#Esta função retorna o time mandante e seu estado de origem
def retMandante(captTimes):
    time = captTimes[0].get_text().split("-")[0].strip()
    uf = captTimes[0].get_text().split("-")[1].strip()
    if (uf == 'PR' and (time == 'Athletico Paranaense' or time == 'Atlético Paranaense' or time == 'Atletico' or time == 'Atlético')):
      mandante_origem = 'Athletico Paranaense'
    elif (uf != 'PR' and (time == 'Atlético' or time == 'Atletico')):
      mandante_origem = 'Atlético-'+uf
    elif (time == 'America Fc' or time == 'América Fc' or time == 'America' or time == 'América'):
      mandante_origem = 'América-'+uf
    elif (time == 'Botafogo'):
      mandante_origem = 'Botafogo-'+uf
    elif (time == 'C.r.b.' or time == 'Crb'):
      mandante_origem = 'CRB-'+uf
    elif (time == 'A.b.c.' or time == 'Abc'):
      mandante_origem = 'ABC-'+uf
    elif (time == 'A.s.a.'):
      mandante_origem = 'ASA-'+uf
    elif (time == 'Csa'):
      mandante_origem = 'CSA-'+uf
    else:
      mandante_origem = time
    mandante = remove_acentos(mandante_origem)
    listaMandante = [mandante, uf]
    return listaMandante

#Esta função retorna o time visitante e seu estado de origem
def retVisitante(captTimes):
    time = captTimes[1].get_text().split("-")[0].strip()
    uf = captTimes[1].get_text().split("-")[1].strip()
    if (uf == 'PR' and (time == 'Athletico Paranaense' or time == 'Atlético Paranaense' or time == 'Atletico' or time == 'Atlético')):
      visitante_origem = 'Athletico Paranaense'
    elif (uf != 'PR' and (time == 'Atlético' or time == 'Atletico')):
      visitante_origem = 'Atlético-'+uf
    elif (time == 'America Fc' or time == 'América Fc' or time == 'America' or time == 'América'):
      visitante_origem = 'América-'+uf
    elif (time == 'Botafogo'):
      visitante_origem = 'Botafogo-'+uf
    elif (time == 'C.r.b.' or time == 'Crb'):
      visitante_origem = 'CRB-'+uf
    elif (time == 'A.b.c.' or time == 'Abc'):
      visitante_origem = 'ABC-'+uf
    elif (time == 'A.s.a.'):
      visitante_origem = 'ASA-'+uf
    elif (time == 'Csa'):
      visitante_origem = 'CSA-'+uf
    else:
      visitante_origem = time
    visitante = remove_acentos(visitante_origem)
    listaVisitante = [visitante, uf]
    return listaVisitante

#Esta função retorna quantos gols o time mandante fez
def retGolMandante(captGols):
    if len(captGols)== 2:
        golmandante = captGols[0].get_text().strip()
    else:
        golmandante = 0
    return int(golmandante)

#Esta função retorna quantos gols o time visitante fez
def retGolVisitante(captGols):
    if len(captGols)== 2:
        golvisitante = captGols[1].get_text().strip()
    else:
        golvisitante = 0
    return int(golvisitante)

#Esta função retorna o total de gols do jogo
def totalGolsJogo(captGols):
    if len(captGols)== 2:
        golmandante = captGols[0].get_text().strip()
        golvisitante = captGols[1].get_text().strip()
        gols_jogo = int(golmandante) + int(golvisitante)
    else:
        gols_jogo = 0
    return int(gols_jogo)

##Esta função retorna uma lista que armazena quem venceu o jogo, qual o resultado do mandante e qual o resultado do visitante
def resultJogo(captGols):
    if len(captGols)== 2:
        gol_mandante = int(captGols[0].get_text().strip())
        gol_visitante = int(captGols[1].get_text().strip())
        if (gol_mandante == gol_visitante):
            resultado = 'Empate'
            resultado_mandante = 'Empate'
            resultado_visitante = 'Empate'
        elif (gol_mandante > gol_visitante):
            resultado = 'Mandante'
            resultado_mandante = 'Vitoria'
            resultado_visitante = 'Derrota'
        else:
            resultado = 'Visitante'
            resultado_mandante = 'Derrota'
            resultado_visitante = 'Vitoria'
    else:
        resultado = 'WO Duplo'
        resultado_mandante = 'WO'
        resultado_visitante = 'WO'
    listaResult = [resultado, resultado_mandante, resultado_visitante]
    return listaResult

##Esta função retorna o placar do jogo (padronizado sempre do maior para o menor número de gols)
def placarJogo(golMandante, golVisitante):
    if (gol_mandante == -1):
        placar = 'W-O'
    elif (gol_mandante == gol_visitante):
        placar = str(gol_mandante)+'-'+str(gol_visitante)
    elif (gol_mandante > gol_visitante):
        placar = str(gol_mandante)+'-'+str(gol_visitante)
    else:
        placar = str(gol_visitante)+'-'+str(gol_mandante)
    return placar
