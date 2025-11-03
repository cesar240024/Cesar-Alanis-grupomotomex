# Prueba Técnica - Especialista en Automatizaciones e IA

## Consideraciones
- Se debe de contar con una API KEY de `Google Gemini` con Google AI Studio

## Resumen Ejecutivo
El principal problema identificado en el área comercial de Bicimex era la falta de priorización, clasificiación y visibilidad de los leads, lo que ocasionaba demoras en la atención, mala asignación de ejecutivos y pérdida de oportunidades de venta.

La solución desarrollada integra automatización inteligente e inteligencia artificial para recibir, clasificar, asignar y visualizar leads en tiempo real.
El sistema analiza los mensajes de prospectos mediante un modelo LLM(Gemini), asigna un score ponderado con base en reglas de negocio, notifica automáticamente al ejecutivo correspondiente vía n8n, y almacena la información en una base de datos conectada a un dashboard de marketing en Streamlit.

Con este flujo, se logra reducir el tiempo de respuesta y aumentar la visibilidad del pipeline comercial, resolviendo los problemas principales mencionados en el caso de estudio.

## Enfoque y Decisiones
Después de analizar el problema, se identificó que la principal causa del colapso en el proceso comercial era la falta de priorización de los leads, derivada de la ausencia de reglas claras para su clasificación.

Con base en ello, el enfoque adoptado se centró en establecer un sistema de clasificación automática que permitiera diferenciar leads de alto valor o urgencia de aquellos menos prioritarios.

Para lograrlo, se decidió combinar inteligencia artificial con reglas de negocio: los modelos de lenguaje (LLM) aportan la capacidad de interpretar la intención y el contexto del mensaje del cliente, mientras que las reglas basadas en el caso de estudio proporcionan estructura y consistencia al cálculo del score final.

De esta forma, cada lead se clasifica principalmente por nivel de urgencia, generando una priorización inteligente y alineada con los objetivos del negocio.

### Método de Clasificación de Leads
El sistema utiliza un método híbrido de clasificación que combina análisis semántico con inteligencia artificial (IA generativa) y un modelo de ponderación basado en reglas de negocio.
El objetivo es determinar de forma automática la intención, urgencia, tipo de cliente y prioridad comercial de cada lead.
#### Etapa 1 - Análisis semántico con IA (Gemini)
Cuando llega un lead, su mensaje libre se envía al modelo **Gemini 2.5 Flash** mediante un prompt estructurado (`PROMPT_TEMPLATE`).
El modelo analiza el texto y devuelve un JSON con los siguientes campos:

| Campo | Descripción | Ejemplo |
|--------|--------------|---------|
| `intent` | Tipo de solicitud (compra, cotización, soporte, consulta) | `"compra"` |
| `urgency` | Nivel de urgencia percibido | `"alta"` |
| `budget_level` | Nivel de presupuesto estimado | `"medio"` |
| `customer_type` | Tipo de cliente (empresa o particular) | `"empresa"` |
| `segment` | Categoría de producto o interés | `"electrica"` |
| `score` | Calificación general del modelo (0–100) | `85` |
| `recommended_action` | Acción sugerida (asignar, responder, escalar) | `"Asignar a ejecutivo"` |

Ejemplo de salida del modelo:
```json
{
  "intent": "compra",
  "urgency": "alta",
  "budget_level": "alto",
  "customer_type": "empresa",
  "segment": "electrica",
  "score": 87,
  "recommended_action": "Asignar a ejecutivo"
}
```
Esta etapa permite interpretar la intención real del mensaje (por ejemplo, distinguir entre alguien “explorando opciones” y alguien “listo para comprar”).

#### Etapa 2 - Ponderación con reglas de negocio (`calculate_lead_score`)

Luego, el sistema aplica un modelo de puntuación interno basado en **factores de negocio clave**, definidos a partir del caso de estudio.  
Cada factor aporta una cantidad de puntos al score según su valor.

