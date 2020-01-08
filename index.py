# @TODO:Agregar SHEBANG!!
# /srv/proyecto/entorno_virtual/bin/python
from flask import Flask, render_template, request, session, redirect, url_for, send_file, flash
from datetime import datetime, date, time, timedelta
import requests
from data import consulta_busqueda, consulta_user_compania, actualiza_registro,\
 consulta_inicial, consulta_host, insertar_registro, clientMonitor, consulta_perfil,  \
 consulta_user, consulta_user_perfiles,actualiza_perfil,insertar_registro_perfil,actualizar_public_cliente,actualizar_rtrim

from utils.get_token import get
from utils.globals import url2, url_chek
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.secret_key = 'many random bytes'


@app.route("/", methods=["GET", "POST"])
def index():

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()
    return redirect(url_for('index'))


def session_token(var_session):
    try:
        validar_session = requests.get(
            url_chek + url2 + var_session['token'], allow_redirects=False, verify=False).content
        return validar_session
    except:
     return 'True'


@app.route('/acceso', methods=["GET", "POST"])
def acceso():

    usuario = request.form['email']
    clave = request.form['password']


    r = get.get_api(usuario, clave)
    if r == False:
        flash("Problemas en la conexion API ")
        return redirect(url_for('index'))

    status = r["status"]
    # VARIABLES SESSION -.---------)
    if status == 0:

        token = r["data"]["token"]
        cliente_usuario_id = r["data"]["cliente_usuario_id"]

        # VARIABLES SESSION -.---------
        session['cliente_usuario_id'] = cliente_usuario_id
        session['token'] = token
        return redirect(url_for('inicio'))
    else:
        flash("Usuario y/o Clave son invalidos", "danger")
        return redirect(url_for('index'))


@app.route('/inicio')
def inicio():

    if len(session) == 0:
        return redirect(url_for('index'))

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    cursor = consulta_inicial.select_inicio()
    if cursor == False:

        flash("No hay conexion a la BD", "danger")
        return redirect(url_for('index'))

    cursor_host = consulta_host.select_consultar_host()
    host_name = cursor_host.fetchall()

    # PERFIL
    cursor_perfil = consulta_perfil.select_perfil()
    perfil_name = cursor_perfil.fetchall()
    session["perfil_nombre"] = perfil_name

    cursor1 = consulta_user_compania.select_user_compania()
    cliente_usuario = cursor1.fetchall()
    session["usr_api"] = (cliente_usuario)
    usuario = session["usr_api"][0][0]
    cliente = session["usr_api"][0][1]

    newList = []
    for datas in cursor:
        newMonitor = '('
        for monitor in datas[3]:
            nameMonitor = clientMonitor.dataMonitor(monitor)[0][0]
            newMonitor += str(monitor) + '-' + str(nameMonitor) + ","
        newMonitor = newMonitor[:-1]
        newMonitor += ')'
        _query = clientMonitor.selectClientMonitor(datas[3])

        clientList = []
        for dato in _query:
            clientList.append(
                {"objetivo": dato[0], "nombre_cliente": dato[1], "estado": dato[2]})

        clientsDown = [x for x in clientList if x["estado"] == True]
        clientList = map(lambda x: x["nombre_cliente"], clientList)
        clientList = str(clientList)[1:-1]

        if len(clientsDown) != 0:
            clientList = 'Todos'
        dictData = {}
        dictData["status"] = datas[0]
        dictData["beginDate"] = datas[1]
        dictData["solutionDate"] = datas[2]
        dictData["fechAvisoCli"] = datas[4]
        dictData["monitor"] = newMonitor
        dictData["clients"] = clientList
        dictData['qcliente'] = len(str(clientList).split(','))
        dictData["problem"] = datas[5]
        dictData["generateProblem"] = datas[6]
        dictData["solution"] = datas[7]
        dictData["culpable"] = datas[8]
        dictData["id"] = datas[9]
        newList.append(dictData)

    if session["perfil_nombre"][0][0] == 'administrador' and session["perfil_nombre"][0][1] == 'si':
        return render_template("template_admin.html", data=newList, usuario=usuario, compania=cliente, host_name=host_name)
    elif session["perfil_nombre"][0][0] == 'lectura' and session["perfil_nombre"][0][1] == 'si':
        return render_template("template_noEdit.html", data=newList, usuario=usuario, compania=cliente, host_name=host_name)
    elif session["perfil_nombre"][0][0] == 'escritura' and session["perfil_nombre"][0][1] == 'si':
        return render_template("template.html", data=newList, usuario=usuario, compania=cliente, host_name=host_name)
    elif session["perfil_nombre"][0][1] == 'no':
        flash("NO TIENE PERFIL ACTIVO", "danger")
        return redirect(url_for('index'))



