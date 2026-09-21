# AGENTS.md — AuditFlow (MIR)

Este archivo define cómo debe comportarse cualquier agente (Claude, Copilot, etc.) al trabajar
en el frontend de este repositorio.

**AuditFlow** es una aplicación web para gestionar procesos de auditoría técnica: auditorías,
equipos, configuraciones, normas, documentación e imágenes asociadas a los elementos auditados.

Stack de este proyecto: **Nuxt + Nuxt UI + TypeScript**, arquitectura **Feature-Sliced Design
(FSD)**.

El frontend es una aplicación independiente y no debe compartir código de dominio con el
backend.

---

## 1. Arquitectura: Feature-Sliced Design (FSD)

Referencia oficial, consultar siempre que exista duda sobre dónde colocar o cómo nombrar un
módulo:

https://feature-sliced.design/llms-small.txt

O usa su skill que esta instalada, la prioridad es la skill.

### Capas (de arriba a abajo)

1. **app** — arranque de la aplicación: routing, providers globales, plugins y estilos globales.
2. **pages** — pantallas completas asociadas a rutas.
3. **widgets** — bloques grandes de interfaz que combinan varias features o entities.
4. **features** — acciones concretas que puede realizar el usuario.
5. **entities** — entidades de negocio utilizadas por el frontend.
6. **shared** — código reutilizable completamente independiente del dominio.

Ejemplos aproximados de slices en AuditFlow:

```text
pages/
  audits/
  pumps/
  standards/

widgets/
  audit-summary/
  pump-details/
  audit-form/

features/
  create-audit/
  edit-audit/
  upload-pump-photo/
  calculate-pump/
  select-standard/

entities/
  audit/
  pump/
  employee/
  standard/
  configuration/
  photo/

shared/
  ui/
  api/
  lib/
  config/
```

Los nombres finales dependen del dominio real existente en el proyecto. No crear slices
innecesarios.

`app` y `shared` no usan slices, se organizan directamente por segments. `pages`, `widgets`,
`features` y `entities` sí usan slices.

---

## 2. Segments dentro de cada slice

Usar únicamente los segments convencionales cuando sean necesarios:

- `ui/` — componentes y representación visual.
- `api/` — comunicación con APIs o fuentes externas.
- `model/` — estado, tipos, validaciones y lógica del slice.
- `lib/` — utilidades internas del slice.
- `config/` — configuración específica del slice.

Evitar carpetas genéricas (`components/`, `hooks/`, `utils/`, `helpers/`, `services/`) cuando su
responsabilidad pueda expresarse mediante un segment estándar de FSD.

No es obligatorio crear todos los segments en cada slice — crear solo los necesarios.

---

## 3. Reglas de importación

Las dependencias siempre apuntan hacia capas inferiores:

```text
app → pages → widgets → features → entities → shared
```

Un módulo solo puede importar desde capas estrictamente inferiores.

```text
pages    → widgets, features, entities, shared
widgets  → features, entities, shared
features → entities, shared
entities → shared
shared   → shared
```

**Prohibido:**
- Imports hacia arriba (`features → widgets`, `features → pages`, `features → app`, etc.).
- Imports entre slices de la misma capa (`entities/pump` no importa `entities/photo`
  directamente). Si varias entidades deben combinarse, la composición se hace en una capa
  superior.

### Public API

Cada slice expone un único punto de entrada (`index.ts`). Nunca hacer imports profundos a
archivos internos de otro slice.

```ts
// Correcto
import { PumpCard, type Pump } from '@/entities/pump'

// Incorrecto
import { PumpCard } from '@/entities/pump/ui/PumpCard.vue'
```

---

## 4. CLI de Feature-Sliced Design

El proyecto usa el CLI oficial de FSD. Antes de crear manualmente una carpeta perteneciente a
FSD, el agente comprueba si puede generarse con el CLI y lo usa siempre que sea posible:

```bash
pnpm fsd pages audits --segments ui
pnpm fsd widgets audit-summary --segments ui
pnpm fsd features create-audit --segments ui,model,api
pnpm fsd entities pump --segments ui,model
pnpm fsd shared --segments ui,api,config
```

---

## 5. TDD — metodología obligatoria

**Todo componente, composable, store o pieza de lógica nueva se construye con TDD. Sin
excepción.**

Ciclo que el agente debe seguir en cada tarea de código:

1. **Red** — Escribir primero el test (`*.spec.ts`) que describe el comportamiento esperado. El
   test debe fallar.
2. **Green** — Escribir el mínimo código necesario para que el test pase.
3. **Refactor** — Limpiar duplicación y nombres sin cambiar comportamiento, con los tests en
   verde.
4. Repetir por cada prop, evento, estado o regla antes de pasar al siguiente.

El agente **nunca** entrega un componente o feature completos sin al menos un test que los
ejerza. Si el usuario pide "implementa X", el agente responde primero con el test y solo después
con el código que lo satisface, salvo instrucción explícita en contra.

### Tests co-ubicados

```text
PumpCard.vue
PumpCard.spec.ts
```

Como mínimo, cada componente comprueba:

- renderizado;
- props principales;
- eventos principales;
- estados relevantes;
- errores cuando aplique.

La lógica de negocio del frontend (composables, stores, `model/`) también lleva tests
independientes cuando sea relevante.

No crear tests que dependan de detalles internos de implementación — priorizar comportamiento
observable.

---

## 6. Lint, tipado y build — obligatorio tras cada cambio

**Todo cambio de código se lintea siempre**, sin esperar a que el usuario lo pida.

Comandos:

