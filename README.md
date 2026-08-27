# 🖨️ Impresoras Dashboard

**Panel de monitoreo en tiempo real para impresoras de red (Xerox y compatibles)**, con seguimiento de consumo de tóner, contadores de páginas, historial diario y notificaciones automáticas de eventos relevantes (como el cambio de cartucho de tóner).

---

## 📋 Tabla de contenidos

- [¿Qué es este proyecto?](#-qué-es-este-proyecto)
- [Características principales](#-características-principales)
- [Arquitectura](#-arquitectura)
- [Stack tecnológico](#-stack-tecnológico)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Puesta en marcha](#-puesta-en-marcha)
- [API del backend](#-api-del-backend)
- [Modelo de datos](#-modelo-de-datos)
- [Notas y limitaciones](#-notas-y-limitaciones)
- [Licencia](#-licencia)

---

## 🎯 ¿Qué es este proyecto?

Muchas oficinas tienen varias impresoras de red repartidas por distintas ubicaciones, y llevar el control manual de cuánto tóner les queda, cuántas hojas han impreso o cuándo se cambió el último cartucho es tedioso y propenso a errores.

**Impresoras Dashboard** resuelve esto **scrapeando la interfaz web administrativa de cada impresora** (los paneles `/stat/*` y `/counters/*` que exponen las Xerox por HTTP/HTTPS) de forma periódica, guardando esa información en una base de datos local y presentándola en un panel visual moderno, con:

- Estado en vivo (online/offline) de cada equipo.
- Nivel de tóner y fecha de instalación del cartucho actual.
- Contadores acumulados y diarios de páginas impresas/copiadas (simples y a doble cara).
- Historial navegable por calendario, día a día.
- Notificaciones automáticas cuando se detecta un cambio de tóner.

Todo pensado para desplegarse fácilmente en una máquina de la oficina (Windows o Linux) y consultarse desde cualquier navegador de la red local.

---

## ✨ Características principales

| Área | Detalle |
|---|---|
| 🔄 **Monitoreo automático** | Tarea en segundo plano que refresca el estado de todas las impresoras cada hora, sin bloquear la API. |
| ⚡ **Refresco manual** | Botón para forzar la actualización de una impresora puntual al instante. |
| 🎨 **Panel visual moderno** | Interfaz oscura, responsive, con barras de progreso de tóner, tarjetas por impresora y animaciones sutiles. |
| 📅 **Historial diario** | Calendario interactivo que marca los días con actividad y resalta los días de cambio de tóner. |
| 🔔 **Notificaciones** | Aviso automático al detectar un cambio de cartucho de tóner en cualquier equipo. |
| 📊 **Contadores detallados** | Páginas impresas, copiadas, a doble cara y totales, tanto acumulados como del día. |
| 🗃️ **Persistencia local** | Base de datos SQLite, sin dependencias externas ni servicios en la nube. |

---

## 🏗️ Arquitectura

```
┌─────────────────────┐        HTTP/HTTPS         ┌──────────────────────┐
│   Impresoras Xerox   │ ◄────────────────────────►│   Backend (FastAPI)  │
│  (paneles /stat, /   │      scraping periódico    │  snmp_service.py     │
│   counters)          │                            │  main.py             │
└─────────────────────┘                            └──────────┬────────────┘
                                                                │
                                                       SQLAlchemy / SQLite
                                                                │
                                                     ┌──────────▼────────────┐
                                                     │   printers.db         │
                                                     │  (printers, logs,     │
                                                     │   history, notifs)    │
                                                     └──────────┬────────────┘
                                                                │
                                                        REST API (JSON)
                                                                │
                                                     ┌──────────▼────────────┐
                                                     │  Frontend (React +    │
                                                     │  Vite + Tailwind)     │
                                                     └────────────────────────┘
```

- El **backend** hace scraping de cada impresora (no usa SNMP real pese al nombre del módulo, sino parsing HTML de los paneles web de administración), calcula los deltas diarios y guarda snapshots en SQLite.
- El **frontend** consulta el backend cada 60 segundos y renderiza el estado actual sin necesidad de recalcular nada del lado del cliente.

---

## 🛠️ Stack tecnológico

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — framework web asíncrono.
- [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite — persistencia de datos.
- [httpx](https://www.python-httpx.org/) + [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — scraping HTTP y parsing HTML.
- [Uvicorn](https://www.uvicorn.org/) — servidor ASGI.

**Frontend**
- [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- [Vite 8](https://vite.dev/) — build tool y dev server.
- [Tailwind CSS 4](https://tailwindcss.com/) — estilos utilitarios.
- [Axios](https://axios-http.com/) — cliente HTTP.
- [react-calendar](https://github.com/wojtekmaj/react-calendar) + [date-fns](https://date-fns.org/) — vista de historial por calendario.
- [lucide-react](https://lucide.dev/) — iconografía.

---

## 📁 Estructura del repositorio

```
.
├── backend/
│   ├── main.py              # API FastAPI + tarea de scraping periódico
│   ├── models.py             # Modelos SQLAlchemy (Printer, DailyLog, PrinterHistory, Notification)
│   ├── database.py           # Configuración del engine SQLite
│   ├── snmp_service.py       # Scraping de los paneles web de la impresora
│   ├── migrate_db*.py        # Scripts de migración incremental de esquema
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Componente principal del dashboard
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
├── setup_windows.bat         # Instalación automatizada en Windows
├── setup_debian13.sh         # Instalación automatizada en Debian 13
└── start.bat                 # Arranque rápido en Windows (backend + frontend)
```

---

## ✅ Requisitos previos

- **Python 3.10+**
- **Node.js 20+** (recomendado para Vite 8 / React 19)
- Acceso de red a las impresoras que se quieran monitorear (puertos 80/443 abiertos hacia sus paneles web)

---

## 📦 Instalación

### Opción A — Windows (automatizada)

```bat
setup_windows.bat
```

Este script crea el entorno virtual de Python, instala las dependencias del backend y ejecuta `npm install` en el frontend.

### Opción B — Debian 13 / Linux (automatizada)

```bash
chmod +x setup_debian13.sh
./setup_debian13.sh
```

Instala dependencias del sistema, Python, Node.js, configura ambos proyectos y genera un `start.sh` para arrancar todo con un solo comando.

### Opción C — Manual

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate.bat
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

---

## 🚀 Puesta en marcha

**Windows:**
```bat
start.bat
```

**Linux (tras usar `setup_debian13.sh`):**
```bash
./start.sh
```

**Manual (dos terminales):**
```bash
# Terminal 1 — backend
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

Luego abre tu navegador en **http://localhost:5173** (o la IP del equipo si accedes desde otro dispositivo de la red).

> ℹ️ El frontend detecta automáticamente el host desde el que se accede (`window.location.hostname`) para apuntar al backend en el puerto `8000`, así que funciona tanto en `localhost` como en la IP de la LAN.

---

## 🔌 API del backend

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/printers` | Lista todas las impresoras registradas. |
| `POST` | `/printers` | Registra una nueva impresora (`name`, `ip_address`) y dispara su primer scraping. |
| `GET` | `/printers/status` | Devuelve el snapshot cacheado del estado de todas las impresoras (respuesta instantánea). |
| `POST` | `/printers/{id}/refresh` | Fuerza un scraping inmediato de una impresora concreta. |
| `GET` | `/printers/{id}/history` | Historial diario de una impresora (contadores y cambios de tóner). |
| `GET` | `/notifications` | Lista de notificaciones generadas por el sistema. |
| `POST` | `/notifications/{id}/read` | Marca una notificación como leída. |

La tarea en segundo plano (`background_status_updater`) recorre todas las impresoras registradas cada **3600 segundos** (1 hora) y actualiza sus datos automáticamente.

---

## 🗄️ Modelo de datos

- **`Printer`** — snapshot cacheado del último estado conocido de cada impresora (para que `/printers/status` responda en milisegundos sin volver a scrapear).
- **`DailyLog`** — primer registro del día por impresora, usado como línea base para calcular los deltas diarios.
- **`PrinterHistory`** — un registro por impresora y día, con los totales diarios y si hubo cambio de tóner.
- **`Notification`** — eventos generados automáticamente (por ahora, cambios de cartucho de tóner).

---

## ⚠️ Notas y limitaciones

- El módulo `snmp_service.py` **no usa el protocolo SNMP real**: obtiene los datos parseando el HTML de los paneles web administrativos de la impresora (`/stat/welcome.php`, `/stat/consumables.php`, `/counters/usage.php`, etc.). Si tu modelo de impresora expone esas páginas con una estructura distinta, será necesario ajustar las expresiones regulares y selectores.
- El scraping asume impresoras Xerox con paneles en español/inglés; otras marcas o idiomas pueden requerir adaptar los patrones de búsqueda.
- No hay autenticación en la API ni en el frontend — pensado para uso dentro de una red local de confianza.

---

## 📄 Licencia

Este proyecto no incluye un archivo de licencia explícito. Si vas a distribuirlo o usarlo en producción, se recomienda añadir una (MIT, Apache 2.0, etc.) según corresponda.
