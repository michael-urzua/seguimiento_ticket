from config import conexion,conexion_sqlite
from flask import Flask, session
from datetime import datetime, date, time, timedelta
import psycopg2,psycopg2.extras
from flask import flash
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class consulta_user_compania:
    @staticmethod
    def select_user_compania():
        try:
            # usuario = session['cliente_usuario_id']
            cursor = conexion.conect_post()

            # cursor.execute("""SELECT cu.nombre , c.nombre
            #                     FROM public.cliente_usuario cu inner join public.cliente c
            #                     ON cu.cliente_id = c.cliente_id
            #                     WHERE cu.cliente_usuario_id = %s""" , (usuario,))
            cursor.execute("""SELECT cu.nombre , c.nombre
                                FROM public.cliente_usuario cu inner join public.cliente c
                                ON cu.cliente_id = c.cliente_id
                                WHERE cu.cliente_usuario_id = 9142""")
            return cursor
        except:
         return False

class consulta_busqueda:
    @staticmethod
    def select_consultar(fecha_inicial_1,fecha_inicial_2):
        print(fecha_inicial_1,fecha_inicial_2)
        try:
             cursor = conexion.conect_post()
             cursor.execute("""SELECT
                                	estado,fecha_inicio_evento,fecha_solucion,monitor_hostname,
                                	problema, problema_genera, solucion, culpable
                                 FROM
                                    sisticket.registro_sisticket
                                where
                                    fecha_inicio_evento::date BETWEEN %s and %s""" , (fecha_inicial_1,fecha_inicial_2,))
             print("cuuursoooor",cursor)
             return cursor
        except:
             flash("No se puede realizar busqueda de registro")
