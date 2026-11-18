
import logging
from abc import ABC, abstractmethod
from datetime import datetime


# CONFIGURACION DEL REGISTRO DE EVENTOS Y ERRORES
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# EXCEPCIONES PERSONALIZADAS
class ErrorSistema(Exception):
    """Excepcion general del sistema."""


class DatosInvalidosError(ErrorSistema):
    """Datos ingresados incorrectamente."""


class ServicioNoDisponibleError(ErrorSistema):
    """Servicio no disponible."""


class ReservaError(ErrorSistema):
    """Error relacionado con una reserva."""


# CLASE ABSTRACTA GENERAL
class Entidad(ABC):

    def __init__(self, identificador):
        if not identificador:
            raise DatosInvalidosError("El identificador es obligatorio.")
        self._identificador = identificador

    @abstractmethod
    def describir(self):
        pass


# CLASE CLIENTE
class Cliente(Entidad):

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        if not nombre.strip():
            raise DatosInvalidosError("El nombre no puede estar vacio.")

        if "@" not in correo or "." not in correo:
            raise DatosInvalidosError("El correo no es valido.")

        if not telefono.isdigit() or len(telefono) < 7:
            raise DatosInvalidosError("El telefono no es valido.")

        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono

    def describir(self):
        return f"Cliente: {self.__nombre} | Correo: {self.__correo}"

    @property
    def nombre(self):
        return self.__nombre


# CLASE ABSTRACTA SERVICIO
class Servicio(Entidad, ABC):

    def __init__(self, identificador, nombre, precio_base):
        super().__init__(identificador)

        if precio_base <= 0:
            raise DatosInvalidosError("El precio debe ser mayor que cero.")

        self.nombre = nombre
        self.precio_base = precio_base
        self.disponible = True

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def describir(self):
        pass

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass


# SERVICIO 1: RESERVA DE SALAS
class ServicioSala(Servicio):

    def validar_parametros(self, duracion):
        if duracion <= 0:
            raise DatosInvalidosError("La duracion de la sala debe ser positiva.")

    def describir(self):
        return f"Reserva de sala: {self.nombre}"

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.precio_base * duracion
        return subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)


# SERVICIO 2: ALQUILER DE EQUIPOS
class ServicioEquipo(Servicio):

    def validar_parametros(self, duracion):
        if duracion <= 0:
            raise DatosInvalidosError("La duracion del alquiler debe ser positiva.")

    def describir(self):
        return f"Alquiler de equipo: {self.nombre}"

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.precio_base * duracion
        return subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)


# SERVICIO 3: ASESORIAS ESPECIALIZADAS
class ServicioAsesoria(Servicio):

    def validar_parametros(self, duracion):
        if duracion <= 0:
            raise DatosInvalidosError("La duracion de la asesoria debe ser positiva.")

    def describir(self):
        return f"Asesoria especializada: {self.nombre}"

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.precio_base * duracion
        return subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)


# CLASE RESERVA
class Reserva(Entidad):

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("Debe ingresar un cliente valido.")

        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Debe ingresar un servicio valido.")

        servicio.validar_parametros(duracion)

        if not servicio.disponible:
            raise ServicioNoDisponibleError("El servicio no esta disponible.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha = datetime.now()

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaError("Solo se pueden confirmar reservas pendientes.")

        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self._identificador)
        return "Reserva confirmada correctamente."

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaError("La reserva ya esta cancelada.")

        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self._identificador)
        return "Reserva cancelada correctamente."

    def procesar(self, impuesto=0, descuento=0):
        try:
            if self.estado != "Confirmada":
                raise ReservaError("La reserva debe estar confirmada.")

            costo = self.servicio.calcular_costo(
                self.duracion, impuesto, descuento
            )
            return costo

        except ErrorSistema as error:
            logging.error("Error al procesar reserva: %s", error)
            raise

        finally:
            logging.info("Finalizo el procesamiento de la reserva.")

    def describir(self):
        return (
            f"Reserva {self._identificador} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Estado: {self.estado}"
        )


