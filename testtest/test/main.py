#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import methods

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app



class BasePage(webapp.RequestHandler):
	def get(self):
		greetings = methods.autorization("/")
		template_values = {'greetings': greetings,}
		
		path = os.path.join(os.path.join(os.path.dirname(__file__), 'html/'), 'content.html')
		self.response.out.write(template.render(path, template_values))	
		
class NewsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.join(os.path.dirname(__file__), 'html/'), 'news.html')
		self.response.out.write(template.render(path, None))	
		
class HistoryPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/history.html')
		self.response.out.write(template.render(path, None))
		
class SchedulePage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/schedule/schedule.html')
		self.response.out.write(template.render(path, None))	
		
class Schedule1Page(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/schedule/sch1.html')
		self.response.out.write(template.render(path, None))	
		
class Schedule2Page(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/schedule/sch2.html')
		self.response.out.write(template.render(path, None))	

class Schedule3Page(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/schedule/sch3.html')
		self.response.out.write(template.render(path, None))
		
class Schedule4Page(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/schedule/sch4.html')
		self.response.out.write(template.render(path, None))	
		
class SearchPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/search.html')
		self.response.out.write(template.render(path, None))
		
class ContentPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'html/content.html')
		self.response.out.write(template.render(path, None))


def main():
    application = webapp.WSGIApplication([  ('/', BasePage),
											('/news', NewsPage),
											('/schedule', SchedulePage),
											('/sch1', Schedule1Page),
											('/sch2', Schedule2Page),
											('/sch3', Schedule3Page),
											('/sch4', Schedule4Page),
											('/history', HistoryPage),
											('/search', SearchPage),
											('/content', ContentPage)],
                                         debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
