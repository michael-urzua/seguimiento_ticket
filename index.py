#@TODO:Agregar SHEBANG!!
#/srv/proyecto/entorno_virtual/bin/python
from flask import Flask, render_template, request, session,redirect, url_for,send_file,flash
from datetime import datetime, date, time, timedelta
import requests
from config import conexion_sqlite
from data import consulta_busqueda,consulta_user_compania,actualiza_registro,consulta_inicial,consulta_host,insertar_registro
from utils.get_token import get
from utils.globals import url2,url_chek
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.secret_key = 'many random bytes'


@app.route("/",methods=["GET","POST"])
def index():

	return render_template("login.html")

@app.route("/logout",methods=["GET","POST"])
def logout():

	session.clear()
	return redirect(url_for('index'))


def session_token(var_session):
	if var_session["option"]=='api':
 		validar_session =requests.get(url_chek+url2+var_session['token'],allow_redirects=False,verify=False).content
		return validar_session
	else:
		return 'True'


@app.route('/acceso',methods=["GET","POST"])
def acceso():

	usuario = request.form['email']
	clave = request.form['password']
	option = request.form['opcion_radiobtn']


	if option == 'local':
		session["option"]='local'
		cursor= conexion_sqlite.conect_sql()
		respuesta = cursor.fetchall()

		if respuesta[0][0] == usuario and respuesta[0][1] == clave :
			return redirect(url_for('inicio'))

		else:
			flash("Usuario y/o Clave son invalidos ")
			return redirect(url_for('index'))


	elif option=='api':

		r = get.get_api(usuario, clave)
		if r == False:
			flash("Problemas en la conexion API ")
			return redirect(url_for('index'))

		status = r["status"]
		#VARIABLES SESSION -.---------)
		if status == 0:
			session["option"]='api'
			token = r["data"]["token"]
			cliente_usuario_id = r["data"]["cliente_usuario_id"]

			#VARIABLES SESSION -.---------
			session['cliente_usuario_id']=cliente_usuario_id
			session['token'] = token
			return redirect(url_for('inicio'))
		else:
			flash("Usuario y/o Clave son invalidos ")
			return redirect(url_for('index'))

@app.route('/inicio')
def inicio():

	if len(session) == 0:
		return redirect(url_for('index'))

	variable = session_token(session)
	if variable == 'False':
		return render_template("login.html")

	cursor=consulta_inicial.select_inicio()
	if cursor == False:

		flash("No hay conexion a la BD")
		return redirect(url_for('index'))

	cursor_host=consulta_host.select_consultar_host()
	host_name = cursor_host.fetchall()

	local = session['option']
	if local == 'local':
		cursor= conexion_sqlite.conect_sql()
		respuesta = cursor.fetchall()
		session["usr_local"]=(respuesta)
		usuario = session["usr_local"][0][0]
		cliente = session["usr_local"][0][2]

		return render_template("template.html" ,data = cursor, usuario = usuario , compania = cliente,host_name = host_name  )
	else:
		cursor1=consulta_user_compania.select_user_compania()
		cliente_usuario = cursor1.fetchall()
		session["usr_api"]=(cliente_usuario)
		usuario = session["usr_api"][0][0]
		cliente = session["usr_api"][0][1]
		return render_template("template.html" ,data = cursor,usuario = usuario , compania = cliente,host_name = host_name )


@app.route("/consultar" ,methods=["GET","POST"])
def consultar():

	from operator import itemgetter

	variable = session_token(session)
	if variable == 'False':
		return render_template("login.html")

	fecha  = request.form['fecha']
	fecha_inicial_1=fecha.split(" ")[0]
	fecha_inicial_2=fecha.split(" ")[2]
	fecha_inicial_1= datetime.strptime(str(fecha_inicial_1), '%d/%m/%Y')
	fecha_inicial_2= datetime.strptime(str(fecha_inicial_2), '%d/%m/%Y')

	cursor=consulta_busqueda.select_consultar(fecha_inicial_1,fecha_inicial_2)
	data = cursor.fetchall()

	print("dataaaaaaa",data)

	cursor_host=consulta_host.select_consultar_host()
	host_name = cursor_host.fetchall()

	local = session['option']

	if local == 'local':
		usuario = session["usr_local"][0][0]
		cliente = session["usr_local"][0][2]
		return render_template("template.html", data = data , ayer=fecha, usuario = usuario , compania = cliente ,host_name = host_name  )
	else:
		cursor3=consulta_user_compania.select_user_compania()
		cliente_usuario = cursor3.fetchall()
		nombre = cliente_usuario[0][0]
		cliente = cliente_usuario[0][1]
		return render_template("template.html", data = data , ayer=fecha ,usuario = nombre , compania = cliente,host_name = host_name  )


@app.route("/actualizar",methods=['POST'])
def actualizar():

	variable = session_token(session)

	if variable == 'False':
		return render_template("login.html")


	id		= request.form['id']
	estado	= request.form['estado']

	cursor=actualiza_registro.update_registro(id,estado)


	#return render_template("template.html" ,persona = cursor ,ayer = yesterday)
	return redirect(url_for('inicio'))

@app.route("/insertar",methods=['POST'])
def insertar():

	variable = session_token(session)
	if variable == 'False':
		return render_template("login.html")

	# estado 			= 't'
	# fecha_inicio_evento		= request.form['fecha_inicio_evento']
	#
	monitor_hostname	= request.form.getlist('monitor_hostname')
	print("monitor_hostnameeeee",monitor_hostname)
	# problema		= request.form['problema']
	#
	# # print("fecha_inicialllllll",fecha_inicial)
	#
	# cursor=insertar_registro.insert(estado,fecha_inicio_evento, monitor_hostname, problema)

	return redirect(url_for('inicio'))


if(__name__ == "__main__"):
	#app.run(debug = True)
	app.run("0.0.0.0",5000)
