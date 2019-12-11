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
                                estado,fecha_inicio_evento,fecha_solucion,inframonitor,
                                coalesce(problema,''), coalesce(problema_genera,''), coalesce(solucion,''), coalesce(culpable,''),id
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
            usuario = session['cliente_usuario_id']
            cursor = conexion.conect_post()

            cursor.execute("""SELECT cu.nombre , c.nombre
                                FROM public.cliente_usuario cu inner join public.cliente c
                                ON cu.cliente_id = c.cliente_id
                                WHERE cu.cliente_usuario_id = %s""" , (usuario,))
            return cursor
        except:
         return False

class consulta_busqueda:
    @staticmethod
    def select_consultar(fecha_inicial_1,fecha_inicial_2):
        try:
             cursor = conexion.conect_post()
             cursor.execute("""SELECT
                                	estado,fecha_inicio_evento,fecha_solucion,inframonitor,
                                	coalesce(problema,''), coalesce(problema_genera,''), coalesce(solucion,''), coalesce(culpable,''),id
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
            flash("No se puede actualizar")

class insertar_registro:
    @staticmethod
    def insert(estado,fecha_inicio_evento, monitor, problema,culpable):

            cursor = conexion.conect_post()

            cursor.execute("SELECT MAX( id ) + 1 FROM sisticket.registro_sisticket")
            id_datos = cursor.fetchone()

            #FECHA ACTUAL
            fecha_creacion = datetime.now()

            local = session['option']
            if local == 'local':
                usuario = session["usr_local"][0][0]
                connection = psycopg2.connect(database = "central2010", user = "postgres", password = "", host = "172.16.5.117", port = "5432")
                cursor=connection.cursor()
                cursor.execute("""INSERT INTO sisticket.registro_sisticket
                                            (id, estado, usuario_nombre_insert ,fecha_inicio_evento, inframonitor, problema,fecha_carga,culpable)
                                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            								   (id_datos, estado, usuario, fecha_inicio_evento,monitor,problema,fecha_creacion,culpable))
                connection.commit()
                flash("Datos Ingresados Correctamente")
                return cursor

            else:
                usuario = session["usr_api"][0][0]
                usuario_id = session['cliente_usuario_id']
                connection = psycopg2.connect(database = "central2010", user = "postgres", password = "", host = "172.16.5.117", port = "5432")
                cursor=connection.cursor()
                cursor.execute("""INSERT INTO sisticket.registro_sisticket
                                                (id, estado,usuario_nombre_insert,usuario_id_insert,fecha_inicio_evento,inframonitor,problema,fecha_carga,culpable)
                                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            								    (id_datos, estado, usuario, usuario_id,fecha_inicio_evento,monitor,problema,fecha_creacion,culpable))

                connection.commit()
                flash("Datos Ingresados Correctamente")
                return cursor

class consulta_host:
    @staticmethod
    def select_consultar_host():
        try:
             cursor = conexion.conect_post()
             cursor.execute("""SELECT monitor_id, CONCAT( monitor_id ,' - ', hostname)
                                FROM sisticket.db_monitor
                                WHERE hostname is not null ORDER BY monitor_id;""" )
             return cursor
        except:
             flash("No se puede realizar busqueda de registro")

class clientMonitor:
    @staticmethod
    def selectClientMonitor(monitors):
        newMon='('
        for monitor in monitors:
            newMon+=str(monitor)+','
        newMon= newMon[:-1]
        newMon+=')'
        _select=str("SELECT distinct(c.cliente_id) as cliente_id, c.nombre, false AS infra_todocliente")
        _select+=" FROM public.cliente c, public.cliente_mapa_cliente_objetivo co"\
                " WHERE c.cliente_id = co.cliente_id"\
                " AND co.objetivo_id IN(SELECT Distinct(objetivo_id) FROM public.objetivo_config"\
                " WHERE es_ultima_config = 't' AND monitor_id <> '{}' AND ARRAY"+str(monitors)
        _select+=" && monitor_id) UNION SELECT distinct(c.cliente_id) as cliente_id, c.nombre, ie.infra_todocliente"\
                " FROM public.cliente c, sisticket.infracliente i, sisticket.infraestructura ie"\
                " WHERE c.cliente_id = i.cliente_id AND i.infra_id = ie.infra_id AND i.infra_id IN"+str(newMon)
        try:
             cursor = conexion.conect_post()
             cursor.execute(_select)
             cursor = cursor.fetchall()
             return cursor
        except:
             flash("No se puede realizar busqueda de registro")
        return ''

    @staticmethod
    def dataMonitor(id_monitor):
        _select=str("SELECT nombre from public.monitor where monitor_id=")+str(id_monitor)
        try:
             cursor = conexion.conect_post()
             cursor.execute(_select)
             cursor = cursor.fetchall()
             return cursor
        except:
             flash("No se puede realizar busqueda de registro")
        return ''
