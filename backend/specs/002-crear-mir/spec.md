# Feature Specification: Registro inicial de MIR

**Feature Branch**: `sin-rama-nueva`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Crear el modulo MIR comenzando solo por el registro. Una MIR puede haberse solucionado previamente o no; si ya esta solucionada, solucion adoptada, analisis de causas y algo mas que hacer son obligatorios. Debe incluir fecha de deteccion, codigo anual secuencial y adjuntos cargados antes de crear la MIR."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar una MIR no solucionada (Priority: P1)

Un detector registra una mejora, incidencia o reclamacion que todavia no esta
solucionada, indicando que sucedio, cuando se detecto y quien lo detecto. La
MIR queda identificada y preparada para que CLD la revise posteriormente.

**Why this priority**: Es el caso basico que inicia el procedimiento PG09 y
permite sustituir el registro manual sin implementar todavia las etapas
posteriores.

**Independent Test**: Se registra una MIR no solucionada con sus datos
obligatorios y se comprueba que queda guardada en revision con un codigo unico,
sin exigir informacion sobre una solucion inexistente.

**Acceptance Scenarios**:

1. **Given** un detector existente y los datos obligatorios validos, **When**
   registra una MIR como no solucionada, **Then** la MIR queda creada en estado
   `EN_REVISION`, con `solucionado` a falso y sin datos de solucion.
2. **Given** una MIR marcada como no solucionada, **When** se incluyen valores
   en los campos propios de una MIR ya solucionada, **Then** esos valores no se
   conservan y la MIR queda registrada sin datos de solucion.
3. **Given** una fecha de deteccion futura, una descripcion vacia, un tipo no
   permitido o un detector inexistente, **When** se intenta registrar la MIR,
   **Then** el registro se rechaza indicando todos los datos invalidos.

---

### User Story 2 - Registrar una MIR ya solucionada (Priority: P1)

Un detector registra una MIR que ya fue solucionada antes de introducirla en
el sistema y documenta obligatoriamente la solucion adoptada, el analisis de
causas y si queda algo mas que hacer.

**Why this priority**: El PG09 contempla que una MIR pueda llegar resuelta al
registro; perder estos datos impediria evaluar posteriormente la actuacion
realizada.

**Independent Test**: Se registra una MIR marcada como solucionada con los tres
datos especificos completos y se comprueba que quedan asociados a la MIR.

**Acceptance Scenarios**:

1. **Given** los datos generales validos y los tres datos de solucion
   cumplimentados, **When** se registra la MIR como solucionada, **Then** queda
   creada en `EN_REVISION` y conserva la solucion adoptada, el analisis de
   causas y la indicacion de si queda algo mas que hacer.
2. **Given** una MIR marcada como solucionada, **When** falta cualquiera de los
   tres datos de solucion o contiene solo espacios, **Then** el registro se
   rechaza e identifica cada dato ausente.

---

### User Story 3 - Registrar una reclamacion (Priority: P1)

Cuando el hecho registrado es una reclamacion, el detector identifica tambien
a la persona reclamante y su empresa para que ninguna reclamacion quede sin la
informacion minima exigida por el PG09.

**Why this priority**: La identificacion del reclamante es obligatoria para
gestionar y responder posteriormente la reclamacion.

**Independent Test**: Se registra una reclamacion con persona y empresa, y se
comprueba que una reclamacion sin cualquiera de esos datos es rechazada.

**Acceptance Scenarios**:

1. **Given** una MIR de tipo Reclamacion con nombre de reclamante y empresa,
   **When** se registra, **Then** ambos datos quedan asociados a la MIR.
2. **Given** una MIR de tipo Reclamacion sin nombre de reclamante o sin empresa,
   **When** se intenta registrar, **Then** el registro se rechaza indicando el
   dato que falta.
3. **Given** una MIR de tipo Mejora o Incidencia, **When** se registra, **Then**
   no se exigen datos de reclamante.

---

### User Story 4 - Registrar una MIR con adjuntos (Priority: P2)

Un detector carga primero hasta diez documentos relacionados con el hecho y,
una vez disponibles, registra la MIR vinculandolos sin tener que esperar de
nuevo por su almacenamiento.

**Why this priority**: Los adjuntos aportan evidencias utiles, pero una MIR sin
adjuntos ya permite realizar el registro basico.