| Factor | Ejemplo de entrada | Rango de puntos |
|---------|--------------------|------------------|
| Tipo de cliente (`tipo_cliente`) | corporativo, tienda, consumidor final | 12 – 30 |
| Canal de contacto (`canal`) | web, email, WhatsApp, feria, redes | 8 – 20 |
| Temporada (`temporada`) | alta, baja | 5 – 15 |
| Ticket estimado (`ticket`) | monto en MXN según presupuesto | 5 – 20 |
| Urgencia (`urgencia`) | alta, media, baja | 0 – 10 |
| Segmento (`segmento`) | eléctrica, MTB, urbana, infantil, etc. | 1 – 5 |

Luego se aplican **penalizaciones dinámicas**:
- Si el cliente es final y proviene de redes o ferias → −10 puntos.  
- Si la urgencia es baja → −5 puntos.  

El resultado se **normaliza entre 0 y 100** para mantener consistencia.

Luego, el sistema aplica un modelo de puntuación interno basado en factores de negocio clave, definidos a partir del caso de estudio.
Cada factor aporta una cantidad de puntos al score según su valor.

Ejemplo:
```
Lead corporativo, canal web, temporada alta, urgencia alta, ticket medio, segmento eléctrica  
→ score ponderado = 82
```

#### Etapa 3 – Score combinado (IA + reglas de negocio)

El sistema combina ambos enfoques (IA + reglas) para generar un **score final de priorización**:
```python
score_final = (score_ia * 0.4) + (ponderacion * 0.6)
```

De esta forma:
- La **IA** aporta la comprensión del lenguaje natural (intención, tono, urgencia).  
- Las **reglas de negocio** aportan estructura, consistencia y alineación con las prioridades comerciales reales.

El resultado final (`score_final`) se utiliza para:
- **Asignar el ejecutivo** adecuado mediante n8n.  
- **Visualizar la prioridad** en el dashboard de marketing.  
- **Analizar métricas de rendimiento** por canal y segmento.

### Elección de Arquitectura y Tecnologías
Se decidió implementar el flujo principal a través de una API desarrollada con FastAPI, con el propósito de mantener el proceso modular y reutilizable dentro de cualquier sistema futuro, ya sea CRM, ERP o una plataforma interna de ventas.

La lógica de clasificación, almacenamiento y visualización se concentró completamente en Python, aprovechando su ecosistema maduro de librerías (SQLAlchemy, Pandas, Streamlit) para garantizar escalabilidad y facilidad de mantenimiento.

Por otro lado, n8n se utilizó de forma complementaria, únicamente para tareas de automatización ligera, como el envío de correos automáticos a los ejecutivos asignados según el segmento o tipo de cliente. Esta decisión permitió reducir complejidad en el código del backend, manteniendo la API enfocada en la lógica de negocio y delegando procesos repetitivos a una herramienta visual de orquestación.

De esta forma, la solución combina robustez técnica, rapidez de desarrollo y flexibilidad de integración, asegurando que el sistema pueda conectarse fácilmente con otros servicios o ampliarse con nuevos módulos en el futuro.

---
### Alternativas Consideradas
Inicialmente se consideró entrenar un modelo de Machine Learning tradicional (por ejemplo, un clasificador supervisado basado en texto) que aprendiera a categorizar leads a partir de ejemplos históricos.

Sin embargo, debido a la limitada disponibilidad de datos de entrenamiento y al tiempo reducido para la implementación, se optó por un enfoque basado en modelos de lenguaje grandes (LLM), específicamente Gemini 2.5 Flash.

Este enfoque permitió aprovechar el conocimiento contextual del modelo preentrenado sin necesidad de recolectar ni etiquetar datasets, manteniendo la precisión suficiente para un prototipo funcional.

### Trade-offs aceptados conscientemente
Al sustituir un modelo de Machine Learning entrenado localmente por un LLM externo, se aceptó un trade-off entre control y velocidad de desarrollo:

- Se gana la capacidad de interpretar lenguaje natural de forma inmediata, incluso con poca información.

- Pero se sacrifica consistencia total y control interno sobre los criterios de clasificación, ya que el modelo puede generar variaciones sutiles en sus respuestas.

