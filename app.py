#python2
# -*- coding: utf-8 -*-

import web
import cagr
import gcalendar
import datetime

urls = (
    '/', 'index',
    '/googleAPI', 'googleAPI',
    '/about', 'about',
    '/(.+)', 'static'
)

#Cria aplicação com suporte a sessions e templates
web.config.debug = False
app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('web/sessions'))
render = web.template.render('web/www', base='layout')

class index:
    def GET(self):
        if 'code' in session:          
            return render.form()
        else:
            return render.mensagem('Para utilizar esse sistema você deve autorizar este aplicativo a utilizar seu serviço de agenda do Google. Faça isso clicando no botão abaixo.', gcalendar.GCalendar().getURI())   

    def POST(self):
        data = web.input()

        #Obtem dados do Formulario
        matricula = data.matricula
        senha = data.senha
        titAgenda = data.nome_agenda

        try:
            dataI = datetime.datetime.strptime(data.element_6_1+data.element_6_2+data.element_6_3,'%d%m%Y')
            dataT = datetime.datetime.strptime(data.element_7_1+data.element_7_2+data.element_7_3,'%d%m%Y')
        except:
            return render.mensagem('Data inválida.')

        #Obtem dados do CAGR
        try:
            CAGR = cagr.CAGR()
            CAGR.login(matricula, senha)
            grade = CAGR.grade()
        except:            
            return render.mensagem('Problema no serviço do CAGR. Verifique sua matrícula e senha.')

        #Faz conexão com API do Google Calendar
        try:
            GC = gcalendar.GCalendar()
            GC.exchange(session.code)
        except:
            return render.mensagem('Problema no serviço Google Calendar. Tente Novamente.')

        #Realiza Importação
        calID = GC.getCalendarID(titAgenda)

        if calID != -1:
            return render.mensagem('Esse calendário já existe. Escolha outro nome ou remova-o primeiro.')
        
        calID = GC.createCalendar(titAgenda, 'Horários de Aula', 'UFSC')

        for disciplina in grade:
            professores = '\n'.join(disciplina['professores'])
            desc = 'Código: {0}\nTurma: {1}\nProfessores:\n{2}'.format(disciplina['codigo'], disciplina['turma'], professores)

            for aula in disciplina['aulas']:
                GC.createRecEvent(calID, disciplina['nome'], desc, aula['local'], dataI, aula['diaS'], dataT, aula['horaI'], aula['horaF'])

        return render.mensagem('Calendário importado com sucesso.', '/about')
                   

class googleAPI:
    def GET(self):
        data = web.input()

        if 'code' in data:
            session.code = data.code

        #Redireciona para HOME
        raise web.seeother('/')

class about:
    def GET(self):
        return render.about()

class static:
    cType = {'html': 'text/html', 'js':'application/javascript', 'css':'text/css', 'gif':'image/gif', 'png':'image/png'}

    def GET(self, file):

        ext = file.split('.')[-1]

        if ext == 'html':
            file = None

        try:
            web.header("Content-Type", self.cType[ext])
            return open('web/www/'+file, 'rb').read()
        except:
            return '404 - file not found'

#Inicia Servidor
if __name__ == "__main__":
    app.run()

