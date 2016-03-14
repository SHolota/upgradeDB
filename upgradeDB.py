#!/usr/bin/env python

import sys
import os 
import ConfigParser
import MySQLdb as mdb
import logging
import glob

LOGFILE = './upgrDB.log'
CONFIGFILE = './db.conf'
SQLDIR = './sql/'

def main():
	FilesList = {}
	ListFiles = []
	ListOfTables = []

	config = ConfigParser.RawConfigParser()
	config.read(CONFIGFILE)

	# logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO, filename = LOGFILE)
	
	# sqldir = config.get('dir','sqldir')
	
	# logging.info("Start upgrade database")

	for m in glob.iglob(SQLDIR+'*.sql'):
		k=m.split('/')[-1]

		l=k.split('.')
		if len(l) == 3:
			#'01.ses.sql'
			FilesList[l[1]+'.'+str(int(l[0]))] = k
		else:
			numver=''
			inum=0
			tablename=''
			for s in k:
				if s.isdigit() : 
					numver += s
					inum += 1
				else:
					break
			tablename = l[0][inum:]

			FilesList[tablename+'.'+str(int(numver))] = k

	print("List of file: ") 
	for t in FilesList.keys():
		print(t+" = "+FilesList[t])
	print("")

	ListOfKey=FilesList.keys()
	# print(ListOfKey)

	try:
		con = mdb.connect(config.get('mysql','host'), config.get('mysql','user'), config.get('mysql','password'), config.get('mysql','database'))
		cur = con.cursor()
		sqlsa="select * from "+config.get('mysql','database')+".version;"
		cur.execute(sqlsa)
		outsql = cur.fetchall()
		con.commit()
	except mdb.Error, e:
		if con:
			con.rollback()
			print("Error "+str(e.args[0])+":"+e.args[1])
			sys.exit(1)
	finally:
		if con:
			con.close()

	for o in outsql:
		ListOfTables.append(o[0]+'.'+str(o[1]))

	print("List of tables.version: ") 
	for y in ListOfTables: 
		print(y)

	print("")

	for pp in ListOfTables:
		TableName,TableVer = pp.split('.')

		for oo in ListOfKey :
			FileName,FileVer = oo.split('.')
			# print(FileName+'.'+FileVer)
			if TableName == FileName and int(TableVer) < int(FileVer): 
				ListFiles.append(FileName+'.'+FileVer)

	ListFiles.sort()
	logging.info("Find "+str(len(ListFiles))+"new scripts")
	print("List of new scripts: ") 

	# print(ListFiles)

	for pp in ListFiles:
		print(FilesList[pp])
		# logging.info("Find new scripts: "+FilesList[pp])

if __name__ == '__main__':
	main()