Para mitigar este efecto, se implementó una ponderación fija con reglas de negocio (60 % del score total) que aporta estabilidad y alineación con las prioridades comerciales, equilibrando la flexibilidad de la IA con la precisión del negocio.

### Innovación y Enfoque Declarativo de la IA
A diferencia del uso tradicional de los modelos de lenguaje como simples asistentes conversacionales o chatbots, este proyecto adopta un enfoque declarativo, en el cual el LLM se convierte en una parte funcional del flujo de código, no en una interfaz aislada.

En lugar de responder con texto libre, el modelo recibe instrucciones precisas y devuelve estructuras JSON controladas, que se integran directamente como valores dentro del sistema, permitiendo que el código continúe su ejecución a partir de las salidas del modelo.

Este enfoque representa una nueva forma de integrar IA en procesos empresariales, ya que permite que los LLM actúen como componentes de decisión dentro del software, combinando razonamiento semántico con reglas determinísticas.

Además, abre la posibilidad de hibridar la inteligencia generativa con modelos de Machine Learning tradicionales, donde los LLM pueden encargarse de interpretar y estructurar los datos de entrada, mientras los modelos de ML refinan la predicción o priorización numérica.

En conjunto, esta implementación demuestra que la IA generativa puede trascender el formato de asistente para convertirse en un motor declarativo dentro de arquitecturas automatizadas, lo cual representa un paso innovador hacia sistemas más autónomos y adaptativos.

## Cómo Funciona (paso a paso)
La solución sigue un flujo **end-to-end totalmente automatizado**, que combina inteligencia artificial, lógica de negocio y visualización en tiempo real.  
A continuación, se describe el proceso completo y la lógica detrás de cada decisión.

### 1. Recepción de lead (FastAPI)
El proceso inicia cuando un nuevo lead llega al endpoint `/lead` en formato JSON.  
El payload contiene datos como nombre, correo, teléfono, mensaje y fuente de contacto.  

Ejemplo:
```json
{
  "nombre": "Ricardo López",
  "email": "ricardo.lopez@fitbikes.mx",
  "telefono": "+52-818-642-0973",
  "tipo_cliente": "consumidor_final",
  "empresa": "N/A",
  "ubicacion": "Monterrey, NL",
  "segmento_interes": "ruta",
  "volumen_estimado": "1-5",
  "presupuesto_aproximado": "medio",
  "urgencia": "este_mes",
  "mensaje": "Estoy buscando una bicicleta de ruta ligera y cómoda para entrenar los fines de semana. Me interesa una opción de gama media con cuadro de aluminio o carbono.",
  "fuente": "whatsapp",
  "temporada": "alta"
}
```
### 2. Clasificación con IA (Gemini 2.5 Flash)
El mensaje del cliente se envía al modelo Gemini 2.5 Flash junto con un prompt estructurado que le indica devolver una respuesta estrictamente en formato JSON.
El modelo analiza el texto y clasifica el lead según:
- **Intención** (`intent`): compra, cotización, soporte o consulta

- **Urgencia** (`urgency`): alta, media o baja

- **Nivel de presupuesto** (`budget_level`): bajo, medio o alto

- **Tipo de cliente** (`customer_type`): empresa o particular

- **Segmento de interés** (`segment`): eléctrica, urbana, MTB, etc.

### 3. Cálculo del Score Ponderado (Reglas de Negocio)

Con base en los datos obtenidos del modelo, el sistema aplica una ponderación adicional mediante la función calculate_lead_score(), que asigna puntos a factores como:

- Tipo de cliente

- Canal de contacto

- Temporada

- Ticket estimado

- Urgencia

- Segmento

También aplica penalizaciones dinámicas (por ejemplo, urgencia baja o canal no prioritario).
El resultado es un score comercial entre 0 y 100 que refleja la prioridad del lead dentro del negocio.

### 4. Combinación de IA + Reglas
Para lograr equilibrio entre interpretación humana y coherencia empresarial, se calcula un score final combinado:
```python
score_final = (score_ia * 0.4) + (ponderacion * 0.6)
```
- La IA aporta la comprensión contextual del mensaje.

- Las reglas de negocio aportan estabilidad y alineación con los criterios comerciales.

