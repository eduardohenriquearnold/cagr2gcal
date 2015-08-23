#python2
# -*- coding: utf-8 -*-

import gflags
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

from datetime import datetime, timedelta

FLAGS = gflags.FLAGS

class GCalendar:
    '''Classe que permite interação com os serviço de agenda do Google'''

    def __init__(self):
        '''Cria objeto necessário para autenticação'''

        self.flow = OAuth2WebServerFlow(client_id='',
                                   client_secret='',
                                   scope='https://www.googleapis.com/auth/calendar',
                                   redirect_uri='',
                                   user_agent='')

        # Servidor local de autenticação desabilitado, utilizarei WebPy para isso
        FLAGS.auth_local_webserver = False

    def getURI(self):
        '''Obtém URL para o usuário permitir acesso ao aplicativo'''

        return self.flow.step1_get_authorize_url()

    def exchange(self, code):
        '''Realiza a troca, oferecendo o codigo cedido pelo usuario e cria objetos necessarios para demais ações'''        

        credentials = self.flow.step2_exchange(code)
            
        http = httplib2.Http()
        http = credentials.authorize(http)

        self.service = build(serviceName='calendar', version='v3', http=http, developerKey='')
   

    def getCalendarID(self, title):
        '''Retorna a ID do calendário com o título descrito. Se não existir, retorna -1.'''

        calendar_list = self.service.calendarList().list().execute()
        
        for cal in calendar_list['items']:
            if cal['summary'] == title:
                return cal['id']

        return -1

    def createCalendar(self, title, description, location):
        '''Cria novo calendário e retorna sua ID'''

        calendar = {'summary':title, 'description':description, 'location':location}
        created_calendar = self.service.calendars().insert(body=calendar).execute()
        return created_calendar['id']

    def deleteCalendar(self, calID):
        '''Deleta calendário com o ID especificado'''
        
        self.service.calendars().delete(calendarId=calID).execute()

    def createRecEvent(self, calID, title, content, location, date, weekDay, lastDate, timeStart, timeEnd, timezone='America/Sao_Paulo'):
        '''Cria um evento recorrente semanal, a partir de date, no dia da semana weekDay (segunda=2). Recorrência acaba em lastDate. Todos os tipos relacionados a data são objetos de datetime.'''

        date = getNextWkDay(date, weekDay)

        event = {
          'summary': title,
          'description': content,
          'location': location,
          'start': {
            'dateTime': date.strftime('%Y-%m-%d')+'T'+timeStart.strftime('%H:%M:%S'),
            'timeZone': timezone
          },
          'end': {
            'dateTime': date.strftime('%Y-%m-%d')+'T'+timeEnd.strftime('%H:%M:%S'),
            'timeZone': timezone
          },
          'recurrence': [
            'RRULE:FREQ=WEEKLY;UNTIL='+lastDate.strftime('%Y%m%d')  
          ]
        }

        self.service.events().insert(calendarId=calID, body=event).execute()    

def getNextWkDay(date, weekDay):
    '''Obtem o próximo dia da semana a partir de date que corresponde ao weekDay'''

    #Converte para padrão da biblioteca (Segunda-feira = 0)
    weekDay -= 2

    while date.weekday() != weekDay:
        date += timedelta(days=1)

    return date



