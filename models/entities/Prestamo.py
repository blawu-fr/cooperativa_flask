class Prestamo:
    def __init__(self, id, usuario_id, monto, tasa_interes, plazo, fecha_prestamo, fecha_pago_prestamo, tipo_cuenta):
        self.id = id
        self.usuario_id = usuario_id
        self.monto = monto
        self.tasa_interes = tasa_interes
        self.plazo = plazo
        self.fecha_prestamo = fecha_prestamo
        self.fecha_pago_prestamo = fecha_pago_prestamo
        self.tipo_cuenta = tipo_cuenta