Este score define el nivel de prioridad del lead (alta, media o baja).

### 5. Almacenamiento del Lead (sqlite)
Una vez calculado el `score_final`, se crea un registro en la base de datos con los campos:

- `nombre`, `email`, `telefono`, `canal`,  `mensaje`

- `tipo_cliente`, `segmento`, `urgencia`, `ticket`, `ponderacion_total`, `score_final`

El lead queda disponible en el endpoint `/leads` para consulta y visualización.

### 6. Notficación y Asignación (n8n):
El backend envía los datos del lead clasificado a un webhook de n8n, donde se ejecuta un flujo que:

Evalúa el segmento o tipo de cliente.

Asigna automáticamente el ejecutivo responsable según reglas predefinidas.

Envía un correo de notificación personalizada con la información del lead y su nivel de urgencia.

Esto permite que los ejecutivos reciban nuevos leads sin intervención manual.

```javascript
const body = $json.body;
const lead = body.lead_data;
const classification = body.classification;

let ejecutivo = { nombre: "", correo: "" };

// Caso prioritario: leads de alto valor (Roberto Campos)
if (classification.budget_level === "alto") {
  ejecutivo = { nombre: "Roberto Campos", correo: "cesar.alanisgro@outlook.com" };
}
// Asignación por segmento
else if (classification.segment === "electrica" || classification.segment === "premium") {
  ejecutivo = { nombre: "Ana Martínez", correo: "alejandro.alanisgrrr@gmail.com" };
}
else if (classification.segment === "mtb") {
  ejecutivo = { nombre: "Carlos López", correo: "cesar.alanisgro@outlook.com" };
}
else if (["corporativo", "gobierno"].includes(lead.tipo_cliente)) {
  ejecutivo = { nombre: "Diana Torres", correo: "alejandro.alanisgrrr@gmail.com" };
}
else if (["retail", "mayoreo"].includes(lead.tipo_cliente)) {
  ejecutivo = { nombre: "Eduardo Ruiz", correo: "cesar.alanisgro@outlook.com" };
}
else if (["urbana", "infantil"].includes(classification.segment)) {
  ejecutivo = { nombre: "Fernanda Silva", correo: "alejandro.alanisgrrr@gmail.com" };
}
// Valor por defecto (si nada coincide)
else {
  ejecutivo = { nombre: "Diana Torres", correo: "alejandro.alanisgrrr@gmail.com" };
}

return [{
  urgencia: classification.urgency,
  nombre: lead.nombre,
  email_cliente: lead.email,
  telefono: lead.telefono,
  segmento: classification.segment,
  tipo_cliente: lead.tipo_cliente,
  mensaje: lead.mensaje,
  fuente: lead.fuente,
  score_final: body.score_final,
  ejecutivo
}];
```

Se utilizan correos personales de ejemplo.

### 7. Visualización en el Dashboard (Streamlit)

El endpoint `/leads` es consumido por un dashboard en Streamlit, el cual muestra:

- Métricas clave: total de leads, urgencia alta, score promedio.

- Gráficos interactivos:

    - Distribución de urgencias

    - Leads por segmento

    - Tipo de cliente

    - Score por canal

    - Tabla de leads recientes: con auto-refresh cada 30 segundos.

Esta vista otorga al área de **marketing visibilidad inmediata y permite detectar tendencias o sobrecarga** de segmentos en tiempo real.

#### Lógica de Decisiones Clave
| Decisión              | Justificación                                                               |
| --------------------- | --------------------------------------------------------------------------- |
| Uso de LLM (Gemini)   | Permite interpretar lenguaje natural sin entrenar un modelo desde cero.     |
| Regla ponderada (60%) | Compensa la variabilidad del LLM con consistencia comercial.                |
| FastAPI               | Arquitectura modular y reutilizable para futuras integraciones.             |
| n8n                   | Automatización simple y visual para tareas repetitivas (envío de correos).  |
| Streamlit             | Herramienta ágil para dashboards con capacidad de actualización automática. |

