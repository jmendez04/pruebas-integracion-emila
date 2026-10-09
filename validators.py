
from datetime import datetime


class ErrorValidacion(Exception):
    def __init__(self, errores):
        super().__init__("Los datos no son validos.")
        self.errores = errores


def validar_texto(datos, campo, errores, maximo=150, obligatorio=True):
    valor = datos.get(campo)

    if valor is None or valor == "":
        if obligatorio:
            errores[campo] = f"El campo '{campo}' es obligatorio."
        return ""

    if not isinstance(valor, str):
        errores[campo] = f"El campo '{campo}' debe ser texto."
        return None

    valor = valor.strip()

    if not valor:
        if obligatorio:
            errores[campo] = f"El campo '{campo}' es obligatorio."
        return ""

    if len(valor) > maximo:
        errores[campo] = (
            f"El campo '{campo}' no puede superar "
            f"{maximo} caracteres."
        )
        return None

    return valor


def validar_fecha(datos, campo, errores):
    valor = datos.get(campo)

    if not isinstance(valor, str) or not valor.strip():
        errores[campo] = f"El campo '{campo}' es obligatorio."
        return None

    try:
        texto = valor.strip()

        if "T" not in texto:
            raise ValueError("Formato incorrecto")

        fecha = datetime.fromisoformat(
            texto.replace("Z", "+00:00")
        )

        if fecha.utcoffset() is None:
            raise ValueError("Falta zona horaria")

        return fecha

    except ValueError:
        errores[campo] = (
            "La fecha debe tener el formato "
            "YYYY-MM-DDTHH:MM:SS-06:00."
        )
        return None


# -----------------------------------------
# VALIDACION POST - CREAR ENTREGA
# -----------------------------------------

def validar_entrega(datos):
    if not isinstance(datos, dict):
        raise ErrorValidacion({
            "json": "Debes enviar un objeto JSON valido."
        })

    errores = {}

    pedido_id = validar_texto(
        datos, "pedido_id", errores, maximo=50
    )

    cliente = validar_texto(
        datos, "cliente", errores, maximo=150
    )

    direccion = validar_texto(
        datos, "direccion", errores, maximo=250
    )

    observaciones = validar_texto(
        datos,
        "observaciones",
        errores,
        maximo=500,
        obligatorio=False
    )

    inicio = validar_fecha(datos, "inicio", errores)
    fin = validar_fecha(datos, "fin", errores)

    if inicio is not None and fin is not None:
        if fin <= inicio:
            errores["fin"] = (
                "La fecha de finalizacion debe ser "
                "posterior a la fecha de inicio."
            )

    if errores:
        raise ErrorValidacion(errores)

    return {
        "pedido_id": pedido_id,
        "cliente": cliente,
        "direccion": direccion,
        "inicio": inicio.isoformat(timespec="seconds"),
        "fin": fin.isoformat(timespec="seconds"),
        "observaciones": observaciones,
    }


# -----------------------------------------
# VALIDACION PATCH - MODIFICAR HORARIO
# -----------------------------------------

def validar_actualizacion_horario(datos):
    if not isinstance(datos, dict):
        raise ErrorValidacion({
            "json": "Debes enviar un objeto JSON valido."
        })

    errores = {}

    inicio = validar_fecha(datos, "inicio", errores)
    fin = validar_fecha(datos, "fin", errores)

    if inicio is not None and fin is not None:
        if fin <= inicio:
            errores["fin"] = (
                "La fecha de finalizacion debe ser "
                "posterior a la fecha de inicio."
            )

    if errores:
        raise ErrorValidacion(errores)

    return {
        "inicio": inicio.isoformat(timespec="seconds"),
        "fin": fin.isoformat(timespec="seconds")
    }
