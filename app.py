#python2
# -*- coding: utf-8 -*-

#Adiciona path para a biblioteca
import sys
sys.path.insert(0, 'lib')

import cagr
import gcalendar

import datetime
from flask import Flask, request, session, render_template, redirect

#Cria aplicação com suporte a sessions e templates
app = Flask(__name__, static_folder='static/', template_folder='static/', static_url_path='')
app.secret_key = '"(*kM]Sn;+8Ck5M~(+p\sRYm2'


@app.route('/', methods=['GET', 'POST'])
def index():
        if request.method == 'GET':
                if 'code' in session:
                        return render_template('form.html')
                else:
                        return render_template('mensagem.html', msg=u'Para utilizar esse sistema você deve autorizar este aplicativo a utilizar seu serviço de agenda do Google. Faça isso clicando no botão abaixo.', lnk=gcalendar.GCalendar().getURI())                
                
        if request.method == 'POST':
                #Get POST info
                matricula = request.form['matricula']
                senha = request.form['senha']
                titAgenda = request.form['nome_agenda']
                data = request.form
                
                try:
                    dataI = datetime.datetime.strptime(data['element_6_1']+data['element_6_2']+data['element_6_3'],'%d%m%Y')
                    dataT = datetime.datetime.strptime(data['element_7_1']+data['element_7_2']+data['element_7_3'],'%d%m%Y')
                except:
                    return render_template('mensagem.html', msg=u'Data inválida.')

                #Obtem dados do CAGR
                try:
                    CAGR = cagr.CAGR()
                    CAGR.login(matricula, senha)
                    grade = CAGR.grade()
                except:            
                    return render_template('mensagem.html', msg=u'Problema no serviço do CAGR. Verifique sua matrícula e senha.')

                #Faz conexão com API do Google Calendar
                try:
                    GC = gcalendar.GCalendar()
                    GC.exchange(session['code'])
                except:
                    return render_template('mensagem.html', msg=u'Problema no serviço Google Calendar. Tente Novamente.')

                #Realiza Importação
                calID = GC.getCalendarID(titAgenda)

                if calID != -1:
                    return render_template('mensagem.html', msg=u'Esse calendário já existe. Escolha outro nome ou remova-o primeiro.')
                
                calID = GC.createCalendar(titAgenda, 'Horários de Aula', 'UFSC')

                for disciplina in grade:
                    professores = '\n'.join(disciplina['professores'])
                    desc = 'Código: {0}\nTurma: {1}\nProfessores:\n{2}'.format(disciplina['codigo'], disciplina['turma'], professores)

                    for aula in disciplina['aulas']:
                        GC.createRecEvent(calID, disciplina['nome'], desc, aula['local'], dataI, aula['diaS'], dataT, aula['horaI'], aula['horaF'])

                return render_template('mensagem.html', msg=u'Calendário importado com sucesso.', lnk='/about')


@app.route('/googleAPI')
def googleAPI():
        if 'code' in request.args:
                session['code'] = request.args['code']
                
        #Redireciona para HOME
        return redirect('/')

        
@app.route('/about')
def about():
        return render_template('about.html')
                

#Inicia Servidor
if __name__ == "__main__":
        app.run(host='127.0.0.1', port=8001, debug=False)

