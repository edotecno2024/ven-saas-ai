from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import datetime

app = FastAPI(title="VEN-Ledger AI Engine")

# --- CONFIGURACIÓN DE SEGURIDAD (CORS) ---
# Esto es vital para que tu dashboard en GitHub no sea bloqueado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que edotecno2024.github.io se conecte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BASE DE DATOS SIMULADA (Para arranque rápido) ---
# En el futuro, aquí conectarás PostgreSQL
db_mock = {
    "tasa_bcv": 36.55,
    "last_update": datetime.date.today().isoformat()
}

# --- RUTAS ---

@app.get("/")
def home():
    """Verificación de estado del motor"""
    return {
        "status": "Online",
        "motor": "VEN-Ledger AI v1.2",
        "tasa_bcv": db_mock["tasa_bcv"],
        "server_time": datetime.datetime.now().strftime("%H:%M:%S")
    }

@app.post("/asiento")
def crear_asiento(
    desc: str = Query(..., description="Descripción del asiento"),
    monto: float = Query(..., description="Monto base en bolívares"),
    es_contribuyente_especial: bool = False
):
    """Procesa un asiento contable con lógica fiscal venezolana"""
    try:
        iva_porcentaje = 0.16
        iva_monto = round(monto * iva_porcentaje, 2)
        total = round(monto + iva_monto, 2)
        
        # Lógica de Retenciones (SENIAT)
        retencion_iva = 0
        if es_contribuyente_especial:
            retencion_iva = round(iva_monto * 0.75, 2) # Retención estándar del 75%

        # Audit Guardian: Análisis de riesgo básico
        alerta = None
        if monto > 50000:
            alerta = "⚠️ MONTO ELEVADO: Requiere revisión de soporte físico para evitar reparos del SENIAT."
        
        return {
            "descripcion": desc.upper(),
            "base_imponible": monto,
            "iva_16": iva_monto,
            "retencion_75": retencion_iva,
            "total_a_pagar": total,
            "equivalente_usd": round(total / db_mock["tasa_bcv"], 2),
            "audit_guardian_note": alerta
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit/rif")
def validar_rif(rif: str):
    """Simulador de validación de RIF"""
    rif = rif.upper().replace("-", "")
    if len(rif) < 9:
        return {"valido": False, "error": "Formato de RIF muy corto."}
    
    return {
        "rif": rif,
        "valido": True,
        "contribuyente": "PERSONA JURÍDICA",
        "status": "ACTIVO"
    }

@app.get("/tasa")
def obtener_tasa():
    """Devuelve la tasa oficial configurada"""
    return db_mock

@app.get("/reporte/balance")
def generar_balance():
    # Simulación de datos contables reales
    return {
        "empresa": "CLIENTE DEMO S.A.",
        "periodo": "MARZO 2026",
        "cuentas": [
            {"codigo": "1.1.01", "nombre": "Caja Chica", "debe": 500.00, "haber": 0},
            {"codigo": "1.1.02", "nombre": "Banco Mercantil", "debe": 12500.50, "haber": 0},
            {"codigo": "2.1.01", "nombre": "Cuentas por Pagar", "debe": 0, "haber": 4200.00},
            {"codigo": "4.1.01", "nombre": "Ventas Gravadas", "debe": 0, "haber": 8800.50}
        ],
        "totales": {"debe": 13000.50, "haber": 13000.50}
    }

