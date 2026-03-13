from flask_wtf import FlaskForm
from wtforms import SelectField, RadioField
from wtforms import StringField, IntegerField, RadioField, SelectMultipleField, widgets, DateField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PizzaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="Campo requerido")])
    direccion = StringField('Dirección', validators=[DataRequired(message="Campo requerido")])
    telefono = StringField('Teléfono', validators=[DataRequired(message="Campo requerido")])
    fecha = DateField('Fecha de compra', format='%Y-%m-%d', validators=[DataRequired(message="Fecha necesaria")])
    
    tamano = RadioField('Tamaño Pizza', choices=[
        ('40', 'Chica $40'), 
        ('80', 'Mediana $80'), 
        ('120', 'Grande $120')
    ], validators=[DataRequired()])
    
    ingredientes = MultiCheckboxField('Ingredientes', choices=[
        ('10_Jamon', 'Jamón $10'), 
        ('10_Piña', 'Piña $10'), 
        ('10_Champiñones', 'Champiñones $10')
    ])
    
    cantidad = IntegerField('Num. de Pizzas', default=1, validators=[DataRequired()])
    

class ReporteForm(FlaskForm):
    tipo_filtro = RadioField('Filtrar por:', choices=[
        ('dia', 'Día de la semana'), 
        ('mes', 'Mes del año')
    ], default='dia')
    
    dia = SelectField('Día de la semana', choices=[
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ])
    
    mes = SelectField('Mes', choices=[
        ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
        ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
        ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ])