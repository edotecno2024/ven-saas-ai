from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta

# Configuración de Seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Base de datos de usuarios (Simulada para esta fase)
users_db = {
    "admin@venledger.com": {
        "username": "admin@venledger.com",
        "full_name": "Contador Pro",
        "hashed_password": pwd_context.hash("clave123"), # Cambia esto luego
        "disabled": False,
    }
}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Correo o clave incorrecta")
    
    # Aquí generamos el "pase de entrada"
    return {"access_token": user["username"], "token_type": "bearer"}

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