**Independent Test**: Se cargan uno o varios documentos validos, se registra la
MIR usando sus referencias y se comprueba que todos quedan vinculados una sola
vez.

**Acceptance Scenarios**:

1. **Given** entre uno y diez documentos cargados correctamente y todavia no
   vinculados, **When** se registra la MIR con sus referencias, **Then** la MIR
   queda creada con todos los documentos asociados.
2. **Given** que falla el registro despues de cargar los documentos, **When** el
   detector corrige el problema y reintenta, **Then** puede reutilizar los
   documentos ya cargados sin volver a cargarlos.
3. **Given** una referencia inexistente, no disponible, repetida o ya vinculada
   a otra MIR, **When** se intenta registrar la MIR, **Then** no se crea la MIR
   ni se vincula parcialmente ningun documento.

### Edge Cases

- Dos o mas altas simultaneas del mismo ano reciben codigos distintos y
  consecutivos, sin duplicados.
- La primera MIR registrada en un ano recibe la secuencia `001`, aunque la MIR
  anterior pertenezca al ano previo.
- La secuencia usa un minimo de tres posiciones y puede crecer sin perder el
  prefijo anual cuando supera `999`.
- La fecha de deteccion puede ser anterior a la fecha de registro, pero nunca
  posterior al dia del registro.
- Los textos obligatorios que contienen solo espacios se consideran ausentes.
- Una lista con la misma referencia documental mas de una vez se rechaza.
- Once o mas adjuntos, o un archivo mayor de 25 MB, se rechazan antes de crear
  la MIR.
- Si falla una de varias cargas, la MIR no se crea hasta que todos los adjuntos
  seleccionados esten disponibles o el detector retire los fallidos.
- Si el registro de la MIR falla, los documentos ya cargados se conservan sin
  vincular para permitir un reintento.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir registrar una MIR indicando tipo,
  descripcion, fecha de deteccion, detector y si ya estaba solucionada.
- **FR-002**: El tipo inicial DEBE limitarse a Mejora, Incidencia o Reclamacion.
- **FR-003**: El sistema DEBE comprobar que el detector existe antes de
  registrar la MIR.
- **FR-004**: La fecha de deteccion DEBE ser obligatoria y no puede ser futura.
- **FR-005**: La descripcion DEBE ser obligatoria, no vacia y relatar el hecho
  detectado.
- **FR-006**: Toda MIR nueva DEBE quedar en estado `EN_REVISION`, con
  independencia de si ya estaba solucionada antes del registro.
- **FR-007**: Cuando `solucionado` sea verdadero, solucion adoptada, analisis de
  causas y algo mas que hacer DEBEN ser obligatorios y no pueden estar vacios.
- **FR-008**: Cuando `solucionado` sea falso, los tres datos de solucion NO
  DEBEN ser obligatorios ni conservarse aunque se hayan proporcionado.
- **FR-009**: Una Reclamacion DEBE incluir el nombre de la persona reclamante y
  su empresa; esos datos NO DEBEN exigirse para Mejora o Incidencia.
- **FR-010**: El sistema DEBE asignar a cada MIR un codigo formado por los dos
  ultimos digitos del ano de registro seguidos de una secuencia anual que
  comienza en `001` y usa al menos tres posiciones; por ejemplo, la primera MIR
  de 2026 recibe `26001`.
- **FR-011**: La secuencia del codigo DEBE reiniciarse cada ano y cada codigo
  DEBE ser unico incluso cuando se registren MIR simultaneamente.
- **FR-012**: El sistema DEBE asignar el identificador y las fechas de creacion
  y modificacion sin solicitarlos al detector.
- **FR-013**: Una MIR DEBE poder registrarse sin adjuntos.
- **FR-014**: Cuando haya adjuntos, estos DEBEN cargarse y quedar disponibles
  antes de solicitar el registro de la MIR.
- **FR-015**: Una MIR DEBE admitir como maximo diez adjuntos, cada uno de hasta
  25 MB y perteneciente a uno de los tipos documentales admitidos actualmente.
- **FR-016**: Al registrar una MIR con adjuntos, el sistema DEBE comprobar que
  todas las referencias existen, estan disponibles, no estan repetidas y no
  pertenecen ya a otra MIR.
- **FR-017**: El registro de la MIR y la vinculacion de todos sus adjuntos DEBEN
  completarse conjuntamente; no puede quedar una MIR con una vinculacion
  parcial.
