#-*- coding: utf-8 -*
from google.appengine.api import users
from google.appengine.ext import db

class UserForum(db.Model):
	idUser = db.IntegerProperty()
	loginGoogle = db.StringProperty(multiline=True)
	loginForum = db.StringProperty(multiline=True)
	position = db.StringProperty(multiline=True)
	name = db.StringProperty(multiline=True)
	lastName = db.StringProperty(multiline=True)
	
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