@app.route("/consultar", methods=["GET", "POST"])
def consultar():

    from operator import itemgetter

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    fecha = request.form['fecha']
    fecha_inicial_1 = fecha.split(" ")[0]
    fecha_inicial_2 = fecha.split(" ")[2]
    fecha_inicial_1 = datetime.strptime(str(fecha_inicial_1), '%d/%m/%Y')
    fecha_inicial_2 = datetime.strptime(str(fecha_inicial_2), '%d/%m/%Y')

    cursor = consulta_busqueda.select_consultar(
        fecha_inicial_1, fecha_inicial_2)
    data = cursor.fetchall()
    cursor_host = consulta_host.select_consultar_host()
    host_name = cursor_host.fetchall()

    cursor3 = consulta_user_compania.select_user_compania()
    cliente_usuario = cursor3.fetchall()
    nombre = cliente_usuario[0][0]
    cliente = cliente_usuario[0][1]
    newList = []
    for datas in data:
        newMonitor = '('
        for monitor in datas[4]:
            nameMonitor = clientMonitor.dataMonitor(monitor)[0][0]
            newMonitor += str(monitor) + '-' + str(nameMonitor) + ","
        newMonitor = newMonitor[:-1]
        newMonitor += ')'
        _query = clientMonitor.selectClientMonitor(datas[4])
        clientList = []
        for dato in _query:
            clientList.append(
                {"objetivo": dato[0], "nombre_cliente": dato[1], "estado": dato[2]})

        clientsDown = [x for x in clientList if x["estado"] == True]
        clientList = map(lambda x: x["nombre_cliente"], clientList)
        clientList = str(clientList)[1:-1]

        if len(clientsDown) != 0:
            clientList = 'Todos'
        dictData = {}
        dictData["status"] = datas[0]
        dictData["beginDate"] = datas[1]
        dictData["solutionDate"] = datas[2]
        dictData["fechAvisoCli"] = datas[3]
        dictData["monitor"] = newMonitor
        dictData["clients"] = clientList
        dictData['qcliente'] = len(str(clientList).split(','))
        dictData["problem"] = datas[5]
        dictData["generateProblem"] = datas[6]
        dictData["solution"] = datas[7]
        dictData["culpable"] = datas[8]
        dictData["id"] = datas[9]
        newList.append(dictData)

    if session["perfil_nombre"][0][0] == 'administrador':
        return render_template("template_admin.html", data=newList, ayer=fecha, usuario=nombre, compania=cliente, host_name=host_name)
    elif session["perfil_nombre"][0][0] == 'lectura':
        return render_template("template_noEdit.html", data=newList, ayer=fecha, usuario=nombre, compania=cliente, host_name=host_name)
    elif session["perfil_nombre"][0][0] == 'escritura':
        return render_template("template.html", data=newList, ayer=fecha, usuario=nombre, compania=cliente, host_name=host_name)



@app.route("/actualizar", methods=['POST'])
def actualizar():

    variable = session_token(session)

    if variable == 'False':
        return render_template("login.html")

    id = request.form['id']
    fecha_solucion = request.form['fecha_solucion']
    fecha_aviso_clientes = request.form['fecha_aviso_clientes']
    problema = request.form['problema']
    problema_genera = request.form['problema_genera']
    solucion = request.form['solucion']
    culpable = request.form['culpable']
    estado = request.form['estado']

    cursor = actualiza_registro.update_registro(
        id, fecha_solucion, fecha_aviso_clientes, problema, problema_genera, solucion, culpable, estado)

    return redirect(url_for('inicio'))


@app.route("/insertar", methods=['POST'])
def insertar():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    estado = 't'
    fecha_inicio_evento = request.form['fecha_inicio_evento']
    monitor_hostname = request.form.getlist('monitor_hostname')

    monitor_hostname_final = ""
    for elem in monitor_hostname:

        monitor_hostname_final2 = (str(elem).split("-")[0])
        monitor_hostname_final = monitor_hostname_final + "," + monitor_hostname_final2
        monitor = "{" + monitor_hostname_final[1:210] + "}"

    problema = request.form['problema']
    culpable = request.form['culpable']
    fecha_solucion = request.form['fecha_solucion']
    fecha_aviso_clientes = request.form['fecha_aviso_clientes']
    problema_genera = request.form['problema_genera']
    solucion = request.form['solucion']

    cursor = insertar_registro.insert(estado, fecha_inicio_evento, monitor, problema,
                                      culpable, fecha_solucion, fecha_aviso_clientes, problema_genera, solucion)

    return redirect(url_for('inicio'))


@app.route("/mantenedor", methods=["GET", "POST"])
def mantenedor():

    if len(session) == 0:
        return redirect(url_for('index'))

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    cursor3 = consulta_user_compania.select_user_compania()
    cliente_usuario = cursor3.fetchall()
    nombre = cliente_usuario[0][0]
    cliente = cliente_usuario[0][1]

    cursor_user = consulta_user.select_user()
    user_add = cursor_user.fetchall()

    cursor_user_perfil = consulta_user_perfiles.select_user_perfil()
    user_show = cursor_user_perfil.fetchall()

    return render_template("mantenedor.html", usuario=nombre, compania=cliente, usuario_add=user_add, mostrar_user=user_show)


@app.route("/insertar_perfil", methods=['POST'])
def insertar_perfil():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    usr_perfil = request.form.getlist('usr_perfil')
    listUsr=[]
    for elem in usr_perfil:
        dictUsr={}
        dictUsr["id_usuario_perfil"] = (str(elem).split("-")[0])
        dictUsr["nombre_usuario_perfil"] = (str(elem).split("-")[1])
        listUsr.append(dictUsr)

    perfil_usr_add = request.form['perfil_usr_add']
    activo_usr_add = request.form['activo_usr_add']

    cursor = insertar_registro_perfil.insert_perfil(listUsr,perfil_usr_add,activo_usr_add)
    if cursor != False:
        cursor2 = actualizar_public_cliente.update_public_cliente(listUsr)
        cursor3 = actualizar_rtrim.update_rtrim()

    return redirect(url_for('mantenedor'))


@app.route("/actualizar_perfil", methods=['POST'])
def actualizar_perfil():

    variable = session_token(session)
    if variable == 'False':
        return render_template("login.html")

    nombre_perfil = request.form['nombre_perfil']
    activo = request.form['activo']
    id_perfil_usuario = request.form['id_perfil_usuario']

    cursor = actualiza_perfil.update_perfil(nombre_perfil,activo,id_perfil_usuario)

    return redirect(url_for('mantenedor'))


if(__name__ == "__main__"):
    #app.run(debug = True)
    app.run("0.0.0.0", 5000)
