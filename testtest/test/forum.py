#-*- coding: utf-8 -*-

import os
import cgi
import time

from datetime import datetime, timedelta
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db

# Форум ##############################################
def autorization(path):
		greetings = ""
		if users.get_current_user():
			greetings += ("<a href='#'> %s</a>&nbsp;&nbsp;&nbsp;<a href=\"%s\">выйти</a>" 
			% (users.get_current_user().nickname(), users.create_logout_url(path)))
			isLogin = True

			isUser = False
			usersForum = db.GqlQuery("SELECT * FROM UserForum")
			userForum = UserForum()
			
			for tmp_user in usersForum:
				if (tmp_user.loginGoogle == users.get_current_user().nickname()):
					isUser = True
			if (isUser == False):
				if (usersForum):
					userForum.idUser = usersForum.count() + 1	
				else:
					userForum.idUser = 1
				userForum.loginGoogle = users.get_current_user().nickname()
				userForum.loginForum = None
				userForum.position = 'user'
				userForum.name = None
				userForum.lastName = None	
				userForum.put()
				
		else:
			greetings += ("<a href=\"%s\">Войти на сайт" % users.create_login_url(path))
			isLogin = False
			
		return greetings
			
def getIdUser(googleName):
	usersForum = db.GqlQuery("SELECT * FROM UserForum")
	for tmp_user in usersForum:
		if (tmp_user.loginGoogle == googleName):
			return tmp_user.idUser

def getUserById(idUser):
	usersForum = db.GqlQuery("SELECT * FROM UserForum")
	for tmp_user in usersForum:
		if (tmp_user.idUser == idUser):
			return tmp_user

class UserForum(db.Model):
	idUser = db.IntegerProperty()
	loginGoogle = db.StringProperty(multiline=True)
	loginForum = db.StringProperty(multiline=True)
	position = db.StringProperty(multiline=True)
	name = db.StringProperty(multiline=True)
	lastName = db.StringProperty(multiline=True)
	

class ForumPage(webapp.RequestHandler):
	def get(self):
		page = int(self.request.get('page'))
		
		greetings = autorization("/forum?page=1")
		
		if users.get_current_user():
			isLogin = True
		else:
			isLogin = False
			
		topicsQuery = db.GqlQuery("SELECT * FROM Topic ORDER BY dateTopic DESC")
		for topic in topicsQuery:
			user = getUserById(topic.idAuthor)
			if (user.loginForum):
				topic.author = user.loginForum
				topic.put()

		
	
		countPages = int(topicsQuery.count()/20)
		if (topicsQuery.count()%20):
			countPages += 1
		
		topicsOnPage = []
		startTopic = page * 20 - 19
		endTopic = startTopic + 19
		count = 1
		for topic in topicsQuery:
			if (count >= startTopic and count <= endTopic):
				topicsOnPage.append(topic)
			count += 1
			
		countPages = int(topicsQuery.count() / 20)
		if (topicsQuery.count() % 20):
			countPages += 1

		visibleAllPages = []
		visibleStartPages = []
		visibleMiddlePages = []
		visibleEndPages = []

		if countPages < 10:
			for count in range(countPages):
				visibleAllPages.append(count + 1)
			visibleStartSeparator = False
			visibleEndSeparator = False

		elif (page < 6):
			if (page < 3):
				for pageForum in range(3):
					visibleStartPages.append(pageForum + 1)
			else:
				for pageForum in range(page + 1):
					visibleStartPages.append(pageForum + 1)
			visibleStartSeparator = False
			visibleEndSeparator = True
			visibleEndPages.append(countPages - 2)
			visibleEndPages.append(countPages - 1)
			visibleEndPages.append(countPages)
			
		elif (page > countPages - 5):
			visibleStartPages.append(1)
			visibleStartPages.append(2)
			visibleStartPages.append(3)
			visibleStartSeparator = True
			visibleEndSeparator = False
			if (page > countPages - 2):
				visibleEndPages.append(countPages - 2)
				visibleEndPages.append(countPages - 1)
				visibleEndPages.append(countPages)
			else:
				visibleEndPages.append(page - 1)
				visibleEndPages.append(page)
				count = page + 1
				while count <= countPages:
					visibleEndPages.append(count)
					count += 1
		else:	
			visibleStartPages.append(1)
			visibleStartPages.append(2)
			visibleStartPages.append(3)
			visibleStartSeparator = True
			visibleMiddlePages.append(page - 1)
			visibleMiddlePages.append(page)
			visibleMiddlePages.append(page + 1)
			visibleEndSeparator = True
			visibleEndPages.append(countPages - 2)
			visibleEndPages.append(countPages - 1)
			visibleEndPages.append(countPages)

		template_values = {
					'isLogin' : isLogin,
      				'greetings': greetings,
					'topics': topicsOnPage,
					'countPages' : countPages, 
					'visibleAllPages' : visibleAllPages,
					'visibleStartPages' : visibleStartPages,
					'visibleStartSeparator' : visibleStartSeparator,
					'visibleMiddlePages' : visibleMiddlePages,
					'visibleEndPages' : visibleEndPages,
					'visibleEndSeparator' : visibleEndSeparator
      				   }
		
		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'forum.html')
		self.response.out.write(template.render(path, template_values))
