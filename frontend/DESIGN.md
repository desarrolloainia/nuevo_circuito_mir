<!-- SEED: established with the user before implementation; re-run /impeccable document once there's code to capture the actual tokens and components. -->

---
name: Circuito de Calidad
description: Sistema de gestión de incidencias, reclamaciones y mejoras para auditores de calidad
colors:
  primary: "#D9550D"
  primary-deep: "#B8420A"
  primary-soft: "#F5D9C4"
  neutral-bg: "#FAF9F7"
  neutral-surface: "#FFFFFF"
  neutral-border: "#E4E1DC"
  neutral-text: "#26241F"
  neutral-text-muted: "#6B6862"
  success: "#2F7D4F"
  warning: "#C9962E"
  danger: "#C13A2E"
---

# Design System: Circuito de Calidad

## Overview

**Creative North Star: "El escritorio del auditor"**

Esta es una interfaz de trabajo, no una vitrina: la gana quien puede leer diez incidencias seguidas sin fatiga y encontrar el botón correcto sin buscarlo. La base es un neutro cálido de papel (no blanco puro, no gris frío de oficina) que sostiene bloques de texto largos con contraste cómodo. El naranja corporativo no cubre la superficie: aparece donde el auditor decide o actúa, y en ningún otro sitio, para que su aparición siga significando algo.

La densidad es la de una herramienta profesional: tablas, filtros, estados y formularios se leen sin decoración, con jerarquía tipográfica en vez de color para distinguir importancia. "Dinámica" significa que la interfaz responde con transiciones breves y feedback inmediato al filtrar, guardar o cambiar de estado — nunca que compita visualmente con el contenido.

**Key Characteristics:**
- Base neutra cálida (no gris de oficina, no blanco frío) pensada para lectura prolongada.
- Naranja restringido a acciones primarias, estados activos y foco — nunca fondo.
- Jerarquía por tipografía y espaciado, no por color.
- Modo claro por defecto con modo oscuro disponible para sesiones largas.

## Colors

Paleta restringida: una base neutra cálida que domina la superficie, con el naranja como único acento reservado para decisión y acción.

