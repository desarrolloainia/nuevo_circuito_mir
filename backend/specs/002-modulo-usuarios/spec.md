# Feature Specification: Módulo Usuarios

**Feature Branch**: `002-modulo-usuarios`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "quiero que creemos el modulo usuarios, para ello el usuario debe de tener de momento un correo, un rol y un departamento. de momento solo quiero eso, no quiero que se autentique con contraseña ni nada"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Alta de un usuario (Priority: P1)

Un técnico de CLD o administrador del sistema da de alta a una persona de la
organización como usuario, indicando su correo, su rol (según los roles del
procedimiento PG09: Detector, Jefe de CLD, Técnico de CLD, Responsable de
resolución, Ejecutor, RSGI) y su departamento.

**Why this priority**: Sin usuarios registrados con su rol y departamento,
ningún otro módulo (como la gestión de MIR) puede asignar responsables,
ejecutores o detectores reales. Es la base de la que depende todo lo demás.

**Independent Test**: Se puede probar dando de alta un usuario con correo,
rol y departamento válidos y comprobando que queda registrado y consultable.

**Acceptance Scenarios**:

1. **Given** no existe ningún usuario con ese correo, **When** se registra un
   usuario con correo, rol y departamento válidos, **Then** el usuario queda
   dado de alta y disponible para su consulta.
2. **Given** un correo ya registrado, **When** se intenta registrar otro
   usuario con el mismo correo, **Then** el sistema rechaza el alta indicando
   que el correo ya existe.
3. **Given** faltan uno o varios de los tres datos (correo, rol o
   departamento), **When** se intenta registrar el usuario, **Then** el
   sistema rechaza el alta e indica qué dato falta.

---

### User Story 2 - Consulta de usuarios (Priority: P1)

Un técnico de CLD o cualquier proceso interno necesita consultar los usuarios
registrados (individualmente o en listado) para saber su rol y departamento,
por ejemplo al elegir a quién asignar como responsable de resolución.

**Why this priority**: La consulta es lo que permite que el resto del
sistema (y las personas) usen la información dada de alta; sin ella, el alta
no aporta valor por sí sola.

**Independent Test**: Se puede probar dando de alta uno o varios usuarios y
comprobando que se pueden consultar individualmente y listar todos.

**Acceptance Scenarios**:

1. **Given** existen usuarios registrados, **When** se consulta un usuario
   por su correo, **Then** el sistema devuelve su correo, rol y departamento.
2. **Given** existen varios usuarios registrados, **When** se solicita el
   listado de usuarios, **Then** el sistema devuelve todos los usuarios
   activos con sus datos.
3. **Given** un correo que no corresponde a ningún usuario, **When** se
   consulta por ese correo, **Then** el sistema indica que no existe.

---

### User Story 3 - Actualización y baja de un usuario (Priority: P2)

Un técnico de CLD corrige el rol o el departamento de un usuario cuando
cambian de puesto, o da de baja a un usuario que ya no pertenece a la
organización.

**Why this priority**: Es necesario para mantener los datos correctos a lo
largo del tiempo, pero el sistema ya aporta valor solo con alta y consulta
(P1); esta historia refina esa base.

**Independent Test**: Se puede probar modificando el rol o departamento de un
usuario existente y comprobando que la consulta refleja el cambio; y dando de
baja un usuario y comprobando que deja de aparecer en el listado de activos
pero su registro se conserva.

**Acceptance Scenarios**:

1. **Given** un usuario existente, **When** se actualiza su rol o su
   departamento, **Then** las consultas posteriores muestran el nuevo valor.
2. **Given** un usuario existente, **When** se da de baja, **Then** deja de
   aparecer en el listado de usuarios activos pero su registro no se elimina
   físicamente y sigue siendo consultable como usuario inactivo.
3. **Given** un usuario dado de baja, **When** se intenta asignarlo a una
   nueva responsabilidad, **Then** el sistema lo rechaza por estar inactivo.

### Edge Cases

- ¿Qué pasa si el correo tiene un formato inválido (sin `@`, dominio vacío,
  etc.)? El sistema rechaza el alta o actualización indicando el motivo.
- ¿Qué pasa si se intenta asignar un rol que no está en el catálogo de roles
  del PG09? El sistema rechaza la operación.
- ¿Qué pasa si dos altas simultáneas usan el mismo correo? Solo una debe
  tener éxito; la otra debe fallar por correo duplicado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir registrar un usuario indicando correo,
  rol y departamento.
- **FR-002**: El sistema DEBE validar que el correo tiene un formato válido.
- **FR-003**: El sistema DEBE impedir registrar dos usuarios con el mismo
  correo.
- **FR-004**: El sistema DEBE restringir el rol a los roles definidos en el
  PG09 (Detector, Jefe de CLD, Técnico de CLD, Responsable de resolución,
  Ejecutor, RSGI).
- **FR-005**: El sistema DEBE rechazar el alta o actualización de un usuario
  si falta el correo, el rol o el departamento.
- **FR-006**: El sistema DEBE permitir consultar un usuario por su correo.
- **FR-007**: El sistema DEBE permitir listar los usuarios activos.
- **FR-008**: El sistema DEBE permitir actualizar el rol y/o el departamento
  de un usuario existente.
- **FR-009**: El sistema DEBE permitir dar de baja a un usuario sin borrar su
  registro (baja lógica), conservando su historial para trazabilidad.
- **FR-010**: El sistema NO DEBE requerir contraseña, login ni ningún
  mecanismo de autenticación para el usuario en esta fase.
- **FR-011**: Un usuario dado de baja NO DEBE poder ser asignado a nuevas
  responsabilidades, aunque su registro siga siendo consultable.

### Key Entities *(include if feature involves data)*

- **Usuario**: representa a una persona de la organización que participa en
  el procedimiento PG09. Atributos: correo (identificador único de contacto),
  rol (uno de los roles fijos del PG09), departamento (nombre del
  departamento al que pertenece), estado (activo/inactivo). No tiene
  contraseña ni credenciales de acceso en esta fase.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Se puede dar de alta un usuario con correo, rol y departamento
  en menos de 1 minuto.
- **SC-002**: El 100% de los intentos de alta con un dato obligatorio
  ausente o un correo duplicado son rechazados con un motivo claro.
- **SC-003**: Un usuario dado de alta puede consultarse individualmente o en
  listado inmediatamente después del alta.
- **SC-004**: El 100% de los usuarios dados de baja dejan de estar
  disponibles para nuevas asignaciones, pero su información histórica sigue
  siendo consultable.

## Assumptions

- Un usuario tiene un único rol asignado a la vez (no múltiples roles
  simultáneos); si su función cambia, se actualiza el rol.
- El departamento se registra como texto libre (nombre del departamento), ya
  que el PG09 no define un catálogo cerrado de departamentos.
- El correo es el identificador único del usuario; no existe un nombre de
  usuario ni identificador separado en esta fase.
- La baja de usuarios es lógica, nunca un borrado físico, conforme a los
  requisitos de trazabilidad del procedimiento PG09.
- La autenticación, autorización de acceso y gestión de contraseñas quedan
  explícitamente fuera de alcance de esta fase y se abordarán en una
  iteración futura si se decide.
- No se gestiona en esta fase el nombre completo de la persona ni otros datos
  personales adicionales al correo; se documentará como ampliación futura si
  se necesita.
