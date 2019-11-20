import psycopg2
import sqlite3
from flask import Flask, session

class conexion:
   @staticmethod
   def conect_post():
      try:
         connection = psycopg2.connect(database = "central2010", user = "reporte_web", password = ".112233.", host = "10.20.12.100", port = "5432")
         cursor=connection.cursor()
         return cursor
      except:
       return False

class conexion_sqlite:
   @staticmethod
   def conect_sql():
      try:
         conexion_sqlite=sqlite3.connect("sqlite.db",check_same_thread=False)
         cursor=conexion_sqlite.execute("SELECT nombre,clave,cliente FROM usuario_sbif")
         return cursor
      except:
       return False