### Primary
- **Naranja Óxido** (#D9550D): acciones primarias (botones, CTAs), estado activo/seleccionado, indicadores de foco, enlaces de navegación activos. Reservado a elementos donde el usuario decide o actúa.
- **Óxido Profundo** (#B8420A): estado hover/pressed del naranja primario.
- **Óxido Suave** (#F5D9C4): fondos de resaltado sutil (fila seleccionada, badge suave, chip informativo) cuando el naranja sólido sería demasiado.

### Neutral
- **Papel** (#FAF9F7): fondo base de la aplicación. Cálido, no blanco puro, para reducir fatiga en sesiones largas.
- **Superficie** (#FFFFFF): tarjetas, paneles, filas de tabla, modales — lo que se eleva sobre el fondo.
- **Línea** (#E4E1DC): bordes, divisores, líneas de tabla. Siempre discreta, nunca estructural por sí sola.
- **Tinta** (#26241F): texto principal. Nunca negro puro, para suavizar el contraste en lectura prolongada.
- **Tinta Atenuada** (#6B6862): texto secundario, metadatos, placeholders, etiquetas de campo.

### Estado (semántico, fuera del acento de marca)
- **Éxito** (#2F7D4F): confirmaciones, incidencia resuelta.
- **Alerta** (#C9962E): pendiente de revisión, plazos próximos.
- **Error** (#C13A2E): incidencia crítica, validación fallida. Deliberadamente distinto del naranja de marca para que "acción" y "error" no se confundan nunca.

### Named Rules
**La Regla del Naranja Escaso.** El naranja de marca ocupa como máximo una acción primaria visible por vista y los estados activo/foco. Si aparece en más de dos elementos no relacionados de la misma pantalla, ha dejado de significar "actúa aquí".

**La Regla del No-Negro.** Ningún texto ni fondo usa negro (#000) o blanco (#FFF) puros. Tinta y Papel llevan siempre un matiz cálido, incluso mínimo.

## Typography

**Body/UI Font:** Public Sans (fallback: system-ui, sans-serif)
**Label/Mono Font:** ui-monospace, "SF Mono", Consolas (para IDs de incidencia, códigos, timestamps)

**Character:** Una sans neutra y muy legible en cuerpos de texto pequeños y densos — nada decorativo, todo funcional. El mono se reserva a datos técnicos para que se distingan de la prosa sin necesidad de color.

### Hierarchy
- **Title** (600, 1.5rem/24px, 1.3): título de página/sección (ej. "Incidencias abiertas").
- **Subtitle** (500, 1.125rem/18px, 1.4): cabeceras de bloque, nombre de registro dentro de un detalle.
- **Body** (400, 0.9375rem/15px, 1.5): texto de tablas, descripciones, contenido de formularios. Máximo 75ch en bloques de prosa (comentarios, descripción de incidencia).
- **Label** (500, 0.8125rem/13px, 1.2, uppercase, letter-spacing 0.02em): etiquetas de campo, cabeceras de columna de tabla, estados en badge.
- **Caption** (400, 0.75rem/12px, 1.3): metadatos, timestamps, texto de ayuda.

### Named Rules
**La Regla de la Lectura Larga.** Ningún bloque de texto de cuerpo baja de 15px ni sube de 75ch de ancho. Esta interfaz se lee durante horas; comprimir tamaño para "caber más" está prohibido.

## Layout

Contenedor de aplicación con sidebar de navegación fija + área de contenido con ancho máximo de lectura (1280px) y padding lateral cómodo (24px en desktop, 16px en móvil). Ritmo de espaciado en pasos de 4px (4/8/12/16/24/32/48), con más espacio por encima de un título que por debajo. Tablas de datos priorizan filas densas (padding vertical 10-12px) sobre tarjetas, salvo en vistas de detalle donde el contenido se organiza en secciones tipo tarjeta con separación generosa.

Responsive: sidebar colapsa a menú superior/drawer por debajo de 1024px; tablas con muchas columnas permiten scroll horizontal antes que apilarse en tarjetas ilegibles.

## Elevation & Depth

Sistema mayormente plano: la jerarquía se transmite con el contraste Papel/Superficie y líneas divisorias, no con sombra. La sombra se reserva como respuesta a estado flotante (dropdown, modal, tooltip), nunca como decoración en reposo.

### Shadow Vocabulary
- **Flotante** (`box-shadow: 0 4px 16px rgba(38, 36, 31, 0.12)`): menús desplegables, popovers, tooltips.
- **Modal** (`box-shadow: 0 12px 32px rgba(38, 36, 31, 0.18)`): diálogos y paneles modales.

### Named Rules
**La Regla de Plano en Reposo.** Ninguna tarjeta ni panel en reposo lleva sombra. La sombra aparece solo cuando el elemento se despega del flujo normal (flotante o modal).

## Shapes

Esquinas suavemente redondeadas y consistentes: 6px en controles pequeños (inputs, badges, botones), 10px en tarjetas y paneles, 999px (pill) en chips de estado. Bordes de 1px en el color Línea para delimitar tablas y campos; nunca doble borde ni bordes gruesos decorativos.

## Do's and Don'ts

### Do:
- **Do** usar el naranja únicamente en la acción primaria de cada vista y en estados activo/foco (La Regla del Naranja Escaso).
- **Do** mantener el cuerpo de texto en 15px mínimo y máximo 75ch de ancho en bloques de prosa (La Regla de la Lectura Larga).
- **Do** usar color semántico (éxito/alerta/error) para estado de incidencia, nunca el naranja de marca para eso.
- **Do** mantener las superficies planas en reposo; sombra solo en elementos flotantes.

### Don't:
- **Don't** usar el naranja como color de fondo de secciones completas (paleta "Drenched" está descartada para este producto de uso interno y lectura intensiva).
- **Don't** usar negro (#000) o blanco (#FFF) puros en texto o fondo.
- **Don't** comprimir el tamaño de fuente del cuerpo para meter más contenido en pantalla.
- **Don't** añadir gradientes, glassmorphism o iconografía decorativa genérica; cada elemento visual debe tener una función clara en el flujo de gestión.