```bash
# Desarrollo
pnpm run dev

# Build
pnpm run build

# Lint
pnpm lint
pnpm lint --fix

# Tests
pnpm test
pnpm test <archivo>
pnpm test --watch

# Type-check
pnpm typecheck
```

### Flujo obligatorio después de generar o modificar código

```bash
pnpm test
pnpm lint
pnpm typecheck
```

Ejecutar también:

```bash
pnpm run build
```

cuando el cambio pueda afectar a compilación, configuración de Nuxt, imports, routing o build de
producción.

Si alguna validación falla: investigar la causa, corregir, y repetir hasta que todas pasen. Una
tarea no está terminada mientras existan errores conocidos de tests, lint, tipos o compilación.

---

## 7. TypeScript

Usar **TypeScript 5.6 o superior**. Todas las funciones correctamente tipadas.

No usar `any` salvo justificación explícita y documentada. Preferir `unknown` cuando realmente
se desconozca el tipo.

Identificadores de código en inglés:

```ts
createAudit()
selectedPump
auditId
PumpCard
AuditForm
```

Textos visibles para el usuario, comentarios y mensajes: en español.

---

## 8. Reutilización de componentes — obligatorio

**Antes de crear un componente nuevo, el agente busca si ya existe algo reutilizable.**

Orden de prioridad:

```text
modificar → reutilizar → extender → crear
```

1. Buscar en `shared/ui`, `entities/*/ui` y `widgets/*/ui` si el componente ya existe.
2. Si existe algo similar, extenderlo o parametrizarlo en vez de duplicarlo.
3. Usar siempre componentes de **Nuxt UI** antes de crear componentes visuales desde cero:

```vue
<UButton />
<UCard />
<UInput />
<USelect />
<UTable />
<UModal />
```

4. Si Nuxt UI no cubre completamente una necesidad, extenderlo mediante componentes dentro de
   `shared/ui`.

Evitar CSS personalizado innecesario. No crear un sistema de diseño paralelo a Nuxt UI.

Evitar sobreingeniería: no crear abstracciones para un único uso, wrappers sin comportamiento,
slices FSD vacíos, ni capas adicionales sin responsabilidad clara.

---

## 9. Diseño de pantallas — Mobbin MCP + skills (obligatorio)

**Para cualquier pantalla nueva o rediseño importante de una existente, es obligatorio en este
orden:**

1. Consultar referencias reales mediante el **MCP de Mobbin** antes de escribir cualquier
   código visual. No empezar la implementación de una pantalla sin haber hecho esta consulta.
2. Usar las referencias de Mobbin como inspiración de UX/UI — nunca como copia literal de otro
   producto.
3. Aplicar las **skills de diseño de pantallas** instaladas en el proyecto para transformar esa
   inspiración en la estructura FSD correcta (slice, segments, componentes Nuxt UI a usar).

4. Hay una libreria de animaciones llamda **@formkit/auto-animate/nuxt** la cual se usa para animar componentes de Nuxt UI. Para consultar su documentación, visita [nuxt-auto-animate](https://nuxt-auto-animate.vercel.app/).

El agente no debe saltarse este paso aunque la pantalla parezca simple. Si Mobbin o la skill de
diseño no está disponible en la sesión, el agente lo indica explícitamente antes de continuar en
lugar de improvisar el diseño.

---

## 10. API en el frontend

Toda comunicación HTTP reutilizable se centraliza según FSD:

- Configuración genérica → `shared/api/`
- Comunicación específica de una entidad → `entities/pump/api/`
- Acciones de una feature → `features/create-audit/api/`

Evitar llamadas `$fetch` dispersas directamente en componentes visuales cuando forman parte de
lógica reutilizable.

---

## 11. Dependencias

No añadir nuevas bibliotecas salvo que sean realmente necesarias. Antes de instalar una
dependencia:

1. comprobar si Nuxt, Nuxt UI o una dependencia existente ya resuelve el problema;
2. justificar la nueva dependencia;
3. preguntar antes de instalarla;
4. si supone un cambio relevante, actualizar primero la spec correspondiente tras recibir
   aprobación.

Nunca introducir una dependencia solo para resolver unas pocas líneas fácilmente mantenibles.

### Cambios críticos (requieren aprobación previa)

- cambios de arquitectura o de capas FSD;
- cambios importantes en entidades de dominio del frontend;
- nuevas dependencias o eliminación de dependencias;
- modificaciones de contratos o interfaces públicas (`index.ts` de un slice);
- cambios incompatibles de API consumida;
- cambios de autenticación;
- borrado de archivos.

---

## 13. Git

No hacer push directo a `main`. Los cambios se integran mediante Pull Request.

No ejecutar operaciones destructivas de Git sin autorización explícita:

```bash
git reset --hard
git clean -fd
git push --force
```

---

## 14. Checklist rápido para el agente antes de escribir código

1. Comprobar la estructura FSD existente antes de asumir dónde va el código.
2. Si es una pantalla nueva o rediseño: consultar Mobbin MCP y aplicar la skill de diseño de
   pantallas correspondiente.
3. Buscar componente reutilizable (`shared/ui`, `entities`, `widgets`, Nuxt UI) antes de crear
   uno nuevo.
4. Escribir el test primero (TDD, §5).
5. Implementar lo mínimo para pasar el test, respetando las reglas de importación de FSD (§3).
6. Refactorizar con tests en verde.
7. Ejecutar `pnpm test`, `pnpm lint`, `pnpm typecheck` (y `pnpm run build` si aplica) antes de
   dar la tarea por terminada.
8. Identificar si el cambio es crítico (§12) y pedir aprobación si corresponde.
