import MySQLdb
import threading
import time

class timeoutCounter(threading.Thread):
	def __init__(self, sqlHandler, timeout = 60):
		threading.Thread.__init__(self)
		self.sqlHandler = sqlHandler
		self.firstSetTO = timeout
		self.timeout = timeout

	def run(self):
		while True:
			time.sleep(1)
			self.timeout -= 1
			if self.timeout <= 0:
				break;
		self.sqlHandler.db = None
		self.sqlHandler.tc = None
		self.sqlHandler.close()

	def refresh(self):
		self.timeout = self.firstSetTO

class mySQLHandler:
	def __init__(self, host, user, password, database, timeout = 60, isLog = False):
		self.host = host
		self.user = user
		self.password = password
		self.database = database
		self.timeout = timeout
		self.db = None
		self.tc = None
		self.isLog = isLog
	
	def newConnection(self):
		if self.db and self.tc:
			self.tc.refresh()
			return
		self.db = MySQLdb.connect(self.host, self.user, self.password, self.database)
		self.cursor = self.db.cursor()
		self.tc = timeoutCounter(self, self.timeout)
		self.tc.start()

	def db_insert(self, table, data):
		col = " (";
		val = " (";
		flag = False
		for key in data.keys():
			if flag:
				col += ","
				val += ","
			else:
				flag = True
			col += key
			if type(data[key]) is str:
				val += "'"+data[key]+"'"
			else:
				val += str(data[key])
				
		col += ") ";
		val += ") ";
		sql = "INSERT INTO "+table+col+"VALUES"+val
		print sql
		try:
			self.newConnection()
			self.execute(sql)
			self.db.commit()
			return True
		except:
			self.db.rollback()
			return False
	
	def db_update(self, table, data,  _where = "true"):
		str_data = " ";
		flag = False
		for key in data.keys():
			if flag:
				str_data += ","
			else:
				flag = True
			str_data += key+" = "
			if type(data[key]) is str:
				str_data += "'"+data[key].replace('\'', '\'\'')+"'"
			else:
				str_data += str(data[key])
				
		sql = "UPDATE "+table+" SET "+str_data+" WHERE "+_where
		try:
			self.newConnection()
			self.execute(sql)
			self.db.commit()
			return True
		except:
			self.db.rollback()
			return False
			
	def db_delete(self, table, data,  _where = "false"):
		str_data = " ";
		flag = False
		for key in data.keys():
			if flag:
				str_data += ","
			else:
				flag = True
			str_data += key+" = "
			if type(data[key]) is str:
				str_data += "'"+data[key].replace('\'', '\'\'')+"'"
			else:
				str_data += str(data[key])
				
		sql = "DELETE FROM "+table+" WHERE "+_where
		try:
			self.newConnection()
			self.execute(sql)
			self.db.commit()
			return True
		except:
			self.db.rollback()
			return False
	
	def db_select(self, table, cols=[] ,  _where = "true"):
		column=''
		if len(cols) == 0:
			column = '*'
		flag = False
		for col in cols:
			if flag:
				column += ","
			else:
				flag = True
			column += col
		sql = "SELECT "+column+" FROM "+table+" WHERE "+_where
		try:
			self.newConnection()
			self.execute(sql)
			results = self.cursor.fetchall()
			return results
		except:
			return False
			
	def execute(self, sql):
		self.cursor.execute(sql)
		if self.isLog:
			print sql
	def string_validation(self, s):
		pass
	def close(self):
		self.db.close()