#### Integración de IA
La IA no actúa como un asistente externo, sino como un componente declarativo dentro del flujo del software:
su salida (JSON estructurado) se interpreta directamente como valores que el sistema utiliza para continuar el procesamiento.
Esto permite que el modelo se integre como una capa de decisión inteligente dentro de la API, más que como un chatbot independiente.

## Demo y Ejemplos
Esta sección muestra cómo se probó la solución de forma práctica, utilizando ejemplos de leads reales y verificando la clasificación automática, la asignación de ejecutivos y la visualización en el dashboard.

Para mantener el documento conciso, se incluye solo un ejemplo detallado.  
En el video complementario se muestran escenarios adicionales (lead mediano, bajo valor y consumidor final) donde puede observarse la variación en el score final y la asignación de ejecutivos. Además se muestra el dashboard donde pudiera apreciarse mejor.

---

### Cómo se probó la solución

1. Se configuró el entorno local de desarrollo con **FastAPI**, **n8n Cloud** y **Streamlit** ejecutándose de manera simultánea:
   - **API:** `uvicorn main:app --reload`
   - **Dashboard:** `streamlit run dashboard.py`
   - **n8n Webhook:** conectado al endpoint `/lead` de la API.

2. Se realizaron múltiples pruebas enviando solicitudes `POST` al endpoint `/lead` mediante **Postman** o **cURL**, simulando leads provenientes de distintos canales y con diferentes intenciones.

3. En cada prueba se verificó:
   - Que el modelo **Gemini 2.5 Flash** devolviera un JSON válido con la clasificación.  
   - Que la función de ponderación asignara correctamente los puntos según las reglas de negocio.  
   - Que el lead se almacenara en la base de datos con su `score_final`.  
   - Que **n8n** enviara un correo automático al ejecutivo correspondiente.  
   - Que el **dashboard** actualizara métricas y gráficos en tiempo real.

---

### Ejemplos de Leads de Entrada
Antes de realizar las pruebas, es necesario **exponer la API localmente** para que el flujo de **n8n** pueda recibir los datos del endpoint `/lead`.

---

### Exponer la API con Localtunnel

1. Instalar Localtunnel globalmente (solo una vez):
   ```bash
   npm install -g localtunnel

2. Ejecutar el comando
```bash
    uvicorn main:app --reload
```
3. En otra terminal, exponer el puerto 8000 (o el que uses):
```bash
lt --port 8000
```
4. Localtunnel generará una URL pública similar a:

    `https://cool-forks-repair.loca.lt`

5. Colocar esta URL en Postman o donde se pruebe la API, `https://cool-forks-repair.loca.lt/lead`

### Ejemplo  - Lead Corporativo de Alto valor:

Ejemplo:
```json
```json
{
  "nombre": "Javier Lozano",
  "email": "javier.lozano@bikecitycorp.mx",
  "telefono": "+52-55-7911-5532",
  "tipo_cliente": "corporativo",
  "empresa": "BikeCity Corp",
  "ubicacion": "Ciudad de México, CDMX",
  "segmento_interes": "eléctrica",
  "volumen_estimado": "60-80",
  "presupuesto_aproximado": "alto",
  "urgencia": "alta",
  "mensaje": "Somos una empresa de transporte urbano y buscamos adquirir 70 bicicletas eléctricas para reparto en CDMX. Necesitamos cotización y tiempos de entrega inmediatos.",
  "fuente": "web",
  "temporada": "alta"
}
```
Resultado esperado después de aplicar reglas de negocio:
| Factor              | Valor           | Puntos |
| ------------------- | --------------- | ------ |
| Tipo de cliente     | corporativo     | 30     |
| Canal               | web             | 20     |
| Temporada           | alta            | 15     |
| Ticket estimado     | alto (1.2M MXN) | 18     |
| Urgencia            | alta            | 10     |
| Segmento            | eléctrica       | 5      |
| Penalizaciones      | —               | 0      |
| **Total ponderado** |                 | **98** |

#### Score final(esperado)
```python
score_final = (94 * 0.4) + (98 * 0.6) = 96.4
```

#### Ejecutivo asignado por n8n (resultado esperado)
```json
{
  "nombre": "Roberto Campos",
  "correo": "cesar.alanisgro@outlook.com"
}
```

#### Resultado API
```JSON
{
    "status": "ok",
    "lead_data": {
        "nombre": "Javier Lozano",
        "email": "javier.lozano@bikecitycorp.mx",
        "telefono": "+52-55-7911-5532",
        "tipo_cliente": "corporativo",
        "empresa": "BikeCity Corp",
        "ubicacion": "Ciudad de México, CDMX",
        "segmento_interes": "eléctrica",
        "volumen_estimado": "60-80",
        "presupuesto_aproximado": "alto",
        "urgencia": "alta",
        "mensaje": "Somos una empresa de transporte urbano y buscamos adquirir 70 bicicletas eléctricas para reparto en CDMX. Necesitamos cotización y tiempos de entrega inmediatos.",
        "fuente": "web",
        "temporada": "alta"
    },
    "classification": {
        "intent": "cotizacion",
        "urgency": "alta",
        "budget_level": "alto",
        "customer_type": "empresa",
        "segment": "electrica",
        "score": 95,
        "recommended_action": "Asignar a ejecutivo"
    },
    "ponderacion_total": 78,
    "score_final": 84.8
}
```
#### Correo enviado a través de n8n
```bash
MENSAJE: Somos una empresa de transporte urbano y buscamos adquirir 70 bicicletas eléctricas para reparto en CDMX. Necesitamos cotización y tiempos de entrega inmediatos.

