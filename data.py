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
                                    re.estado, re.objetivo_id,re.objetivo_nombre, re.paso_orden,re.paso_nombre,cau.causa_nombre,inci.incidencia_nombre,
                                    re.fecha_inicial::timestamp,re.fecha_final::timestamp, coalesce(re.observacion,''), coalesce(re.inc,''), coalesce(re.pbi,''),
                                    cate.categoria_nombre,re.activo,re.id
                                FROM
                                    sbif.registro re inner join sbif.causa cau on re.causa_id = cau.causa_id
                                    inner join sbif.incidencia inci on inci.incidencia_id = re.incidencia_id
                                    inner join sbif.categoria cate on cate.categoria_id = re.categoria_id
                                where
                                    re.fecha_inicial::date BETWEEN %s and %s""" , (fecha_inicial_1,fecha_inicial_2,))
             return cursor
        except:
             flash("No se puede realizar busqueda de registro")