- **FR-018**: Si falla el registro de la MIR despues de cargar documentos, el
  sistema DEBE conservarlos sin vincular para que puedan reutilizarse en un
  reintento.
- **FR-019**: El sistema DEBE rechazar el registro cuando falte cualquier dato
  obligatorio e indicar los campos que deben corregirse.
- **FR-020**: La MIR creada DEBE conservar el codigo, los datos aportados, su
  estado inicial y las referencias de sus adjuntos para consultas y etapas
  posteriores.
- **FR-021**: En esta fase el sistema NO DEBE evaluar, clasificar por origen o
  tipologia PG09, asignar tecnico de CLD, responsable de resolucion o ejecutor,
  aprobar acciones, cerrar, comprobar eficacia ni finalizar la MIR.
- **FR-022**: En esta fase el sistema NO DEBE permitir editar, archivar o borrar
  una MIR mediante esta funcionalidad.

### Key Entities *(include if feature involves data)*

- **MIR**: registro de una mejora, incidencia o reclamacion. Contiene codigo
  unico, tipo inicial, descripcion, fecha de deteccion, detector, indicador de
  solucion previa, datos condicionales de solucion, datos condicionales de
  reclamante, estado inicial, referencias documentales y fechas de registro.
- **Documento**: archivo cargado antes de registrar la MIR. Tiene una referencia
  unica, nombre, tipo, tamano, creador y disponibilidad; puede estar sin
  vincular mientras se corrige o reintenta un registro fallido y solo puede
  pertenecer a una MIR.
- **Detector**: persona existente de la organizacion a cuyo nombre se registra
  la deteccion de la MIR.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un detector puede completar un registro valido sin adjuntos en
  menos de 2 minutos.
- **SC-002**: El 100% de las MIR validas quedan identificadas inmediatamente
  con un codigo anual unico y en estado `EN_REVISION`.
- **SC-003**: El 100% de las MIR solucionadas a las que falte uno de los tres
  datos de solucion son rechazadas con una indicacion clara del dato ausente.
- **SC-004**: El 100% de las reclamaciones sin persona reclamante o empresa son
  rechazadas antes de su registro.
- **SC-005**: En una prueba de 50 registros simultaneos del mismo ano, los 50
  reciben codigos distintos y ninguno se pierde por colision de secuencia.
- **SC-006**: Un detector puede registrar correctamente una MIR con hasta diez
  adjuntos ya disponibles sin volver a cargar ninguno.
- **SC-007**: El 100% de los registros fallidos despues de una carga conservan
  los documentos disponibles para reintento y no producen vinculaciones
  parciales.
- **SC-008**: Al menos el 90% de usuarios de una prueba de aceptacion completa
  correctamente el registro al primer intento cuando dispone de todos los
  datos obligatorios.

## Assumptions

- El ano del codigo MIR es el ano en que se registra la MIR, no el ano de su
  fecha de deteccion.
- La parte secuencial comienza en `001`, se rellena con ceros hasta un minimo
  de tres posiciones y puede crecer a cuatro o mas posiciones si el volumen
  anual supera 999 registros.
- El codigo se asigna al confirmar el registro; un intento rechazado no consume
  un codigo definitivo.
- `algo_mas_que_hacer` conserva en esta fase el significado textual del modelo
  de dominio actual, sin iniciar automaticamente una accion o una nueva MIR.
- Los tipos documentales admitidos son los ya existentes: PDF, Word, Excel,
  imagen y otro.
- La carga y conservacion de archivos depende de la capacidad documental ya
  existente. Esta especificacion solo exige su vinculacion al registrar la MIR.
- Los documentos cargados y aun no vinculados no se borran automaticamente;
  su gestion posterior queda fuera del alcance de esta fase.
- Los adjuntos son opcionales, pero todos los seleccionados deben estar
  disponibles antes de crear la MIR.
- La autenticacion, los permisos por rol y las actuaciones del Jefe de CLD se
  abordaran en fases posteriores.
- La consulta, actualizacion, archivo y resto del ciclo de vida de la MIR quedan
  fuera del alcance de esta especificacion.
- El PDF original del PG09 no esta presente en el repositorio; esta
  especificacion usa las reglas de dominio documentadas en la constitucion y
  las instrucciones operativas del proyecto.
