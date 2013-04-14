#python2
# -*- coding: utf-8 -*-

import urllib, urllib2
import bs4
import datetime

class CAGR:
    '''Implementa a comunicação e obtenção de dados com o sistema CAGR da UFSC'''

    def __init__(self):
        '''Cria objeto que lida com cookies e obtem cookies necessarios para acesso posterior'''

        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        #Abre pagina uma vez para obter primeiro JSESSIONID
        res = self.opener.open('https://sistemas.ufsc.br/login')
        res = res.read().decode('utf-8')

        #Obtem lt (necessário para login posterior)
        ifrom = res.find('name="lt"')+17
        ito = res.find('"',ifrom)
        self.lt = res[ifrom:ito]

    def login(self, usr, psw):
        '''Realiza o login no Sistema da UFSC de forma a possibilitar o acesso ao CAGR'''

        url = 'https://sistemas.ufsc.br/login'
        data = {'userType':'alunoGraduacao', 'username':usr, 'password':psw, '_eventId':'submit', 'lt':self.lt}
        data = urllib.urlencode(data).encode('utf-8')

        request = urllib2.Request(url, data)
        response = self.opener.open(request)
        response = response.read().decode('utf-8')
        
        if 'logou com sucesso' in response:
            return True
        else:
            return False

    def getAulas(self, codigo_disciplina):  
        '''Obtem lista de aulas da disciplina. Cada item da lista é um dicionário com: local, diaS, horaI, horaF'''

        #Melhora desempenho, não precisa verificar o site a cada chamada
        if 'soup' not in vars(self):
            response = self.opener.open('https://cagr.sistemas.ufsc.br/modules/aluno/espelhoMatricula/')
            response = response.read().decode('utf-8').replace('\n','').replace('\t','')
            self.soup = bs4.BeautifulSoup(response)

        #Obtem Tabela Maior
        tabela = self.soup.find('th',text='Resultados').parent.parent.parent
        linha = tabela.find('td',text=codigo_disciplina)

        #Chega até elemento que contém Horários/Locais
        for i in range(12):
            linha = linha.next_element

        #Separa cada horário/local e remove tags <br/>
        dados = [x for x in linha.contents if type(x) is not bs4.element.Tag]

        aulas=[]  

        for d in dados:
            ds = d.split('/')

            horario = ds[0].strip()
            diaS = int(horario[0])
            qAulas = int(horario[-1])
            horai = datetime.datetime.strptime(horario[2:6],'%H%M')
            horaf = horai+datetime.timedelta(minutes=50*qAulas)            
            local = ds[1].strip()

            aulas.append({'local':local, 'diaS':diaS, 'horaI':horai, 'horaF':horaf})

        return aulas

    def grade(self):
        '''Gera lista com informações da cada disciplina'''

        info=[]

        url = 'https://cagr.sistemas.ufsc.br/modules/aluno/grade/'
        response = self.opener.open(url)
        response = response.read().decode('utf-8').replace('\n','').replace('\t','')

        soup = bs4.BeautifulSoup(response)        
        tabela = soup.find('table', width='540', align='center')
        
        for tr in tabela.contents[1:]:
            disciplina={}
            disciplina['codigo'] = tr.contents[0].text
            disciplina['turma'] = tr.contents[1].text.strip()
            disciplina['nome'] = tr.contents[2].text.encode('utf-8')
            disciplina['professores'] = [x.title().encode('utf-8') for x in tr.contents[3].contents if type(x) is not bs4.element.Tag]
            disciplina['aulas'] = self.getAulas(disciplina['codigo'])

            info.append(disciplina)
        
        return info



