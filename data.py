from config import conexion,conexion_sqlite
from flask import Flask, session
from datetime import datetime, date, time, timedelta
import psycopg2,psycopg2.extras
from flask import flash
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class consulta_inicial:
    @staticmethod
    def select_inicio():
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT
                                estado,fecha_inicio_evento,fecha_solucion,monitor_hostname,
                                problema, problema_genera, solucion, culpable,id
                                 FROM
                                    sisticket.registro_sisticket
                                where
                                    fecha_inicio_evento::date  = (NOW()::date - INTERVAL '1 DAYS') """)
            return cursor
        except:
         return False


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
        try:
             cursor = conexion.conect_post()
             cursor.execute("""SELECT
                                	estado,fecha_inicio_evento,fecha_solucion,monitor_hostname,
                                	problema, problema_genera, solucion, culpable,id
                                 FROM
                                    sisticket.registro_sisticket
                                where
                                    fecha_inicio_evento::date BETWEEN %s and %s order by fecha_inicio_evento asc""" , (fecha_inicial_1,fecha_inicial_2,))
             return cursor
        except:
             flash("No se puede realizar busqueda de registro")

class actualiza_registro:
    @staticmethod
    def update_registro(id,estado):
        try:

            local = session['option']
            if local == 'local':
                usuario = session["usr_local"][0][0]
                connection = psycopg2.connect(database = "central2010", user = "postgres", password = "", host = "172.16.5.117", port = "5432")
                cursor=connection.cursor()
                cursor.execute(""" UPDATE sisticket.registro_sisticket
               							SET estado=%s,usuario_nombre_update=%s
            							WHERE id = %s
            							""",(estado,usuario,id))
                connection.commit()
                flash("Datos Actualizados Correctamente")


            else:
                usuario = session["usr_api"][0][0]
                usuario_id = session['cliente_usuario_id']

                connection = psycopg2.connect(database = "central2010", user = "postgres", password = "", host = "172.16.5.117", port = "5432")
                cursor=connection.cursor()
                cursor.execute(""" UPDATE sisticket.registro_sisticket
               							SET estado=%s,usuario_nombre_update=%s,usuario_id_update =%s
            							WHERE id = %s
            							""",(estado,usuario,usuario_id,id))
                connection.commit()
                flash("Datos Actualizados Correctamente")

        except:
            #return('no se actualizo')
            flash("No se puede actualizar")

# class insertar_registro:
#     @staticmethod
#     def insert(estado,objetivo_id,paso_orden,paso_nombre,incidencia_id,
# 									fecha_inicial,fecha_final,causa_id,categoria_id,observacion,inc,
# 									pbi,cliente_id,usuario_nombre_insert,activo):
#
#             # ID
#             cursor = conexion.conect_post()
#
#             cursor.execute("SELECT MAX( id ) + 1 FROM sbif.registro")
#             id_datos = cursor.fetchone()
#
#
#             #FECHA ACTUAL
#             fecha_creacion = datetime.now()
#
#             local = session['option']
#             if local == 'local':
#                 usuario = session["usr_local"][0][0]
#                 connection = psycopg2.connect(database = "central2010", user = "reporte_web", password = ".112233.", host = "10.20.12.100", port = "5432")
#                 cursor=connection.cursor()
#                 cursor.execute("""INSERT INTO sbif.registro(
#                         						id, estado, objetivo_id, objetivo_nombre,paso_orden,paso_nombre,incidencia_id, fecha_inicial, fecha_final,
#                          						fecha_creacion,causa_id, categoria_id,observacion, inc, pbi,cliente_id,usuario_nombre_insert,activo,usuario_local_insert)
#                                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
#             								   (id_datos, estado, objetivo_id, objetivo_nombre,paso_orden,paso_nombre,incidencia_id, fecha_inicial, fecha_final,
#                                                fecha_creacion,causa_id, categoria_id,observacion,inc, pbi,cliente_id,usuario_nombre_insert,activo,usuario))
#                 connection.commit()
#                 flash("Datos Ingresados Correctamente")
#                 return cursor
#
#             else:
#                 # USUARIO SESSION
#                 usuario_insert = session['cliente_usuario_id']
#
#                 connection = psycopg2.connect(database = "central2010", user = "reporte_web", password = ".112233.", host = "10.20.12.100", port = "5432")
#                 cursor=connection.cursor()
#                 cursor.execute("""INSERT INTO sbif.registro(
#                         						id, estado, objetivo_id, objetivo_nombre,paso_orden,paso_nombre,incidencia_id, fecha_inicial, fecha_final,
#                          						fecha_creacion,causa_id, categoria_id,observacion, inc, pbi,cliente_id,usuario_nombre_insert,activo,usuario_id_insert)
#                                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
#             								   (id_datos, estado, objetivo_id, objetivo_nombre,paso_orden,paso_nombre,incidencia_id, fecha_inicial, fecha_final,
#                                                fecha_creacion,causa_id, categoria_id,observacion,inc, pbi,cliente_id,usuario_nombre_insert,activo,usuario_insert))
#
#                 connection.commit()
#                 flash("Datos Ingresados Correctamente")
#                 return cursor

class consulta_host:
    @staticmethod
    def select_consultar_host():
        try:
             cursor = conexion.conect_post()
             cursor.execute("""SELECT CONCAT( monitor_id ,' - ', hostname)
                                FROM sisticket.db_monitor  ORDER BY monitor_id;""" )
             return cursor
        except:
             flash("No se puede realizar busqueda de registro")