#Топик############################################################################################################################
class Topic(db.Model):
	idTopic = db.IntegerProperty()
	author = db.StringProperty(multiline=True)
	idAuthor = db.IntegerProperty()
	nameTopic = db.StringProperty(multiline=True)
	dateTopic = db.StringProperty(multiline=True)

class CreateTopicPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'createtopic.html')
		self.response.out.write(template.render(path, None))

class CreateTopic(webapp.RequestHandler):
	def post(self):
		queryLastTopic = db.Query(Topic)
		queryLastTopic.order("-idTopic")
		lastTopic = queryLastTopic.get()
    		
		if (self.request.get('nameTopic')):
			topic = Topic()
			if lastTopic:		
				topic.idTopic = lastTopic.idTopic + 1
			else:
				topic.idTopic = 1

			topic.author = users.get_current_user().nickname()
			topic.idAuthor = getIdUser(users.get_current_user().nickname())
    			topic.nameTopic = self.request.get('nameTopic')
			topic.dateTopic = datetime.now().strftime('%d.%m.%y %H:%M')
			
			if (self.request.get('message')):
				message = Message()
				message.idMessage = 1
				message.Row = 1
				message.idTopic = topic.idTopic
				message.author = users.get_current_user().nickname()
				message.idAuthor = getIdUser(users.get_current_user().nickname())
				message.message = self.request.get('message').replace('\n','</br>')
				message.dateMessage = datetime.now().strftime('%d.%m.%y %H:%M')	
		    		
				message.put()
				topic.put()
	
				self.redirect('/topic?idTopic=%s&topicPage=1' % topic.idTopic)
			else:
				self.redirect('/errorCreateTopic')	
		else:
			self.redirect('/errorCreateTopic')

		

class ErrorCreateTopic(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'errorCreateTopic.html')
		self.response.out.write(template.render(path, None))

class TopicPage(webapp.RequestHandler):
	def get(self):
		greetings = autorization("/topic?idTopic=1&topicPage=1")
		
		idTopic = self.request.get('idTopic')
		topicPage = int(self.request.get('topicPage'))
		
		topicQuery = db.GqlQuery("SELECT * FROM Topic WHERE idTopic = %s" % idTopic)
		topic = topicQuery.get()	
    		
		user = getUserById(topic.idAuthor)
		if (user.loginForum):
			topic.author = user.loginForum
			topic.put()

		messagesQuery = db.GqlQuery("SELECT * FROM Message WHERE idTopic = %s ORDER BY idMessage" % idTopic)

		for message in messagesQuery:
			user = getUserById(message.idAuthor)
			if (user.loginForum):
				message.author = user.loginForum
				message.put()

		if users.get_current_user():
			if(user.loginGoogle == users.get_current_user().nickname()):
				message.isAuthor = True
				message.put()
			else:
				message.isAuthor = False
				message.put()

		messagesOnPage = []
		startMessage = topicPage * 20 - 19
		endMessage = startMessage + 19
		count = 1
		for message in messagesQuery:
			if (count >= startMessage and count <= endMessage):
				messagesOnPage.append(message)
			count += 1
			
		countPages = int(messagesQuery.count() / 20)
		if (messagesQuery.count() % 20):
			countPages += 1

		visibleAllPages = []
		visibleStartPages = []
		visibleMiddlePages = []
		visibleEndPages = []

		if countPages < 10:
			for count in range(countPages):
				visibleAllPages.append(count + 1)
			visibleStartSeparator = False
			visibleEndSeparator = False
		elif (topicPage < 6):
			if (topicPage < 3):
				for page in range(3):
					visibleStartPages.append(page + 1)
			else:
				for page in range(topicPage + 1):
					visibleStartPages.append(page + 1)
			visibleStartSeparator = False
			visibleEndSeparator = True
			visibleEndPages.append(countPages - 2)
			visibleEndPages.append(countPages - 1)
			visibleEndPages.append(countPages)
			
		elif (topicPage > countPages - 5):
			visibleStartPages.append(1)
			visibleStartPages.append(2)
			visibleStartPages.append(3)
			visibleStartSeparator = True
			visibleEndSeparator = False
			if (topicPage > countPages - 2):
				visibleEndPages.append(countPages - 2)
				visibleEndPages.append(countPages - 1)
				visibleEndPages.append(countPages)
			else:
				visibleEndPages.append(topicPage - 1)
				visibleEndPages.append(topicPage)
				count = topicPage + 1
				while count <= countPages:
					visibleEndPages.append(count)
					count += 1
		else:	
			visibleStartPages.append(1)
			visibleStartPages.append(2)
			visibleStartPages.append(3)
			visibleStartSeparator = True
			visibleMiddlePages.append(topicPage - 1)
			visibleMiddlePages.append(topicPage)
			visibleMiddlePages.append(topicPage + 1)
			visibleEndSeparator = True
			visibleEndPages.append(countPages - 2)
			visibleEndPages.append(countPages - 1)
			visibleEndPages.append(countPages)

		template_values = {
					'greetings' : greetings,
      				'messages': messagesOnPage,
					'topic': topic,
					'visibleAllPages' : visibleAllPages,
					'visibleStartPages' : visibleStartPages,
					'visibleStartSeparator' : visibleStartSeparator,
					'visibleMiddlePages' : visibleMiddlePages,
					'visibleEndPages' : visibleEndPages,
					'visibleEndSeparator' : visibleEndSeparator
				  }

		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'topic.html')
		self.response.out.write(template.render(path, template_values))
