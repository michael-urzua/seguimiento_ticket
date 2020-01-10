from config import conexion
from flask import Flask, session
from datetime import datetime, date, time, timedelta
import psycopg2
import psycopg2.extras
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
                                   estado,fecha_inicio_evento,fecha_solucion,inframonitor,fecha_aviso_clientes,
                                   coalesce(problema,''), coalesce(problema_genera,''), coalesce(solucion,''), coalesce(culpable,''),id
                                FROM
                                   sisreg.registro_sisticket
                               where
                                   fecha_inicio_evento::date = (NOW()::date - INTERVAL '1 DAYS') order by estado, fecha_inicio_evento asc""")
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
                                WHERE cu.cliente_usuario_id = %s""", (usuario,))
            return cursor
        except:
            return False


class consulta_user:
    @staticmethod
    def select_user():
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT distinct concat(cu.cliente_usuario_id,' - ',cu.nombre) ,cu.activo_perfil,c.nombre
                                FROM public.cliente_usuario cu inner join public.cliente c
                                ON cu.cliente_id = c.cliente_id
                                where cu.nombre is not null and cu.activo_perfil = 'si' and c.nombre = 'Atentus'  """)
            return cursor
        except:
            return False


class consulta_perfil:
    @staticmethod
    def select_perfil():
        try:
            usuario = session['cliente_usuario_id']
            cursor = conexion.conect_post()

            cursor.execute("""SELECT a1.nombre_perfil, b2.activo
                                  FROM sisreg.perfil a1 inner join sisreg.perfil_usuario b2
                                  ON a1.perfil_id = b2.perfil_id
                                  where b2.cliente_usuario_id = '%s'""", (usuario,))
            return cursor
        except:
            return False


class consulta_busqueda:
    @staticmethod
    def select_consultar(fecha_inicial_1, fecha_inicial_2):
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT
                                	estado,fecha_inicio_evento,coalesce(CAST(fecha_solucion AS VARCHAR(25)),'SIN FECHA'),
                                    coalesce(CAST(fecha_aviso_clientes AS VARCHAR(25)),'SIN FECHA'),inframonitor,
                                	coalesce(problema,''), coalesce(problema_genera,''), coalesce(solucion,''), coalesce(culpable,''),id
                                 FROM
                                    sisreg.registro_sisticket
                                where
                                    fecha_inicio_evento::date BETWEEN %s and %s order by estado, fecha_inicio_evento asc""",
                                    (fecha_inicial_1, fecha_inicial_2,))
            return cursor
        except:
            flash("NO SE PUEDE REALIZAR BUSQUEDA !!", "danger")


class actualiza_registro:
    @staticmethod
    def update_registro(id, fecha_solucion, fecha_aviso_clientes, problema, problema_genera, solucion, culpable, estado):
        try:
            fecha_actualizacion = datetime.now()

            usuario = session["usr_api"][0][0]
            usuario_id = session['cliente_usuario_id']

            # connection = psycopg2.connect(
                # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")

            connection = psycopg2.connect(
                database="central2010", user="postgres", password="", host="172.16.5.117", port="5432")
            cursor = connection.cursor()
            cursor.execute(""" UPDATE sisreg.registro_sisticket
                                    SET usuario_nombre_update=%s,usuario_id_update =%s,fecha_solucion=%s,fecha_aviso_clientes=%s,problema=%s,
                                    problema_genera=%s,solucion=%s,culpable=%s,estado=%s
                                    WHERE id = %s
                                    """, (usuario, usuario_id, fecha_solucion, fecha_aviso_clientes, problema, problema_genera, solucion, culpable, estado, id))
            connection.commit()
            flash("DATOS ACTUALIZADOS EXITOSAMENTE", "success")

        except:
            flash("NO ES POSIBLE ACTUALIZAR !!", "danger")
            return cursor


class insertar_registro:
    @staticmethod
    def insert(estado, fecha_inicio_evento, monitor, problema, culpable, fecha_solucion, fecha_aviso_clientes, problema_genera, solucion):

        cursor = conexion.conect_post()

        cursor.execute(
            "SELECT MAX( id ) + 1 FROM sisreg.registro_sisticket")
        id_datos = cursor.fetchone()

        # FECHA ACTUAL
        fecha_creacion = datetime.now()

        usuario = session["usr_api"][0][0]
        usuario_id = session['cliente_usuario_id']

        # connection = psycopg2.connect(
            # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")
        connection = psycopg2.connect(
            database="central2010", user="postgres", password="", host="172.16.5.117", port="5432")
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO sisreg.registro_sisticket
                                            (id, estado,usuario_nombre_insert,usuario_id_insert,fecha_inicio_evento,inframonitor,problema,
                                            fecha_carga,culpable,fecha_solucion,fecha_aviso_clientes,problema_genera,solucion)
                                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                       (id_datos, estado, usuario, usuario_id, fecha_inicio_evento, monitor, problema,
                        fecha_creacion, culpable, fecha_solucion, fecha_aviso_clientes, problema_genera, solucion))

        connection.commit()
        flash("DATOS INGRESADOS CON EXITO", "success")
        return cursor


