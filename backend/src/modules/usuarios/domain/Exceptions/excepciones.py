class CorreoYaRegistradoError(Exception):
    """Se intenta registrar un usuario con un correo ya existente (FR-003)."""


class RolInvalidoError(Exception):
    """El rol indicado no pertenece al catálogo cerrado del PG09 (FR-004)."""


class FormatoCorreoInvalidoError(Exception):
    """El correo no tiene un formato válido (FR-002)."""


class DatoObligatorioFaltanteError(Exception):
    """Falta correo, rol o departamento (FR-005)."""


class UsuarioNoEncontradoError(Exception):
    """No existe ningún usuario con el correo indicado."""


class UsuarioInactivoError(Exception):
    """Se intenta actualizar un usuario dado de baja (FR-011)."""
