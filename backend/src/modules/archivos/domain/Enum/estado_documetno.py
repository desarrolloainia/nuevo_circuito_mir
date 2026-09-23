from enum import Enum


class TipoDocumento(str, Enum):
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    IMAGEN = "imagen"
    OTRO = "otro"
