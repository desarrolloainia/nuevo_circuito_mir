# Circuito MIR

## Acceso y registro de MIR

- `/login`: acceso por correo y pestaña de registro (correo, departamento y rol).
- El detector accede a `/mis-mir`, crea registros en `/crear-mir` y consulta cada uno en `/mir/{codigo_mir}`. Los demás roles siguen en `/en-construccion`.
- `POST /mir` recibe `datos` (JSON de `CrearMirDTO`) y `archivos` como multipart; `GET /mir?detectada_por_id=<id>` carga el historial del detector y `GET /mir/{codigo_mir}` carga el detalle.
- El detalle muestra el número de adjuntos; el contrato actual no devuelve sus nombres ni ofrece descarga desde esta aplicación.
- Backend configurable mediante `NUXT_PUBLIC_API_BASE` (por defecto `http://localhost:8000`).
- Contratos generados en `src/shared/schema.ts`; peticiones de usuario en `src/entities/user/api` y consultas de MIR en `src/entities/mir/api`.
- El correo se recuerda durante la pestaña y se consulta de nuevo al recargar. No se crean tokens de autenticación.

Las pantallas están en `src/pages`, la composición de rutas en `src/app/routes` y el transporte HTTP en `src/shared/api`. Los slices exponen sus imports mediante `index.ts`. Tailwind escanea todas las capas FSD desde `src/app/assets/css/main.css`.

Validación: `pnpm test`, `pnpm lint`, `pnpm typecheck`, `pnpm build`.

`pnpm exec steiger src` comprueba las fronteras FSD. Conserva los diagnósticos de nombres de la estructura original (`src/app/assets` y el contrato generado `src/shared/schema.ts`) y considera el slice existente `features/crear-mir` de un solo consumidor.

## Plantilla de origen

[![Nuxt UI](https://img.shields.io/badge/Made%20with-Nuxt%20UI-00DC82?logo=nuxt&labelColor=020420)](https://ui.nuxt.com)

Use this template to get started with [Nuxt UI](https://ui.nuxt.com) quickly.

- [Live demo](https://starter-template.nuxt.dev/)
- [Documentation](https://ui.nuxt.com/docs/getting-started/installation/nuxt)

<a href="https://starter-template.nuxt.dev/" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://ui.nuxt.com/assets/templates/nuxt/starter-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://ui.nuxt.com/assets/templates/nuxt/starter-light.png">
    <img alt="Nuxt Starter Template" src="https://ui.nuxt.com/assets/templates/nuxt/starter-light.png" width="830" height="466">
  </picture>
</a>

> The starter template for Vue is on https://github.com/nuxt-ui-templates/starter-vue.

## Quick Start

```bash [Terminal]
npm create nuxt@latest -- -t ui
```

## Deploy your own

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-name=starter&repository-url=https%3A%2F%2Fgithub.com%2Fnuxt-ui-templates%2Fstarter&demo-image=https%3A%2F%2Fui.nuxt.com%2Fassets%2Ftemplates%2Fnuxt%2Fstarter-dark.png&demo-url=https%3A%2F%2Fstarter-template.nuxt.dev%2F&demo-title=Nuxt%20Starter%20Template&demo-description=A%20minimal%20template%20to%20get%20started%20with%20Nuxt%20UI.)

## Setup

Make sure to install the dependencies:

```bash
pnpm install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
pnpm dev
```

## Production

Build the application for production:

```bash
pnpm build
```

Locally preview production build:

```bash
pnpm preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

## Renovate integration

Install [Renovate GitHub app](https://github.com/apps/renovate/installations/select_target) on your repository and you are good to go.
