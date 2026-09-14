from enum import StrEnum


class Rol(StrEnum):
    """Catálogo cerrado de roles del PG09 §1.1."""

    DETECTOR = "DETECTOR"
    JEFE_CLD = "JEFE_CLD"
    TECNICO_CLD = "TECNICO_CLD"
    RESPONSABLE_RESOLUCION = "RESPONSABLE_RESOLUCION"
    EJECUTOR = "EJECUTOR"
    RSGI = "RSGI"
