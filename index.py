#@TODO:Agregar SHEBANG!!
#/srv/proyecto/entorno_virtual/bin/python
from flask import Flask, render_template, request, session,redirect, url_for,send_file,flash
from datetime import datetime, date, time, timedelta
import requests
from config import conexion_sqlite
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

	return render_template("template.html")



if(__name__ == "__main__"):
	#app.run(debug = True)
	app.run("0.0.0.0",5000)