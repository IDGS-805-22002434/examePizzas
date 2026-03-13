from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True) 
    nombre = db.Column(db.String(100), nullable=False) 
    direccion = db.Column(db.String(200), nullable=False) 
    telefono = db.Column(db.String(20), nullable=False) 
    
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id_pizza = db.Column(db.Integer, primary_key=True) 
    tamano = db.Column(db.String(20), nullable=False) 
    ingredientes = db.Column(db.String(200)) 
    precio = db.Column(db.Numeric(8, 2), nullable=False) 
    
    detalles = db.relationship('DetallePedido', backref='pizza', lazy=True)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id_pedido = db.Column(db.Integer, primary_key=True) 
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False) 
    fecha = db.Column(db.Date, default=datetime.utcnow) 
    total = db.Column(db.Numeric(10, 2), nullable=False) 
    
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id_detalle = db.Column(db.Integer, primary_key=True) 
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False) 
    id_pizza = db.Column(db.Integer, db.ForeignKey('pizzas.id_pizza'), nullable=False) 
    cantidad = db.Column(db.Integer, nullable=False) 
    subtotal = db.Column(db.Numeric(10, 2), nullable=False) 