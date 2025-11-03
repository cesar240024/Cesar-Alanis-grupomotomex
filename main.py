from fastapi import Depends, FastAPI, Request
import google.generativeai as genai
import os, json, re
from dotenv import load_dotenv

from sqlalchemy.orm import Session
from databases.leads.database import SessionLocal
from databases.leads.models import Lead
import requests


# Configurar API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(title="Lead Classifier API", version="1.2")


MODEL = "gemini-2.5-flash"

PROMPT_TEMPLATE = """
Eres un clasificador inteligente de leads para una empresa que vende bicicletas.

Analiza el siguiente mensaje y devuelve SOLO un JSON con esta estructura, sin ningún texto adicional:

{{
  "intent": "compra" | "cotizacion" | "soporte" | "consulta",
  "urgency": "alta" | "media" | "baja",
  "budget_level": "bajo" | "medio" | "alto",
  "customer_type": "empresa" | "particular",
  "segment": "mtb" | "urbana" | "infantil" | "electrica",
  "score": número entre 0 y 100,
  "recommended_action": "Asignar a ejecutivo" | "Responder información" | "Escalar a supervisor"
}}

Mensaje del lead:
\"\"\"{mensaje}\"\"\"
"""


# ------------------------------------------------------
# FUNCIÓN DE PONDERACIÓN
# ------------------------------------------------------
def calculate_lead_score(tipo_cliente, canal, temporada, ticket, urgencia, segmento):
    tipo_cliente_pts = {
        "corporativo": 30, "retail": 27, "mediana": 22,
        "pequeña": 17, "tienda": 17, "final": 12,
        "consumidor_final": 12, "gobierno": 25
    }.get(tipo_cliente.lower(), 10)

    canal_pts = {
        "formulario web": 20, "web": 20, "email": 18, "whatsapp": 15,
        "llamada": 12, "redes": 8, "feria": 10, "evento": 10
    }.get(canal.lower(), 10)

    temporada_pts = {"alta": 15, "baja": 10}.get(temporada.lower(), 5)

    # ✅ Soporte para texto y números
    ticket_pts = 0
    if isinstance(ticket, str):
        ticket_pts = {"bajo": 5, "medio": 10, "alto": 20}.get(ticket.lower(), 10)
    else:
        if 8000 <= ticket <= 25000: ticket_pts = 5
        elif 80000 <= ticket <= 200000: ticket_pts = 10
        elif 200000 <= ticket <= 500000: ticket_pts = 15
        elif 500000 <= ticket <= 2000000: ticket_pts = 18
        elif 300000 <= ticket <= 5000000: ticket_pts = 20

    urgencia_pts = {"alta": 10, "media": 5, "baja": 0}.get(urgencia.lower(), 0)

    segmento_pts = {
        "electrica": 5, "mtb": 4, "ruta": 3,
        "urbana": 2, "infantil": 1, "bmx": 1
    }.get(segmento.lower(), 2)

    score = sum([
        tipo_cliente_pts,
        canal_pts,
        temporada_pts,
        ticket_pts,
        urgencia_pts,
        segmento_pts
    ])

    # Penalizaciones dinámicas
    if tipo_cliente.lower() in ["final", "consumidor_final"] and canal.lower() in ["redes", "feria"]:
        score -= 10
    if urgencia.lower() == "baja":
        score -= 5

    # Escalar entre 0 y 100
    return max(min(score, 100), 0)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def notificar_n8n(lead_data):
    N8N_WEBHOOK_URL = "https://cesaralanis2400.app.n8n.cloud/webhook/21e43be0-940c-4f7a-a0cd-a464beca9619"
    try:
        requests.post(N8N_WEBHOOK_URL, json=lead_data)
    except Exception as e:
        print(f"Error notificando a n8n: {e}")


# ------------------------------------------------------
# ENDPOINT PRINCIPAL
# ------------------------------------------------------
@app.post("/lead")
async def classify_lead(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    mensaje = data.get("mensaje", "")

    if not mensaje:
        return {"error": "Falta el campo 'mensaje' en el JSON."}

    prompt = PROMPT_TEMPLATE.format(mensaje=mensaje)

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        text_output = response.text.strip()

        # Limpiar bloques de código markdown
        clean_text = re.sub(r"```(?:json)?", "", text_output).strip()

        try:
            classification = json.loads(clean_text)
        except json.JSONDecodeError:
            classification = {"raw_output": text_output}

        # Extraer variables necesarias (usando defaults)
        tipo_cliente = classification.get("customer_type", "particular")
        canal = data.get("fuente", "formulario web")
        temporada = data.get("temporada", "baja")
        ticket_label = classification.get("budget_level", "medio")
        urgencia = classification.get("urgency", "media")
        segmento = classification.get("segment", "urbana")

        # Traducir ticket label a monto estimado
        ticket = {
            "bajo": 15000,
            "medio": 150000,
            "alto": 1200000
        }.get(ticket_label, 150000)

        ponderacion = calculate_lead_score(
            tipo_cliente, canal, temporada, ticket, urgencia, segmento
        )

        # Score combinado (ponderación + LLM)
        llm_score = classification.get("score", 0)
        score_final = round((llm_score * 0.4) + (ponderacion * 0.6), 2)

            # Al final, guarda el lead en la base de datos
        nuevo_lead = Lead(
            nombre=data.get("nombre"),
            email=data.get("email"),
            telefono=data.get("telefono"),
            canal=canal,
            mensaje=mensaje,
            tipo_cliente=tipo_cliente,
            segmento=segmento,
            urgencia=urgencia,
            ticket=ticket,
            ponderacion_total=ponderacion,
            score_final=score_final
        )



        

        db.add(nuevo_lead)
        db.commit()
        db.refresh(nuevo_lead)

        output = {
            "status": "ok",
            "lead_data": data,
            "classification": classification,
            "ponderacion_total": ponderacion,
            "score_final": score_final
        }

        notificar_n8n(output)

        return output

    except Exception as e:
        return {"error": str(e)}
    
# ------------------------------------------------------
# ENDPOINT PARA LISTAR LEADS
# ------------------------------------------------------
@app.get("/leads")
def listar_leads(db: Session = Depends(get_db)):
    """
    Devuelve todos los leads almacenados en la base de datos.
    """
    leads = db.query(Lead).order_by(Lead.id.desc()).all()

    # Convertir los objetos SQLAlchemy a diccionarios JSON serializables
    resultado = [
        {
            "id": lead.id,
            "nombre": lead.nombre,
            "email": lead.email,
            "telefono": lead.telefono,
            "canal": lead.canal,
            "mensaje": lead.mensaje,
            "tipo_cliente": lead.tipo_cliente,
            "segmento": lead.segmento,
            "urgencia": lead.urgencia,
            "ticket": lead.ticket,
            "ponderacion_total": lead.ponderacion_total,
            "score_final": lead.score_final,
        }
        for lead in leads
    ]

    return {"total": len(resultado), "leads": resultado}


