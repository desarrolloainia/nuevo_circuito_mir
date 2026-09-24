class MirPersistenceError(Exception):
    pass


class MirNoEncontradaError(MirPersistenceError):
    pass


class DocumentoNoEncontradoError(MirPersistenceError):
    pass


class DocumentoYaAsignadoError(MirPersistenceError):
    pass


class EstadoInvalidoError(MirPersistenceError):
    pass


class DatoObligatorioFaltanteError(Exception):
    """Falta un dato que la MIR exige (descripcion o datos de solucion)."""


class ActorNoAutorizadoError(Exception):
    """Quien dispara la transicion no tiene permiso para hacerlo."""