#Сообщение########################################################################################################################
class Message(db.Model):
	Row = db.IntegerProperty()
	idMessage = db.IntegerProperty()
	idTopic = db.IntegerProperty()
	author = db.StringProperty(multiline=True)
	idAuthor = db.IntegerProperty()
	message = db.StringProperty(multiline=True)
	dateMessage = db.StringProperty(multiline=True)
	isAuthor =  db.BooleanProperty()

class AddMessage(webapp.RequestHandler):
	def post(self):
		idTopic = self.request.get('idTopic')

		queryLastMessage = db.Query(Message)
		queryLastMessage.order("-idMessage")
		lastMessage = queryLastMessage.get()

		
		messagesQuery = db.GqlQuery("SELECT * FROM Message WHERE idTopic=%s" % idTopic)

		topicPage = int(messagesQuery.count() / 20)
		if (messagesQuery.count() % 20):
			topicPage += 1
			
		if(self.request.get('messageArea')):
	
			message = Message()
			message.idMessage = lastMessage.idMessage + 1

			if(lastMessage.Row == 1):
				message.Row = 2
			else:
				message.Row = 1

			message.idTopic = int(idTopic)
			message.author = users.get_current_user().nickname()
			message.idAuthor = getIdUser(users.get_current_user().nickname())
			message.message =  self.request.get('messageArea').replace('\n','<br />')
			message.dateMessage = datetime.now().strftime('%d.%m.%y %H:%M')	
		    	message.put()

			
    			
			self.redirect('/topic?idTopic=%s&topicPage=%s' % (idTopic, topicPage))
		else:
			self.redirect('/errorAddMessage?idTopic=%s&topicPage=%s' % (idTopic, topicPage))

class ErrorAddMessage(webapp.RequestHandler):
	def get(self):
		idTopic = self.request.get('idTopic')
		topicPage = self.request.get('topicPage')

		template_values = {
						'idTopic':idTopic,
      					'topicPage':topicPage
				  }

		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'errorAddMessage.html')
		self.response.out.write(template.render(path, template_values))

class EditMessage(webapp.RequestHandler):
	def get(self):
		greetings = autorization("/editMessage")
		idTopic = self.request.get('idTopic')
		idMessage = self.request.get('idMessage')

		if(idTopic and idMessage):
				messageQuery = db.GqlQuery("SELECT * FROM Message WHERE idTopic=%s AND idMessage=%s" % (idTopic, idMessage))
				for message in messageQuery:
					if(getIdUser(users.get_current_user().nickname()) == message.idAuthor):
						messageText = message.message.replace('<br />','\n')
	
						template_values = {
									'messageText': messageText,
									'idTopic': idTopic,
									'idMessage': idMessage,
									'greetings': greetings
								  }
			
						path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'editMessage.html')
						self.response.out.write(template.render(path, template_values))
					else:
						pass