class consulta_host:
    @staticmethod
    def select_consultar_host():
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT id, nombre
                                    FROM(
                                    	(SELECT infra_id AS id, CONCAT(infra_id,' - ',infra_nombre) AS nombre, 'A' AS tipo
                                    			from sisreg.infraestructura
                                    			where activo = TRUE)

                                    	UNION

                                    	(SELECT monitor_id AS id, CONCAT( monitor_id ,' - ', hostname) AS nombre, 'Z' AS tipo
                                    					FROM sisreg.db_monitor
                                    					WHERE hostname is not null)
                                    ) AS foo
                                    ORDER BY tipo, id;""")
            return cursor
        except:
            flash("NO SE PUEDE REALIZAR LA BUSQUEDA DE MONITOR", "danger")


class clientMonitor:
    @staticmethod
    def selectClientMonitor(monitors):
        newMon = '('
        for monitor in monitors:
            newMon += str(monitor) + ','
        newMon = newMon[:-1]
        newMon += ')'
        _select = str(
            "SELECT distinct(c.cliente_id) as cliente_id, c.cliente_id ||'.'||c.nombre AS nombre, false AS infra_todocliente")
        _select += " FROM public.cliente c, public.cliente_mapa_cliente_objetivo co"\
            " WHERE c.cliente_id = co.cliente_id"\
            " AND co.objetivo_id IN(SELECT Distinct(objetivo_id) FROM public.objetivo_config"\
            " WHERE es_ultima_config = 't' AND monitor_id <> '{}' AND ARRAY" + \
            str(monitors)
        _select += " && monitor_id) UNION SELECT distinct(c.cliente_id) as cliente_id, c.nombre, ie.infra_todocliente"\
            " FROM public.cliente c, sisreg.infracliente i, sisreg.infraestructura ie"\
            " WHERE c.cliente_id = i.cliente_id AND i.infra_id = ie.infra_id AND i.infra_id IN" + \
            str(newMon)
        try:
            cursor = conexion.conect_post()
            cursor.execute(_select)
            cursor = cursor.fetchall()
            return cursor
        except:
            flash("NO SE PUEDE REALIZAR LA BUSQUEDA DE REGISTRO", "danger")
        return ''

    @staticmethod
    def dataMonitor(id_monitor):
        _select = str(
            "SELECT nombre from public.monitor where monitor_id=") + str(id_monitor)
        if id_monitor > 90000:
            _select = str(
                "SELECT infra_nombre from sisreg.infraestructura where infra_id=") + str(id_monitor)
        try:
            cursor = conexion.conect_post()
            cursor.execute(_select)
            cursor = cursor.fetchall()
            return cursor
        except:
            flash("NO SE PUEDE REALIZAR LA BUSQUEDA DE REGISTRO", "danger")
        return ''


class consulta_user_perfiles:
    @staticmethod
    def select_user_perfil():
        try:
            cursor = conexion.conect_post()
            cursor.execute("""SELECT a2.nombre_perfil, a1.activo, a1.nombre_usuario,a1.id_perfil_usuario
                              FROM sisreg.perfil_usuario  a1 inner join sisreg.perfil a2
                              ON a1.perfil_id = a2.perfil_id""")
            return cursor
        except:
            return False


class actualiza_perfil:
    @staticmethod
    def update_perfil(nombre_perfil, activo, id_perfil_usuario):
        try:
            # connection = psycopg2.connect(
                # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")

            connection = psycopg2.connect(
                database="central2010", user="postgres", password="", host="172.16.5.117", port="5432")
            cursor = connection.cursor()
            cursor.execute(""" UPDATE sisreg.perfil_usuario SET  perfil_id=%s, activo=%s WHERE id_perfil_usuario =%s """,
                           (nombre_perfil, activo, id_perfil_usuario))

            connection.commit()
            flash("DATOS ACTUALIZADOS EXITOSAMENTE", "success")
        except:
            flash("NO ES POSIBLE ACTUALIZAR !!", "danger")
            return cursor


class insertar_registro_perfil:
    @staticmethod
    def insert_perfil(list, perfil_usr_add, activo_usr_add):

        # connection = psycopg2.connect(
            # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")

        connection = psycopg2.connect(
            database="central2010", user="postgres", password="", host="172.16.5.117", port="5432")
        cursor = connection.cursor()
        for data in list:
            cursor.execute(
                "SELECT MAX( id_perfil_usuario ) + 1 FROM sisreg.perfil_usuario")
            id_datos = cursor.fetchone()
            cursor.execute("""INSERT INTO sisreg.perfil_usuario(id_perfil_usuario, cliente_usuario_id, perfil_id, activo, nombre_usuario)
                                    VALUES (%s,%s,%s,%s,%s)""",
                           (id_datos, data["id_usuario_perfil"], perfil_usr_add, activo_usr_add, data["nombre_usuario_perfil"]))
            connection.commit()
        flash("DATOS INGRESADOS CON EXITO", "success")
        return cursor


class actualizar_public_cliente:
    @staticmethod
    def update_public_cliente(list):
        try:
            # connection = psycopg2.connect(
                # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")

            connection = psycopg2.connect(
                database="central2010", user="postgres", password="", host="172.16.5.117", port="5432")
            cursor = connection.cursor()
            for data in list:

                cursor.execute(""" UPDATE public.cliente_usuario SET  activo_perfil = 'no' WHERE cliente_usuario_id = %s """,
                               (data["id_usuario_perfil"],))
                connection.commit()

        except:
            flash("NO ES POSIBLE ACTUALIZAR !!", "danger")
            return cursor


class actualizar_rtrim:
    @staticmethod
    def update_rtrim():
        try:
            # connection = psycopg2.connect(
                # database="central2010", user="reporte_web", password=".112233.", host="10.20.12.100", port="5432")
            connection = psycopg2.connect(
                database="central2010", user="postgres", password="", host="172.16.5.117", port="5432")
            cursor = connection.cursor()
            cursor.execute(
                """ UPDATE sisreg.perfil_usuario SET cliente_usuario_id=rtrim(cliente_usuario_id) """)
            connection.commit()
        except:
            flash("NO ES POSIBLE ACTUALIZAR  RTRIM!!", "danger")
            return cursor