# GESTOR DEL SISTEMA
class GestorSoftwareFJ:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto no es un cliente valido.")

        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.nombre)
        return "Cliente registrado correctamente."

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El servicio no es valido.")

        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s", servicio.nombre)
        return "Servicio registrado correctamente."

    def crear_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ReservaError("La reserva no es valida.")

        self.reservas.append(reserva)
        logging.info("Reserva creada: %s", reserva._identificador)
        return "Reserva creada correctamente."


# FUNCION PARA EJECUTAR PRUEBAS
def ejecutar_operacion(numero, descripcion, funcion):
    print(f"\nOPERACION {numero}: {descripcion}")

    try:
        resultado = funcion()
        print("RESULTADO:", resultado)
        logging.info("Operacion %s ejecutada correctamente.", numero)

    except ErrorSistema as error:
        print("ERROR CONTROLADO:", error)
        logging.error("Operacion %s: %s", numero, error)

    except Exception as error:
        print("ERROR INESPERADO:", error)
        logging.exception("Error inesperado en operacion %s.", numero)


# PROGRAMA PRINCIPAL
def main():

    print("=" * 55)
    print("       SISTEMA INTEGRAL DE GESTION SOFTWARE FJ")
    print("=" * 55)

    gestor = GestorSoftwareFJ()

    # OPERACION 1: REGISTRO VALIDO DE CLIENTE
    cliente1 = Cliente("C001", "Carlos Perez", "carlos@gmail.com", "3001234567")
    ejecutar_operacion(
        1, "Registro valido de cliente",
        lambda: gestor.registrar_cliente(cliente1)
    )

    # OPERACION 2: REGISTRO INVALIDO DE CLIENTE
    ejecutar_operacion(
        2, "Registro de cliente con correo incorrecto",
        lambda: Cliente("C002", "Ana Lopez", "correo_invalido", "3001234567")
    )

    # OPERACION 3: CREACION DE SERVICIO DE SALA
    sala = ServicioSala("S001", "Sala de reuniones", 50000)
    ejecutar_operacion(
        3, "Creacion de servicio de sala",
        lambda: gestor.registrar_servicio(sala)
    )

    # OPERACION 4: CREACION DE SERVICIO DE EQUIPO
    equipo = ServicioEquipo("S002", "Computador portatil", 30000)
    ejecutar_operacion(
        4, "Creacion de servicio de alquiler de equipos",
        lambda: gestor.registrar_servicio(equipo)
    )

    # OPERACION 5: CREACION DE SERVICIO DE ASESORIA
    asesoria = ServicioAsesoria("S003", "Asesoria de software", 80000)
    ejecutar_operacion(
        5, "Creacion de servicio de asesoria",
        lambda: gestor.registrar_servicio(asesoria)
    )

    # OPERACION 6: CREACION DE SERVICIO INVALIDO
    ejecutar_operacion(
        6, "Creacion de servicio con precio negativo",
        lambda: ServicioSala("S004", "Sala invalida", -100)
    )

    # OPERACION 7: CREACION DE RESERVA
    reserva1 = Reserva("R001", cliente1, sala, 2)
    ejecutar_operacion(
        7, "Creacion de reserva",
        lambda: gestor.crear_reserva(reserva1)
    )

    # OPERACION 8: CONFIRMACION DE RESERVA
    ejecutar_operacion(
        8, "Confirmacion de reserva",
        lambda: reserva1.confirmar()
    )

    # OPERACION 9: PROCESAMIENTO Y CALCULO DEL COSTO
    ejecutar_operacion(
        9, "Procesamiento de reserva con impuesto y descuento",
        lambda: f"Costo total: ${reserva1.procesar(19, 10):,.2f}"
    )

    # OPERACION 10: INTENTO DE CANCELACION Y REPROCESAMIENTO
    def cancelar_y_procesar():
        reserva1.cancelar()
        return reserva1.procesar()

    ejecutar_operacion(
        10, "Intento de procesar una reserva cancelada",
        cancelar_y_procesar
    )

    print("\n" + "=" * 55)
    print("RESUMEN DEL SISTEMA")
    print("=" * 55)
    print("Clientes registrados:", len(gestor.clientes))
    print("Servicios registrados:", len(gestor.servicios))
    print("Reservas registradas:", len(gestor.reservas))
    print("Archivo de eventos y errores: software_fj.log")
    print("\nEJECUCION FINALIZADA. EL SISTEMA SIGUE ACTIVO.")


if __name__ == "__main__":
    main()