class ActionEditMessage(webapp.RequestHandler):
	def post(self):
		idTopic = self.request.get('idTopic')
		idMessage = self.request.get('idMessage')
		messageText = self.request.get('messageText')
		greetings = autorization("/actionEditMessage")

		if(idTopic and idMessage and messageText):
			messageQuery = db.GqlQuery("SELECT * FROM Message WHERE idTopic=%s AND idMessage=%s" % (idTopic, idMessage))
			for message in messageQuery:
				if(getIdUser(users.get_current_user().nickname()) == message.idAuthor):
					
					message.message = messageText.replace('\n','<br />')
					message.put()
			
					template_values = {
								'greetings': greetings,
								'idTopic': idTopic
							  }
					self.redirect('/successEditMessage?idTopic=%s' % idTopic)
				else:
					pass
		else:	
			pass
class ActionDeleteMessage(webapp.RequestHandler):
	def get(self):
		greetings = autorization("/actionDeleteMessage")
		idTopic = self.request.get('idTopic')
		idMessage = self.request.get('idMessage')
    		
		if(idTopic and idMessage):
			messageQuery = db.GqlQuery("SELECT * FROM Message WHERE idTopic=%s AND idMessage=%s" % (idTopic, idMessage))
			for message in messageQuery:
				if(getIdUser(users.get_current_user().nickname()) == message.idAuthor):
				
					message.delete()
			
					template_values = {
								'greetings': greetings,
								'idTopic': idTopic
							  }
					self.redirect('/successDeleteMessage?idTopic=%s' % idTopic)
				else:
					pass
		else:
			pass

class SuccessEditMessage(webapp.RequestHandler):
	def get(self):
		greetings = autorization("/successEditMessage")
		idTopic = self.request.get('idTopic')
			
		template_values = {
					'greetings': greetings,
					'idTopic': idTopic
				  }

		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'successEditMessage.html')
		self.response.out.write(template.render(path, template_values))

class SuccessDeleteMessage(webapp.RequestHandler):
	def get(self):
		greetings = autorization("/successDeleteMessage")
		idTopic = self.request.get('idTopic')
			
		template_values = {
					'greetings': greetings,
					'idTopic': idTopic
				  }

		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'successDeleteMessage.html')
		self.response.out.write(template.render(path, template_values))
#####################################################################################################################################
class User(webapp.RequestHandler):
	def get(self):

		userById = db.GqlQuery("SELECT * FROM UserForum WHERE idUser = %s" % self.request.get('id'))
		for userForum in userById:
			loginGoogle = userForum.loginGoogle
			login = userForum.loginForum
			position = userForum.position
			name = userForum.name
			lastName = userForum.lastName
			isUser = False
			if (userForum.loginGoogle == users.get_current_user().nickname()):
				isUser = True

		template_values = {
					'isUser': isUser,
					'loginGoogle': loginGoogle,
					'login': login,
					'position': position,
					'name': name,
					'lastName': lastName
				  }

		path = os.path.join(os.path.join(os.path.dirname(__file__), 'forum'), 'user.html')
		self.response.out.write(template.render(path, template_values))

class SaveChanges(webapp.RequestHandler):
	def post(self):

		query = db.GqlQuery("SELECT * FROM UserForum WHERE idUser = %s" % getIdUser(self.request.get('loginGoogle')))
		for userForum in query:
			idUser = userForum.idUser

			if self.request.get('login'):
				userForum.loginForum = self.request.get('login')
			else:
				userForum.loginForum = None
			
			if self.request.get('name'):
				userForum.name = self.request.get('name')
			else:
				userForum.name = None

			if self.request.get('lastName'):
				userForum.lastName = self.request.get('lastName')
			else:
				userForum.lastName = None

			userForum.put()

		self.redirect('/user?id=%s' % idUser)

#########################################################
		
application = webapp.WSGIApplication(
                                     [
											('/forum', ForumPage),
											('/createTopic', CreateTopicPage),
											('/actionCreateTopic', CreateTopic),
											('/topic', TopicPage),
											('/addMessage', AddMessage),
											('/editMessage', EditMessage),
											('/successEditMessage', SuccessEditMessage),
											('/actionEditMessage', ActionEditMessage),
											('/actionDeleteMessage', ActionDeleteMessage),
											('/successDeleteMessage', SuccessDeleteMessage),
											('/errorCreateTopic', ErrorCreateTopic),	
											('/errorAddMessage', ErrorAddMessage),
											('/user', User),
											('/saveChanges', SaveChanges)
								     ],
                                     debug=True)

def main():
	run_wsgi_app(application)
	
if __name__ == "__main__":
	main()
