#!/usr/bin/env python

import sys
import os 
import MySQLdb as mdb
import glob

SQLDIR = './sql/'

def main():
	FilesList = {} 
	ListFilesUniq = []
	ListOfTables = []

	# I find list of SQL scripts stored in a folder SQLDIR
	for m in glob.iglob(SQLDIR+'*.sql'):
		k=m.split('/')[-1]

		l=k.split('.')
		# If file like '015.apn.sql' (there is . after the number) 
		# I create dictionary like apn.15 = 015.apn.sql
		if len(l) == 3:
			FilesList[l[1]+'.'+str(int(l[0]))] = k

		# If file like '014ses.sql' or '1ses.sql' (there isn't . after the number) 
		# I find first not digit symbol and break FOR
		# I create dictionary like ses.14 = 014ses.sql
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
	# I make list of scripts (['apn.10', 'apn.13', 'apn.15',...)
	ListOfKey=FilesList.keys()

	try:
		# Connect to MYSQL using environment variables
		con = mdb.connect(os.environ["MYSQL_ENV_HOST"], os.environ["MYSQL_ENV_USER"], os.environ["MYSQL_ENV_PASSWORD"], os.environ["MYSQL_ENV_DATABASE"])
		cur = con.cursor()
		# I get versions of tables
		sqlsa="select * from "+os.environ["MYSQL_ENV_DATABASE"]+".version;"
		cur.execute(sqlsa)
		outsql = cur.fetchall()
		con.commit()
		# I create list table_name.version ['apn.10', 'ses.5']
		for o in outsql:
			ListOfTables.append(o[0]+'.'+str(o[1]))

		print("\nList of table.version: ") 
		for y in ListOfTables : print(y)
		# Compare list of scripts and list from MYSQL
		for pp in ListOfTables:
			TableName,TableVer = pp.split('.')

			for oo in ListOfKey :
				FileName,FileVer = oo.split('.')
				# If version in script > then in MYSQL add this record in new list => ListFilesUniq.
				if TableName == FileName and int(TableVer) < int(FileVer): 
					ListFilesUniq.append(FileName+'.'+FileVer)
		
		# I sort list
		ListFilesUniq.sort()

		print("\nFind "+str(len(ListFilesUniq))+" new scripts:")

		MaxVersion={} # Dictionary with max version of tables

		for pp in ListFilesUniq:
			TableName,TableVer = pp.split('.')

			#The latest version of the table is written last, because the list has been sorted before.
			MaxVersion[TableName]=TableVer	
			
			# I sent SQL files to MYSQL
			os.system("mysql -u {0} -p{1} {2} < {3}{4}".format(os.environ["MYSQL_ENV_USER"], os.environ["MYSQL_ENV_PASSWORD"], os.environ["MYSQL_ENV_DATABASE"], SQLDIR, FilesList[pp]))
			print(FilesList[pp])
		
		# I update version table
		for rr in MaxVersion : 	cur.execute("update version set version={0} where tables='{1}';".format(MaxVersion[rr], rr))
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

if __name__ == '__main__':
	main()