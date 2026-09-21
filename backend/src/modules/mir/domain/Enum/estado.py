from enum import StrEnum


class Estado(StrEnum):
    """Enum que represneta los distintos estados de un MIR."""

    EN_REVISION = "EN_REVISION"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"
    RECHAZADA = "RECHAZADA"
    TERMINADA = "TERMINADA"
