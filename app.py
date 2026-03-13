from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask_migrate import Migrate
from datetime import datetime
import forms
from models import db, Cliente, Pedido, Pizza, DetallePedido

app = Flask(__name__)
app.secret_key = "examen_pizzas"
csrf = CSRFProtect(app)
app.config.from_object(DevelopmentConfig)

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/", methods=["GET", "POST"])
def pizza():
    form = forms.PizzaForm()
    
    if 'pedido_temporal' not in session:
        session['pedido_temporal'] = []

    if request.method == 'GET' and 'cliente_temp' in session:
        form.nombre.data = session['cliente_temp'].get('nombre')
        form.direccion.data = session['cliente_temp'].get('direccion')
        form.telefono.data = session['cliente_temp'].get('telefono')
        if 'fecha' in session['cliente_temp']:
            try:
                form.fecha.data = datetime.strptime(session['cliente_temp']['fecha'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

    hoy = datetime.utcnow().date()
    ventas_hoy = Pedido.query.filter_by(fecha=hoy).all()
    total_ventas_hoy = sum(v.total for v in ventas_hoy)

    if form.validate_on_submit():
        if 'agregar' in request.form:
            precio_tamano = int(form.tamano.data)
            ingredientes_labels = []
            costo_ingredientes = 0

            for i in form.ingredientes.data:
                costo, nombre = i.split('_')
                costo_ingredientes += int(costo)
                ingredientes_labels.append(nombre)

            total_u = precio_tamano + costo_ingredientes
            subtotal = total_u * form.cantidad.data

            pizza_temp = {
                "id_temp": len(session['pedido_temporal']) + 1,
                "tamano_valor": form.tamano.data,
                "tamano_label": dict(form.tamano.choices).get(form.tamano.data),
                "ingredientes_raw": form.ingredientes.data,
                "ingredientes": ", ".join(ingredientes_labels) if ingredientes_labels else "Ninguno",
                "cantidad": form.cantidad.data,
                "subtotal": subtotal,
                "precio_unitario": total_u
            }
            
            temp_list = session['pedido_temporal']
            temp_list.append(pizza_temp)
            session['pedido_temporal'] = temp_list
            
            session['cliente_temp'] = {
                "nombre": form.nombre.data,
                "direccion": form.direccion.data,
                "telefono": form.telefono.data,
                "fecha": form.fecha.data.strftime('%Y-%m-%d') if form.fecha.data else datetime.utcnow().strftime('%Y-%m-%d')
            }

            return redirect(url_for('pizza'))

    return render_template("index.html", 
                           form=form, 
                           pedido_temporal=session.get('pedido_temporal', []), 
                           cliente_temp=session.get('cliente_temp', {}),
                           ventas_hoy=ventas_hoy,
                           total_ventas_hoy=total_ventas_hoy)
    
@app.route("/quitar", methods=["POST"])
def quitar_pizza():
    id_temp = request.form.get('id_temp', type=int)
    
    if id_temp and 'pedido_temporal' in session:
        temp_list = session['pedido_temporal']
        session['pedido_temporal'] = [p for p in temp_list if p['id_temp'] != id_temp]
        
    return redirect(url_for('pizza'))

@app.route("/terminar", methods=["POST"])
def terminar_pedido():
    pedido_temporal = session.get('pedido_temporal', [])
    cliente_temp = session.get('cliente_temp', {})

    if not pedido_temporal or not cliente_temp:
        return redirect(url_for('pizza'))

    total_pedido = sum(p['subtotal'] for p in pedido_temporal)

    try:
        cliente = Cliente.query.filter_by(telefono=cliente_temp['telefono']).first()
        if not cliente:
            cliente = Cliente(
                nombre=cliente_temp['nombre'],
                direccion=cliente_temp['direccion'],
                telefono=cliente_temp['telefono']
            )
            db.session.add(cliente)
            db.session.flush() 

        fecha_str = cliente_temp.get('fecha')
        fecha_pedido = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else datetime.utcnow().date()

        nuevo_pedido = Pedido(
            id_cliente=cliente.id_cliente,
            fecha=fecha_pedido, 
            total=total_pedido
        )
        db.session.add(nuevo_pedido)
        db.session.flush()

        for p_temp in pedido_temporal:
            nueva_pizza = Pizza(
                tamano=p_temp['tamano_label'],
                ingredientes=p_temp['ingredientes'],
                precio=p_temp['precio_unitario']
            )
            db.session.add(nueva_pizza)
            db.session.flush()

            detalle = DetallePedido(
                id_pedido=nuevo_pedido.id_pedido,
                id_pizza=nueva_pizza.id_pizza,
                cantidad=p_temp['cantidad'],
                subtotal=p_temp['subtotal']
            )
            db.session.add(detalle)

        db.session.commit()
        
        session.pop('pedido_temporal', None)
        session.pop('cliente_temp', None)
        
    except Exception as e:
        db.session.rollback()

    return redirect(url_for('pizza'))

@app.route("/reportes", methods=["GET", "POST"])
def reportes():
    form = forms.ReporteForm()
    pedidos_filtrados = []
    total_acumulado = 0
    
    if request.method == "POST":
        todos_los_pedidos = Pedido.query.all()
        
        if form.tipo_filtro.data == 'dia':
            dia_seleccionado = int(form.dia.data)
            pedidos_filtrados = [p for p in todos_los_pedidos if p.fecha.weekday() == dia_seleccionado]
            
        elif form.tipo_filtro.data == 'mes':
            mes_seleccionado = int(form.mes.data)
            pedidos_filtrados = [p for p in todos_los_pedidos if p.fecha.month == mes_seleccionado]
        
        total_acumulado = sum(p.total for p in pedidos_filtrados)
        
    return render_template("reportes.html", form=form, pedidos=pedidos_filtrados, total_acumulado=total_acumulado)

@app.route("/detalle/<int:id_pedido>")
def detalle_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    return render_template("detalle.html", pedido=pedido)

if __name__ == "__main__":
    app.run(debug=True)