Nombre: Javier Lozano
Correo: javier.lozano@bikecitycorp.mx
Teléfono: ‪+52-55-7911-5532‬
Segmento: electrica
Fuente: web
Score Final: 84.8
Ejecutivo Asignado

Nombre: Roberto Campos
Correo: cesar.alanisgro@outlook.com 
```

#### Nota sobre discrepancias en el score
Durante las pruebas se observó que el score final calculado por la API puede diferir ligeramente del score estimado manualmente en el documento.
Esta diferencia no representa un error, sino una consecuencia directa del modelo de puntuación implementado.

Causas principales:

- Escala real de negocio:
Los puntos asignados en calculate_lead_score() se basan en rangos económicos y características reales del cliente.
Por ejemplo, un lead con presupuesto de 1.2 M MXN pertenece al rango “retail” (500 k–2 M), el cual otorga 18 puntos,
mientras que solo proyectos mayores a 3 M MXN alcanzan los 20 puntos.
Esto refleja una escala no lineal, alineada con la realidad comercial.

- Normalización de puntajes:
El valor de ponderacion_total no necesariamente alcanza 100, ya que el modelo fue calibrado para mantener un margen razonable entre categorías.
Por tanto, un lead de alto valor puede tener una ponderación de 76–90 sobre 100 sin dejar de ser prioritario.

- Ajuste híbrido (IA + reglas):
El score_final combina el resultado semántico del modelo LLM (40 %) con la ponderación de reglas de negocio (60 %).
De esta forma:
```
score_final = (score_ia * 0.4) + (ponderacion_total * 0.6)
```

Cualquier pequeña variación en la salida del modelo o en los factores de negocio genera diferencias esperadas entre ejemplos teóricos y resultados reales.


## Roadmap Futuro y Escalabilidad

El prototipo actual demuestra un flujo funcional y automatizado de clasificación inteligente de leads, combinando IA generativa, reglas de negocio y automatización visual (n8n).  
A continuación, se detallan las líneas de evolución técnica planificadas para llevar esta solución a un entorno productivo, escalable y completamente autónomo:

---

### 1. Despliegue en la nube

**Objetivo:** Escalar la API y garantizar alta disponibilidad.

- Contenerizar la aplicación con **Docker**.  
- Exponer la API en **Azure Container Apps** o **Azure App Service**, asegurando un entorno con balanceo de carga, métricas y control de versiones.  
- Integrar pipelines CI/CD con **GitHub Actions** o **Azure DevOps**.  
- Desplegar el **dashboard en Streamlit Cloud** o dentro del mismo entorno de Azure, asegurando acceso público controlado y sincronización en tiempo real con la base de datos.

**Beneficio:** La API y el dashboard podrán ser accedidos globalmente con seguridad y escalabilidad, listos para integración con CRM o ERP corporativos.

---

### 2. Extensión de funcionalidades de la API

**Objetivo:** Ampliar la utilidad del sistema y mejorar su mantenibilidad.

- Incorporar nuevos **endpoints REST** (`PUT`, `DELETE`, `PATCH`) para gestión avanzada de leads.  
- Implementar autenticación basada en **JWT + API Key**.  
- Agregar un endpoint `/analytics` con métricas en tiempo real (por canal, tipo de cliente, urgencia o ejecutivo).  
- Integrar un sistema de logs y auditoría centralizada.

**Beneficio:** Convertir la API en un servicio reutilizable, modular y listo para integrarse en arquitecturas empresariales.

---

### 3. Integración con un LLM autónomo mediante MCP Server

**Objetivo:** Automatizar completamente la captura y clasificación de leads.

- Desarrollar un **MCP Server (Model Context Protocol)** que permita a un modelo LLM conectarse con fuentes externas (correos, formularios o redes sociales).  
- El servidor podrá interpretar mensajes automáticamente, extraer los leads y enviarlos directamente a la base de datos a través de la API.  
- Esto habilita un flujo totalmente autónomo, donde la IA actúa como agente inteligente dentro del ecosistema empresarial.

**Beneficio:** Captura automática y clasificación inteligente sin intervención manual, manteniendo trazabilidad en la base de datos.

---

### 4. Migración de base de datos a PostgreSQL

**Objetivo:** Mejorar la escalabilidad, seguridad y capacidad analítica.

- Migrar la base de datos local (SQLite) a **PostgreSQL**.  
- Implementar un esquema relacional optimizado con índices, vistas analíticas y soporte multiusuario.  
- Configurar conexión segura mediante **SQLAlchemy** y variables de entorno en Azure.

**Beneficio:** Mayor rendimiento, estabilidad y escalabilidad, especialmente en entornos con grandes volúmenes de leads.

---

### 5. Dashboard avanzado y analítica inteligente

**Objetivo:** Evolucionar la visualización hacia un sistema de inteligencia comercial completo.

- Incorporar **gráficos comparativos, KPIs dinámicos y filtros por canal o segmento**.  
- Integrar autenticación y roles de usuario (marketing, dirección, analistas).  
- Agregar análisis predictivo de cierre de leads y rendimiento por ejecutivo.

**Beneficio:** Ofrecer una vista estratégica del pipeline comercial, con datos en tiempo real y métricas accionables.

---

### 6. Implementación de un modelo de Machine Learning complementario

**Objetivo:** Fortalecer el método de clasificación con un modelo de aprendizaje supervisado.

- Entrenar un **modelo de Machine Learning (Random Forest, Logistic Regression o XGBoost)** utilizando los leads históricos almacenados en PostgreSQL.  
- Este modelo permitirá **predecir la probabilidad de conversión o valor comercial** de un nuevo lead, complementando el análisis semántico del LLM.  
- La arquitectura combinará ambos enfoques:
  - **LLM (Gemini):** interpreta la intención, urgencia y tono del mensaje.  
  - **Modelo ML:** ajusta el score final en base a patrones reales de conversión.  

**Beneficio:** Un sistema híbrido más preciso, que aprende de datos reales mientras conserva la flexibilidad interpretativa de la IA generativa.

---

### Visión General

El objetivo final es evolucionar el prototipo hacia una **plataforma de inteligencia comercial integral**, en la cual:

- La **API** se ejecute de forma continua en la nube (Azure).  
- La **IA** capture, clasifique y registre leads automáticamente.  
- El **modelo de Machine Learning** refine las predicciones a partir del historial de resultados.  
- El **dashboard** se convierta en un panel interactivo de inteligencia comercial.  
- Y la **base de datos PostgreSQL** sea el núcleo analítico de toda la arquitectura.

---

**Resultado esperado:**  
Una solución modular, escalable y autónoma que combine IA declarativa, Machine Learning y automatización empresarial para optimizar la gestión de leads a nivel corporativo.
