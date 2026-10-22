import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import io
import requests

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DEL ENLACE DE GOOGLE DRIVE (PEGA AQUÍ TU URL CORPORATIVO)
# -----------------------------------------------------------------------------
URL_GOOGLE_DRIVE_DEFAULT = "https://docs.google.com/spreadsheets/d/1e80JLTk3YW7c6yxNwiMXq7_5XtpvGd9s/edit?usp=sharing&ouid=116051950038931432257&rtpof=true&sd=true"

# -----------------------------------------------------------------------------
# 2. CONFIGURACIÓN DE PÁGINA Y ESTILOS EJECUTIVOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Control Operativo BOL | Seguimiento Integral",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 15px 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04);
        margin-bottom: 12px;
    }
    .metric-title {
        color: #64748b;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.65rem;
        font-weight: 800;
        margin-top: 4px;
    }
    .metric-sub {
        color: #334155;
        font-size: 0.76rem;
        font-weight: 500;
        margin-top: 4px;
    }
    .badge-green {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .badge-yellow {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .badge-red {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .alert-standby {
        background-color: #fff7ed;
        border-left: 5px solid #f97316;
        padding: 14px 18px;
        border-radius: 8px;
        border-top: 1px solid #fed7aa;
        border-right: 1px solid #fed7aa;
        border-bottom: 1px solid #fed7aa;
        margin-bottom: 14px;
        color: #0f172a;
        font-size: 0.9rem;
    }
    .alert-overtime {
        background-color: #f5f3ff;
        border-left: 5px solid #7c3aed;
        padding: 14px 18px;
        border-radius: 8px;
        border-top: 1px solid #ddd6fe;
        border-right: 1px solid #ddd6fe;
        border-bottom: 1px solid #ddd6fe;
        margin-bottom: 14px;
        color: #0f172a;
        font-size: 0.9rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 6px;
        padding: 8px 12px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
        color: #334155;
        font-size: 0.82rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-color: #0f172a !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MAESTRO OFICIAL DE RECURSOS, SECTORES, ZONAS Y REGLAS DE TURNO
# -----------------------------------------------------------------------------
MAESTRO_ZONAS = {
    "BOLG-332": ("CENTRO", "IBAGUE URBANA"),
    "BOLM-301": ("CENTRO", "IBAGUE RURAL"),
    "BOLM-302": ("CENTRO", "IBAGUE RURAL"),
    "BOLM-308": ("CENTRO", "ROVIRA"),
    "BOLM-309": ("CENTRO", "SAN JUAN DE LA CHINA"),
    "BOLM-310": ("CENTRO", "SAN LUIS"),
    "BOLM-311": ("CENTRO", "VALLE DE SAN JUAN"),
    "BOLM-313": ("CENTRO", "PIEDRAS"),
    "BOLM-330": ("CENTRO", "IBAGUE RURAL"),
    "BOLM-348": ("CENTRO", "IBAGUE URBANA"),
    "BOLM-353": ("CENTRO", "CAJAMARCA"),
    "BOLV-303": ("CENTRO", "CAJAMARCA"),
    "BOLV-304": ("CENTRO", "PAYANDE"),
    "BOLV-307": ("CENTRO", "ROVIRA"),
    "BOLV-312": ("CENTRO", "ALVARADO"),
    "BOLV-330": ("CENTRO", "IBAGUE URBANA"),
    "BOLV-333": ("CENTRO", "IBAGUE URBANA"),
    "BOLV-336": ("CENTRO", "IBAGUE URBANA"),
    "BOLV-337": ("CENTRO", "IBAGUE RURAL"),
    "BOLV-394": ("CENTRO", "IBAGUE URBANA"),
    "BOLV-397": ("CENTRO", "IBAGUE URBANA"),
    "BOLV-398": ("CENTRO", "IBAGUE URBANA"),
    "BOLV-399": ("CENTRO", "IBAGUE URBANA"),
    "BOLE-990": ("CENTRO", "CENTRO"),
    "BOLE-999": ("NORTE", "NORTE"),
    "BOLV-365": ("NORTE", "HONDA"),
    "BOLV-363": ("NORTE", "HONDA"),
    "BOLV-396": ("NORTE", "MARIQUITA"),
    "BOLV-366": ("NORTE", "MARIQUITA"),
    "BOLV-368": ("NORTE", "MARIQUITA"),
    "BOLV-372": ("NORTE", "LERIDA"),
    "BOLV-360": ("NORTE", "VENADILLO"),
    "BOLV-317": ("NORTE", "FRESNO"),
    "BOLM-314": ("NORTE", "CASABIANCA"),
    "BOLM-315": ("NORTE", "FALAN"),
    "BOLM-316": ("NORTE", "FRESNO"),
    "BOLM-318": ("NORTE", "HERVEO"),
    "BOLM-319": ("NORTE", "PADUA"),
    "BOLM-321": ("NORTE", "AMBALEMA"),
    "BOLM-371": ("NORTE", "LERIDA"),
    "BOLM-369": ("NORTE", "LIBANO"),
    "BOLV-370": ("NORTE", "LIBANO"),
    "BOLM-322": ("NORTE", "ANZOATEGUI"),
    "BOLM-324": ("NORTE", "JUNIN"),
    "BOLM-320": ("NORTE", "PALOCABILDO"),
    "BOLM-323": ("NORTE", "PALOCABILDO"),
    "BOLM-361": ("NORTE", "GUAYABAL"),
    "BOLM-362": ("NORTE", "GUAYABAL"),
    "BOLM-325": ("NORTE", "SANTA ISABEL"),
    "BOLM-326": ("NORTE", "LIBANO"),
    "BOLM-327": ("NORTE", "MURILLO"),
    "BOLM-328": ("NORTE", "SANTA TERESA"),
    "BOLM-329": ("NORTE", "VILLAHERMOSA"),
    "BOLM-350": ("NORTE", "MARIQUITA")
}

ROTATIVAS_3T_CENTRO = {"BOLG-332", "BOLV-330", "BOLV-333", "BOLV-336", "BOLV-394", "BOLV-397", "BOLV-399"}
ROTATIVAS_2T_NORTE = {"BOLV-363", "BOLV-365"}
ROTATIVAS_3T_NORTE = {"BOLV-366", "BOLV-368", "BOLV-396"}
BOLE_ESPECIALES = {"BOLE-990", "BOLE-999"}

MESES_ES = {
    1: "01 - Enero", 2: "02 - Febrero", 3: "03 - Marzo", 4: "04 - Abril",
    5: "05 - Mayo", 6: "06 - Junio", 7: "07 - Julio", 8: "08 - Agosto",
    9: "09 - Septiembre", 10: "10 - Octubre", 11: "11 - Noviembre", 12: "12 - Diciembre"
}

ACTIVIDADES_RUTINA = [
    "INICIO TURNO", "FIN TURNO", "ALIMENTACIÓN", "ALIMENTACION",
    "FORMACIONES", "TIEMPO NO PRODUCTIVO"
]

COLORES_CAUSAS = {
    "🌿 Vegetación / Árboles": "#10b981",
    "🔧 Deterioro / Falla de Material": "#f59e0b",
    "🌧️ Lluvias / Mal Tiempo": "#3b82f6",
    "💨 Fuertes Vientos": "#06b6d4",
    "⚡ Descargas Atmosféricas": "#8b5cf6",
    "🐾 Animales / Fauna": "#ec4899",
    "🚗 Terceros / Vehículos": "#ef4444",
    "🔌 Variación Voltaje / Acometida BT": "#6366f1",
    "🔍 Operación / Sin Causa Explícita": "#94a3b8"
}

# -----------------------------------------------------------------------------
# 4. FUNCIONES DE LECTURA Y PROCESAMIENTO
# -----------------------------------------------------------------------------
def convert_time_to_minutes(time_val):
    if pd.isna(time_val):
        return 0.0
    val_str = str(time_val).strip()
    try:
        if ':' in val_str:
            parts = val_str.split(':')
            if len(parts) >= 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                return float(hours * 60 + minutes)
        return float(val_str)
    except Exception:
        return 0.0


def hour_str_to_min_of_day(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    m = re.search(r'^(\d{1,2}):(\d{2})', s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    return np.nan


def parse_google_drive_url(url: str) -> str:
    if not url:
        return ""
    sheets_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
    if sheets_match:
        sheet_id = sheets_match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    drive_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
        
    return url


def normalize_recurso_key(recurso_str: str) -> str:
    if pd.isna(recurso_str):
        return "SIN RECURSO"
    s = str(recurso_str).upper().strip()
    s = re.sub(r'^(BOL[A-Z])\s+(\d+)', r'\1-\2', s)
    match = re.search(r'(BOL[A-Z]-\d+)', s)
    if match:
        return match.group(1)
    return s


def get_shift_profile(recurso_base: str):
    if recurso_base in BOLE_ESPECIALES:
        return ("L-V 07:30-16:30 (Enlace CELSIA)", "FIJO_BOLE", 7*60+30, 16*60+30, 8.0)
    if recurso_base == "BOLV-398":
        return ("Fijo 08:00-16:00 (7h netas)", "FIJO", 8*60, 16*60, 7.0)
    if recurso_base in {"BOLM-348", "BOLM-353"}:
        return ("Fijo 09:00-17:00 (7h netas)", "FIJO", 9*60, 17*60, 7.0)
    if recurso_base in ROTATIVAS_3T_CENTRO:
        return ("Rotativo 3T Urbano (6-14 / 14-22 / 22-6)", "ROTATIVO_3T", None, None, 8.0)
    if recurso_base in ROTATIVAS_2T_NORTE:
        return ("Rotativo 2T Norte (6-14 / 14-22)", "ROTATIVO_2T", None, None, 8.0)
    if recurso_base in ROTATIVAS_3T_NORTE:
        return ("Rotativo 3T Norte (6-14 / 14-22 / 22-6)", "ROTATIVO_3T", None, None, 8.0)
    return ("Fijo 07:00-15:00 (7h netas)", "FIJO", 7*60, 15*60, 7.0)


def infer_daily_shift_window(tipo_turno, min_ini_fijo, min_fin_fijo, mins_inicio_dia):
    if tipo_turno in {"FIJO", "FIJO_BOLE"}:
        return min_ini_fijo, min_fin_fijo, f"{min_ini_fijo//60:02d}:{min_ini_fijo%60:02d} a {min_fin_fijo//60:02d}:{min_fin_fijo%60:02d}"
    
    valid_mins = [m for m in mins_inicio_dia if pd.notna(m)]
    first_m = min(valid_mins) if valid_mins else 360

    if tipo_turno == "ROTATIVO_2T":
        if first_m < 11 * 60 + 30:
            return 6*60, 14*60, "Turno 1 (06:00 a 14:00)"
        else:
            return 14*60, 22*60, "Turno 2 (14:00 a 22:00)"

    if tipo_turno == "ROTATIVO_3T":
        has_night = any(m >= 21*60 + 30 or m < 5*60 for m in valid_mins)
        has_morning = any(5*60 <= m < 11*60 + 30 for m in valid_mins)
        if has_night and not has_morning:
            return 22*60, 30*60, "Turno 3 Nocturno (22:00 a 06:00)"
        elif first_m < 11*60 + 30:
            return 6*60, 14*60, "Turno 1 Mañana (06:00 a 14:00)"
        else:
            return 14*60, 22*60, "Turno 2 Tarde (14:00 a 22:00)"

    return 7*60, 15*60, "07:00 a 15:00"


def classify_urban_vs_rural(row):
    zona_of = str(row.get('Zona_Oficial', '')).upper()
    if zona_of == "IBAGUE URBANA":
        return "🏙️ Ibagué Casco Urbano"
    
    txt = f"{row.get('Dirección', '')} {row.get('Descripcion_Orden', '')} {row.get('Observaciones', '')}".upper()
    is_rural = any(k in txt for k in [
        "VDA", "VEREDA", "FCA", "FINCA", "HDA", "HACIENDA", "CORREGIMIENTO",
        "PARCELA", "SECTOR RURAL", "KMT", "KM ", "RAMAL", "CRUCE"
    ])
    is_urban = any(k in txt for k in [
        "CRA", "CARRERA", "CLL", "CALLE", "BARRIO", "B/ ", "B.", "CENTRO",
        "MZ", "MANZANA", "URB ", "URBANIZACION", "CONJUNTO", "DIAGONAL", "TRANSVERSAL", "APTO"
    ])
    
    if is_urban and not is_rural:
        return "🏘️ Casco Urbano Municipio"
    if is_rural:
        return "🌲 Zona Veredal / Rural"
    if zona_of == "IBAGUE RURAL":
        return "🌲 Zona Veredal / Rural"
    return "📍 General Municipio"


def extract_lat_lon(coord_str):
    if pd.isna(coord_str):
        return np.nan, np.nan
    s = str(coord_str)
    m = re.search(r'lat:([-\d\.]+),lng:([-\d\.]+)', s)
    if m:
        try:
            return float(m.group(1)), float(m.group(2))
        except Exception:
            return np.nan, np.nan
    return np.nan, np.nan


def calc_reaction_minutes(row):
    asig = row.get('Hora_Asignacion')
    ini = row.get('Inicio')
    if pd.isna(asig) or pd.isna(ini):
        return np.nan
    try:
        asig_str = str(asig).strip()
        ini_str = str(ini).strip()
        m_asig = re.search(r'(\d{1,2}):(\d{2})', asig_str)
        m_ini = re.search(r'^(\d{1,2}):(\d{2})', ini_str)
        if m_asig and m_ini:
            min_a = int(m_asig.group(1)) * 60 + int(m_asig.group(2))
            min_i = int(m_ini.group(1)) * 60 + int(m_ini.group(2))
            diff = min_i - min_a
            if 0 <= diff <= 600:
                return float(diff)
    except Exception:
        pass
    return np.nan


def classify_observaciones(obs_text):
    if pd.isna(obs_text) or not str(obs_text).strip():
        return "Sin Observación"
    t = str(obs_text).upper()
    tags = []
    if any(k in t for k in ["L.V", "LINEA VIVA", "LÍNEA VIVA", "VEGETACION", "VEGETACIÓN", "PODA", "ARBOL", "ÁRBOL", "PALMA", "GUADUA", "RAMA"]):
        tags.append("Vegetación / Línea Viva")
    if any(k in t for k in ["LLUVIA", "TORMENTA", "DIFICIL ACCESO", "DIFÍCIL ACCESO", "MAL TIEMPO", "DERRUMBE"]):
        tags.append("Clima / Difícil Acceso")
    if any(k in t for k in ["SERVICIO NORMAL", "NO CONTESTA", "AUSENTE", "FALSA ALARMA"]):
        tags.append("Servicio Normal / Usuario Ausente")
    if any(k in t for k in ["FUSIBLE", "CAÑUELA", "CORTACIRCUITO", "SECCIONAMIENTO", "TRANSFORMADOR", "ACOMETIDA", "PUENTE", " PIN ", "AISLADOR"]):
        tags.append("Maniobra / Material Red")
    if not tags:
        return "Gestión General"
    return " | ".join(tags)


def detect_root_causes_multicausal(row):
    textos = [
        str(row.get('Observaciones', '')),
        str(row.get('Comentarios_Suspension', '')),
        str(row.get('Comentarios_No_Realizado', '')),
        str(row.get('Comentarios_Cancelacion', '')),
        str(row.get('Descripcion_Orden', ''))
    ]
    t = " ".join([x for x in textos if x and x != 'nan']).upper()
    if not t.strip():
        return ["🔍 Operación / Sin Causa Explícita"]
    
    causas = []
    if any(k in t for k in ["VEGETACION", "VEGETACIÓN", "ARBOL", "ÁRBOL", "RAMA", "GUADUA", "PALMA", "PODA", "MALEZA", "CHAMIZA", "BAMBU", "BAMBÚ"]):
        causas.append("🌿 Vegetación / Árboles")
    if any(k in t for k in ["LLUVIA", "TORMENTA", "AGUACERO", "INVIERNO", "MAL TIEMPO", "BORRASCA", "VENDAVAL", "INUNDACION"]):
        causas.append("🌧️ Lluvias / Mal Tiempo")
    if any(k in t for k in ["VIENTO", "VIENTOS", "VENTARRON", "VENTARRÓN", "BRISA FUERTE"]):
        causas.append("💨 Fuertes Vientos")
    if any(k in t for k in ["DESCARGA", "RAYO", "ATMOSFERICA", "ATMOSFÉRICA", "TRUENO", "DPS", "PARARRAYO"]):
        causas.append("⚡ Descargas Atmosféricas")
    if any(k in t for k in ["ANIMAL", "AVE ", "AVES", "PAJARO", "PÁJARO", "ARDILLA", "IGUANA", "SERPIENTE", "CULEBRA", "GATO", "ZARIGÜEYA", "CHUCHA", "MONO", "GARZA", "GALLINAZO", "NIDO"]):
        causas.append("🐾 Animales / Fauna")
    if any(k in t for k in ["VEHICULO", "VEHÍCULO", "CAMION", "CAMIÓN", "CARRO", "TERCERO", "VANDALISMO", "HURTO", "ROBO", "CHOQUE", "ESTRELL", "GRUA", "GRÚA", "VOLQUETA", "RETRO", "COMETA"]):
        causas.append("🚗 Terceros / Vehículos")
    if any(k in t for k in ["PUNTO CALIENTE", "AISLADOR", "PIN DE PORCELANA", "SULFATA", "DETERIOR", "MAL ESTADO", "FATIGA", "QUEMAD", "ROTO", "REVENTAD", "CUERDA CAIDA", "CUERDAS CAIDAS", "VELA CAIDA", "VELAS CAIDAS", "CAÑUELA", "CORTACIRCUITO"]):
        causas.append("🔧 Deterioro / Falla de Material")
    if any(k in t for k in ["VOLTAJE", "SUBE Y BAJA", "BORNERA", "ACOMETIDA", "MEDIDOR"]):
        causas.append("🔌 Variación Voltaje / Acometida BT")

    if not causas:
        return ["🔍 Operación / Sin Causa Explícita"]
    return causas


def classify_labor_tecnica(row):
    """Clasifica el tipo de labor técnica ejecutada en sitio basada en los textos."""
    textos = [
        str(row.get('Observaciones', '')),
        str(row.get('Comentarios_Suspension', '')),
        str(row.get('Comentarios_No_Realizado', '')),
        str(row.get('Descripcion_Orden', ''))
    ]
    t = " ".join([x for x in textos if x and x != 'nan']).upper()
    
    if any(k in t for k in ["RETENSIONA", "TEMPLADO", "EMPALME", "LÍNEA REVENTADA", "LINEA REVENTADA", "PUENTE ROTO", "PUENTE REVENTADO", "CUERDA CAIDA", "CUERDAS CAIDAS", "ACOMETIDA REVENTADA"]):
        return "🧗 Retensionado / Empalme / Línea Reventada"
    if any(k in t for k in ["PODA", "RETIRO DE VEGETACIÓN", "RETIRO DE VEGETACION", "DESRAME", "ARBOL", "ÁRBOL", "GUADUA", "PALMA", "RAMA"]):
        return "🌿 Poda / Despeje Vegetación"
    if any(k in t for k in ["AISLADOR", "PIN DE PORCELANA", "CORTACIRCUITO", "DPS", "PARARRAYO", "BORNERA", "CRUCETA", "PUNTO CALIENTE"]):
        return "🔩 Cambio / Adecuación Componentes"
    if any(k in t for k in ["FUSIBLE", "CAÑUELA", "VELA", "SECCIONAMIENTO", "RECONECTADOR", "CIERRE"]):
        return "⚡ Maniobra Rápida en Fusible / Cañuela"
    if any(k in t for k in ["INSPECCIÓN VISUAL", "INSPECCION VISUAL", "CONTESTA", "SERVICIO NORMAL", "SIN NOVEDAD"]):
        return "🔎 Inspección / Servicio Normal"
    return "🔧 Intervención General en Red"


def recommend_action_from_causes(causes_str: str) -> str:
    recs = []
    if "Vegetación" in causes_str:
        recs.append("🌲 Programar Poda / Despeje Red / Apoyo L.V.")
    if "Deterioro" in causes_str:
        recs.append("🔧 Inspección Termográfica / Cambio Aislamiento o Herrajes")
    if "Animales" in causes_str:
        recs.append("🐾 Instalar Dispositivos Antifauna / Cubiertas")
    if "Descargas" in causes_str:
        recs.append("⚡ Revisar DPS / Puesta a Tierra (SPT)")
    if "Terceros" in causes_str:
        recs.append("🚗 Validar Altura / Señalización / Adecuación Red")
    if "Lluvias" in causes_str or "Vientos" in causes_str:
        recs.append("🌧️ Revisión de Tensionado y Amarres de Línea")
    if "Voltaje" in causes_str:
        recs.append("🔌 Balanceo de Cargas / Revisión Conexiones BT")
    if not recs:
        return "🔎 Inspección Técnica General de Nodo"
    return " + ".join(recs[:2])


def classify_cancelacion(row):
    estado = str(row.get('Estado_Actividad', '')).lower().strip()
    if estado != 'cancelada':
        return "No Aplica (No Cancelada)"
    
    motivo = str(row.get('Motivo_Cancelacion', '')).upper()
    coment = str(row.get('Comentarios_Cancelacion', '')).upper()
    obs = str(row.get('Observaciones', '')).upper()
    texto_total = f"{motivo} {coment} {obs}"

    if "EGAM" in texto_total:
        return "🖥️ Cancelado por EGAM"
    if "RPA" in texto_total or "AGRUPACION" in texto_total or "AGRUPACIÓN" in texto_total or "SISTEMA EXTERNO" in motivo:
        return "🤖 Agrupación Automática RPA"
    if "OTRO AVISO" in motivo or "OTRO TIQUETE" in motivo or "ADMS-INC" in coment:
        return "🔗 Agrupado en otro ADMS-INC"
    if "CONFIRMADO CON CLIENTE" in motivo or "SERVICIO NORMAL" in texto_total or "TELEFÓNICA" in texto_total or "TELEFONICA" in texto_total:
        return "📞 Operativo: Servicio Confirmado Cliente"
    if "SECTOR A" in texto_total:
        return "⚠️ Escalamiento Sector A"
    return "👷 Operativo / Otros Motivos"


def extract_nodes_preserve_exact(row):
    textos = [
        str(row.get('Observaciones', '')),
        str(row.get('Comentarios_Suspension', '')),
        str(row.get('Comentarios_No_Realizado', '')),
        str(row.get('Comentarios_Cancelacion', '')),
        str(row.get('Descripcion_Orden', '')),
        str(row.get('Numero_Descargo', ''))
    ]
    full_text = " ".join([t for t in textos if t and t != 'nan']).upper()
    if not full_text.strip():
        return []
    pattern = r'\b(?:PF6\d{5,9}[A-Z0-9-]*|6\d{5,9}[A-Z0-9-]*|RB\d{2,6}[A-Z0-9-]*|RC\d{2,6}[A-Z0-9-]*|CD\d{3,7}[A-Z0-9-]*|S\d{4,6}[A-Z0-9-]*)\b'
    found = re.findall(pattern, full_text)
    return list(dict.fromkeys(found))


def classify_node_type(node_code: str) -> str:
    c = str(node_code).upper()
    if c.startswith("RB") or c.startswith("RC"):
        return "Reconectador (RB / RC)"
    if c.startswith("CD"):
        return "Cortacircuito / Transformador (CD)"
    if c.startswith("S"):
        return "Seccionamiento (S)"
    if c.startswith("PF") or c.startswith("6"):
        return "Punto Físico / Nodo (6 / PF)"
    return "Otro Equipo"


def clean_dataframe(df: pd.DataFrame, source_name: str = "") -> pd.DataFrame:
    if df.empty:
        return df
    
    df = df.copy()
    
    col_mapping = {
        'Estado de actividad': 'Estado_Actividad',
        'Tiempo de viaje': 'Tiempo_Viaje_Raw',
        'Duración': 'Duracion_Raw',
        'ID de actividad': 'ID_Actividad',
        'Orden de trabajo': 'Orden_Trabajo',
        'Zona de trabajo': 'Zona_Trabajo_WFM',
        'Tipo de actividad': 'Tipo_Actividad_Base',
        'Tipo de actividad.1': 'Subtipo_Actividad',
        'Descripción de la orden': 'Descripcion_Orden',
        'Motivo de Cancelación': 'Motivo_Cancelacion',
        'Comentarios de Cancelación': 'Comentarios_Cancelacion',
        'Comentarios de Suspensión': 'Comentarios_Suspension',
        'Comentarios No Realizado': 'Comentarios_No_Realizado',
        'Fecha de Generación': 'Fecha_Generacion',
        'Hora de asignación de actividad': 'Hora_Asignacion',
        'Número de Descargo': 'Numero_Descargo',
        'Ubicación Inicio Actividad': 'Ubicacion_Inicio',
        'Ubicación Completado': 'Ubicacion_Fin'
    }
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)

    if 'Orden_Trabajo' not in df.columns:
        df['Orden_Trabajo'] = 'Sin OT'
    else:
        df['Orden_Trabajo'] = df['Orden_Trabajo'].fillna('Sin OT').astype(str).str.strip()

    if 'ID_Actividad' not in df.columns:
        df['ID_Actividad'] = df.index.astype(str)
    else:
        df['ID_Actividad'] = df['ID_Actividad'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

    if 'Recurso' in df.columns:
        df['Recurso'] = df['Recurso'].fillna('Sin Recurso').astype(str).str.strip()
    else:
        df['Recurso'] = 'Sin Recurso'
        
    df['Recurso_Base'] = df['Recurso'].apply(normalize_recurso_key)

    sectores_asignados, zonas_asignadas = [], []
    desc_horarios, tipos_turno, hrs_netas_base = [], [], []

    for idx, row in df.iterrows():
        rec_b = row['Recurso_Base']
        if rec_b in MAESTRO_ZONAS:
            sec_of, zon_of = MAESTRO_ZONAS[rec_b]
        else:
            sec_col = str(row.get('Sector', '')).upper()
            if 'NORTE' in sec_col or 'NORTE' in source_name.upper():
                sec_of = 'NORTE'
            elif 'CENTRO' in sec_col or 'CENTRO' in source_name.upper():
                sec_of = 'CENTRO'
            else:
                sec_of = 'OTRO'
            zon_of = str(row.get('Zona_Trabajo_WFM', 'SIN ZONA ASIGNADA')).upper()
        
        d_hor, t_tur, _, _, h_net = get_shift_profile(rec_b)
        sectores_asignados.append(sec_of)
        zonas_asignadas.append(zon_of)
        desc_horarios.append(d_hor)
        tipos_turno.append(t_tur)
        hrs_netas_base.append(h_net)

    df['Sector'] = sectores_asignados
    df['Zona_Oficial'] = zonas_asignadas
    df['Regla_Horario'] = desc_horarios
    df['Tipo_Turno_Regla'] = tipos_turno
    df['Horas_Netas_Turno_Base'] = hrs_netas_base

    if 'Fecha' in df.columns:
        fechas_dt = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Fecha_Str'] = fechas_dt.dt.strftime('%Y-%m-%d').fillna('Sin Fecha')
        df['Anio'] = fechas_dt.dt.year.fillna(0).astype(int).astype(str).replace('0', 'Sin Año')
        df['Mes_Num'] = fechas_dt.dt.month.fillna(0).astype(int)
        df['Mes_Nombre'] = df['Mes_Num'].map(MESES_ES).fillna('Sin Mes')
        df['Dia_Semana_Num'] = fechas_dt.dt.dayofweek.fillna(0).astype(int)
    else:
        df['Fecha_Str'] = 'Sin Fecha'
        df['Anio'] = 'Sin Año'
        df['Mes_Nombre'] = 'Sin Mes'
        df['Dia_Semana_Num'] = 0

    df['Minutos_Viaje'] = df['Tiempo_Viaje_Raw'].apply(convert_time_to_minutes) if 'Tiempo_Viaje_Raw' in df.columns else 0.0
    df['Minutos_Duracion'] = df['Duracion_Raw'].apply(convert_time_to_minutes) if 'Duracion_Raw' in df.columns else 0.0

    df['Ini_Min_Dia'] = df['Inicio'].apply(hour_str_to_min_of_day) if 'Inicio' in df.columns else np.nan
    df['Fin_Min_Dia'] = df['Finalización'].apply(hour_str_to_min_of_day) if 'Finalización' in df.columns else np.nan

    if 'Inicio' in df.columns and 'Finalización' in df.columns:
        dt_ini_s = pd.to_datetime(df['Fecha_Str'] + ' ' + df['Inicio'].fillna('').astype(str).str.strip(), errors='coerce')
        dt_fin_s = pd.to_datetime(df['Fecha_Str'] + ' ' + df['Finalización'].fillna('').astype(str).str.strip(), errors='coerce')
        dt_fin_adj = np.where(
            (dt_fin_s.notna()) & (dt_ini_s.notna()) & (dt_fin_s < dt_ini_s),
            dt_fin_s + pd.Timedelta(days=1),
            np.where(
                (dt_fin_s.notna()) & (dt_ini_s.notna()) & (dt_fin_s == dt_ini_s),
                dt_fin_s + pd.Timedelta(minutes=2),
                dt_fin_s
            )
        )
        df['DT_Inicio'] = pd.to_datetime(dt_ini_s)
        df['DT_Fin'] = pd.to_datetime(dt_fin_adj)
    else:
        df['DT_Inicio'] = pd.NaT
        df['DT_Fin'] = pd.NaT

    if 'Fecha_Generacion' in df.columns and 'Hora_Asignacion' in df.columns:
        dt_gen = pd.to_datetime(df['Fecha_Generacion'], dayfirst=True, errors='coerce')
        dt_asig = pd.to_datetime(df['Hora_Asignacion'], errors='coerce')
        diff_cola = (dt_asig - dt_gen).dt.total_seconds() / 60.0
        df['Minutos_Cola_EGAM'] = diff_cola.where((diff_cola >= 0) & (diff_cola <= 14400), np.nan)
    else:
        df['Minutos_Cola_EGAM'] = np.nan

    if 'Estado_Actividad' in df.columns:
        df['Estado_Actividad'] = df['Estado_Actividad'].fillna('No Definido').astype(str).str.strip().str.capitalize()
    else:
        df['Estado_Actividad'] = 'No Definido'

    if 'Subtipo_Actividad' not in df.columns:
        df['Subtipo_Actividad'] = df.get('Tipo_Actividad_Base', 'General')
    df['Subtipo_Actividad'] = df['Subtipo_Actividad'].fillna('General').astype(str).str.strip()

    df['Categoria_Labor'] = df['Subtipo_Actividad'].apply(
        lambda x: 'Rutina / Administrativa' if str(x).upper() in ACTIVIDADES_RUTINA else 'Operativa (Daños / OT)'
    )

    for c_txt in ['Observaciones', 'Comentarios_Cancelacion', 'Comentarios_Suspension', 'Comentarios_No_Realizado', 'Motivo_Cancelacion', 'Descripcion_Orden', 'Numero_Descargo']:
        if c_txt not in df.columns:
            df[c_txt] = ''
        else:
            df[c_txt] = df[c_txt].fillna('').astype(str)

    df['Etiqueta_Hallazgo'] = df['Observaciones'].apply(classify_observaciones)
    df['Origen_Cancelacion'] = df.apply(classify_cancelacion, axis=1)
    df['Entorno_Ubicacion'] = df.apply(classify_urban_vs_rural, axis=1)

    df['Lista_Nodos'] = df.apply(extract_nodes_preserve_exact, axis=1)
    df['Nodos_Detectados'] = df['Lista_Nodos'].apply(lambda lst: ", ".join(lst) if lst else "")
    df['Lista_Causas_Raiz'] = df.apply(detect_root_causes_multicausal, axis=1)
    df['Causas_Raiz_Texto'] = df['Lista_Causas_Raiz'].apply(lambda lst: " | ".join(lst))
    df['Labor_Tecnica'] = df.apply(classify_labor_tecnica, axis=1)

    df['Minutos_Reaccion'] = df.apply(calc_reaction_minutes, axis=1)

    # -------------------------------------------------------------------------
    # CÁLCULO EXACTO AL MINUTO DE JORNADA ORDINARIA VS TIEMPO EXTENDIDO / EXTRAS
    # -------------------------------------------------------------------------
    df['Clasificacion_Jornada'] = "En Jornada Ordinaria"
    df['Turno_Detectado_Dia'] = ""
    df['Minutos_En_Jornada'] = 0.0
    df['Minutos_Extra_PostTurno'] = 0.0

    for (rec, f_str), group in df.groupby(['Recurso', 'Fecha_Str']):
        rec_b = group['Recurso_Base'].iloc[0]
        _, t_turno, m_ini_fijo, m_fin_fijo, _ = get_shift_profile(rec_b)
        
        w_ini, w_fin, label_turno = infer_daily_shift_window(
            t_turno, m_ini_fijo, m_fin_fijo, group['Ini_Min_Dia'].tolist()
        )
        df.loc[group.index, 'Turno_Detectado_Dia'] = label_turno

        for idx, r in group.iterrows():
            total_row_min = float(r['Minutos_Viaje'] + r['Minutos_Duracion'])

            if rec_b in BOLE_ESPECIALES and r['Dia_Semana_Num'] in [5, 6]:
                df.loc[idx, 'Clasificacion_Jornada'] = "🚨 Caso Excepcional BOLE (Fin de Semana)"
                df.loc[idx, 'Minutos_En_Jornada'] = 0.0
                df.loc[idx, 'Minutos_Extra_PostTurno'] = total_row_min
                continue

            sub_up = str(r['Subtipo_Actividad']).upper()
            if sub_up in ["INICIO TURNO", "FIN TURNO", "ALIMENTACIÓN", "ALIMENTACION"]:
                df.loc[idx, 'Clasificacion_Jornada'] = "En Jornada Ordinaria"
                df.loc[idx, 'Minutos_En_Jornada'] = 0.0
                df.loc[idx, 'Minutos_Extra_PostTurno'] = 0.0
                continue

            ini_m = r['Ini_Min_Dia']
            fin_m = r['Fin_Min_Dia']

            if pd.isna(ini_m) and pd.isna(fin_m):
                df.loc[idx, 'Clasificacion_Jornada'] = "Sin Hora Inicio (Cancelada / Pendiente)"
                df.loc[idx, 'Minutos_En_Jornada'] = 0.0
                df.loc[idx, 'Minutos_Extra_PostTurno'] = 0.0
                continue

            if w_fin > 1440:
                df.loc[idx, 'Clasificacion_Jornada'] = "En Jornada Ordinaria"
                df.loc[idx, 'Minutos_En_Jornada'] = total_row_min
                df.loc[idx, 'Minutos_Extra_PostTurno'] = 0.0
                continue

            if pd.notna(ini_m) and (ini_m >= w_fin or ini_m < w_ini - 30):
                df.loc[idx, 'Clasificacion_Jornada'] = "🌙 Caso B: Reactivación Post-Turno (Inicia Después del Turno)"
                df.loc[idx, 'Minutos_En_Jornada'] = 0.0
                df.loc[idx, 'Minutos_Extra_PostTurno'] = total_row_min

            elif pd.notna(ini_m) and pd.notna(fin_m) and ini_m < w_fin and fin_m > w_fin:
                df.loc[idx, 'Clasificacion_Jornada'] = "⏱️ Caso A: Tiempo Extendido (Cruza Hora Fin de Turno)"
                min_despues_cierre = float(fin_m - w_fin)
                min_extra_calc = min(total_row_min, max(1.0, min_despues_cierre))
                min_ord_calc = max(0.0, total_row_min - min_extra_calc)
                df.loc[idx, 'Minutos_En_Jornada'] = min_ord_calc
                df.loc[idx, 'Minutos_Extra_PostTurno'] = min_extra_calc

            else:
                df.loc[idx, 'Clasificacion_Jornada'] = "En Jornada Ordinaria"
                df.loc[idx, 'Minutos_En_Jornada'] = total_row_min
                df.loc[idx, 'Minutos_Extra_PostTurno'] = 0.0

    lats, lons = [], []
    for idx, row in df.iterrows():
        lat, lon = extract_lat_lon(row.get('Ubicacion_Fin'))
        if pd.isna(lat):
            lat, lon = extract_lat_lon(row.get('Ubicacion_Inicio'))
        lats.append(lat)
        lons.append(lon)
    df['Lat'] = lats
    df['Lon'] = lons

    return df


@st.cache_data(ttl=120, show_spinner=False)
def load_data_from_url(drive_url: str):
    try:
        direct_url = parse_google_drive_url(drive_url)
        response = requests.get(direct_url, timeout=30)
        response.raise_for_status()
        excel_bytes = io.BytesIO(response.content)
        
        xl = pd.ExcelFile(excel_bytes)
        dfs = []
        for sheet in xl.sheet_names:
            sub_df = xl.parse(sheet)
            sub_df = clean_dataframe(sub_df, source_name=sheet)
            dfs.append(sub_df)
            
        consolidado = pd.concat(dfs, ignore_index=True)
        if 'ID_Actividad' in consolidado.columns:
            consolidado = consolidado.drop_duplicates(subset=['ID_Actividad'], keep='last')
        return consolidado, None
    except Exception as e:
        return None, str(e)


def get_semaforo_badge(val):
    if val >= 85.0:
        return f'<span class="badge-green">🟢 {val:.1f}% (Óptimo)</span>'
    elif val >= 50.0:
        return f'<span class="badge-yellow">🟡 {val:.1f}% (Seguimiento)</span>'
    else:
        return f'<span class="badge-red">🔴 {val:.1f}% (Crítico)</span>'


def multiselect_with_all(label, options, key_prefix, default_all=True):
    clean_opts = sorted([str(x) for x in options if pd.notna(x) and str(x).strip() != ''])
    sel = st.multiselect(
        label,
        options=clean_opts,
        default=[] if default_all else clean_opts[:1],
        placeholder="Todos seleccionados (o escoge varios)...",
        key=f"ms_{key_prefix}"
    )
    return clean_opts if len(sel) == 0 else sel


# -----------------------------------------------------------------------------
# 5. BARRA LATERAL: CONFIGURACIÓN Y CARGUE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ Control Operativo BOL")
    st.caption("Gestión de Turnos, Standby, Nodos y Causas")
    st.markdown("---")
    
    st.markdown("**1. Enlace de Datos (Google Drive)**")
    drive_url = st.text_input(
        "URL del Excel Consolidado:",
        value=URL_GOOGLE_DRIVE_DEFAULT,
        help="Enlace compartido con permiso de lectura."
    )
    
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with c_b2:
        if st.button("Limpiar Caché", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with st.expander("📂 Cargue Manual de Emergencia (.xlsx)"):
        uploaded_files = st.file_uploader(
            "Subir archivos locales:",
            type=["xlsx"],
            accept_multiple_files=True
        )

# -----------------------------------------------------------------------------
# 6. OBTENCIÓN DE DATOS
# -----------------------------------------------------------------------------
df_raw = None

if uploaded_files:
    dfs = []
    for f in uploaded_files:
        xls_temp = pd.ExcelFile(f)
        for sh in xls_temp.sheet_names:
            t_df = xls_temp.parse(sh)
            t_df = clean_dataframe(t_df, source_name=f"{f.name}_{sh}")
            dfs.append(t_df)
    df_raw = pd.concat(dfs, ignore_index=True)
    if 'ID_Actividad' in df_raw.columns:
        df_raw = df_raw.drop_duplicates(subset=['ID_Actividad'], keep='last')
elif drive_url and "TU_ID_DE_ARCHIVO" not in drive_url:
    with st.spinner("Sincronizando base operativa desde Google Drive..."):
        df_raw, err = load_data_from_url(drive_url)
        if err:
            st.error(f"Error al leer el enlace de Google Drive: {err}")
            st.info("Verifica que el archivo tenga el permiso: 'Cualquier persona con el enlace puede ver'.")
            st.stop()
else:
    st.info("👋 **Bienvenido al Centro de Control Operativo BOL.** Configura tu enlace de Google Drive en la barra lateral o sube tus archivos Excel en el cargador manual.")
    st.stop()

if df_raw is None or df_raw.empty:
    st.warning("No se encontraron registros en la fuente de datos.")
    st.stop()


# -----------------------------------------------------------------------------
# 7. FILTROS EN CASCADA (BARRA LATERAL)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("**2. Modo de Evaluación y Horarios**")
    
    modo_enfoque = st.radio(
        "Enfoque de Actividades:",
        options=[
            "Solo Operativas (Daños / OT)",
            "Todas las Actividades Consolidadas",
            "Solo Rutina / Administrativas"
        ],
        index=0
    )
    
    usar_horario_oficial = st.checkbox(
        "Usar Horario Oficial específico de cada Brigada (7h / 8h según turno)",
        value=True
    )
    
    if not usar_horario_oficial:
        horas_turno_manual = st.slider("Jornada Manual General (Horas):", 6.0, 12.0, 8.0, 0.5)
    else:
        horas_turno_manual = None

    excluir_rpa_egam_efectividad = st.checkbox(
        "Excluir canceladas por EGAM / RPA del cálculo de Efectividad",
        value=False
    )

    st.markdown("---")
    st.markdown("**3. Filtros de Tiempo (Multiselección)**")
    
    sel_anios = multiselect_with_all("Año(s):", df_raw['Anio'].unique(), "anio")
    df_f = df_raw[df_raw['Anio'].isin(sel_anios)].copy()
    
    sel_meses = multiselect_with_all("Mes(es):", df_f['Mes_Nombre'].unique(), "mes")
    df_f = df_f[df_f['Mes_Nombre'].isin(sel_meses)].copy()
    
    sel_fechas = multiselect_with_all("Día(s) / Fecha(s):", df_f['Fecha_Str'].unique(), "fecha")
    df_f = df_f[df_f['Fecha_Str'].isin(sel_fechas)].copy()

    sel_jornadas = multiselect_with_all(
        "Franja / Condición de Jornada (Ordinaria vs. Post-Turno):",
        df_f['Clasificacion_Jornada'].unique(),
        "jornada"
    )
    df_f = df_f[df_f['Clasificacion_Jornada'].isin(sel_jornadas)].copy()

    st.markdown("---")
    st.markdown("**4. Filtros Geográficos, Operativos y Causa Raíz**")
    
    sel_sectores = multiselect_with_all("Sector(es):", df_f['Sector'].unique(), "sector")
    df_f = df_f[df_f['Sector'].isin(sel_sectores)].copy()
    
    sel_zonas = multiselect_with_all("Zona(s) Oficiales:", df_f['Zona_Oficial'].unique(), "zona")
    df_f = df_f[df_f['Zona_Oficial'].isin(sel_zonas)].copy()
    
    sel_recursos = multiselect_with_all("Brigada(s) / Recurso BOL:", df_f['Recurso'].unique(), "recurso")
    df_f = df_f[df_f['Recurso'].isin(sel_recursos)].copy()

    df_contexto_turno = df_f.copy()

    if modo_enfoque == "Solo Operativas (Daños / OT)":
        df_f = df_f[df_f['Categoria_Labor'] == 'Operativa (Daños / OT)'].copy()
    elif modo_enfoque == "Solo Rutina / Administrativas":
        df_f = df_f[df_f['Categoria_Labor'] == 'Rutina / Administrativa'].copy()

    sel_subtipos = multiselect_with_all("Tipo de Actividad (Detalle):", df_f['Subtipo_Actividad'].unique(), "subtipo")
    df_f = df_f[df_f['Subtipo_Actividad'].isin(sel_subtipos)].copy()

    sel_estados = multiselect_with_all("Estado(s) de Actividad:", df_f['Estado_Actividad'].unique(), "estado")
    df_f = df_f[df_f['Estado_Actividad'].isin(sel_estados)].copy()

    todas_causas_disp = sorted(list({c for lst in df_f['Lista_Causas_Raiz'] for c in lst}))
    sel_causas_global = multiselect_with_all("Causa(s) Raíz Detectadas:", todas_causas_disp, "causas_glob")
    if len(sel_causas_global) < len(todas_causas_disp):
        df_f = df_f[df_f['Lista_Causas_Raiz'].apply(lambda lst: any(c in sel_causas_global for c in lst))].copy()


# -----------------------------------------------------------------------------
# 8. PROCESAMIENTO DE INDICADORES Y RESUMEN POR BRIGADA
# -----------------------------------------------------------------------------
if df_f.empty:
    st.warning("No hay actividades que coincidan con la combinación de filtros seleccionada.")
    st.stop()

total_act = len(df_f)
fin_act = int((df_f['Estado_Actividad'].str.lower() == 'finalizada').sum())
canc_act = int((df_f['Estado_Actividad'].str.lower() == 'cancelada').sum())
susp_act = int((df_f['Estado_Actividad'].str.lower() == 'suspendida').sum())

canc_egam = int((df_f['Origen_Cancelacion'] == "🖥️ Cancelado por EGAM").sum())
canc_rpa = int((df_f['Origen_Cancelacion'] == "🤖 Agrupación Automática RPA").sum())

caso_a_cnt = int((df_f['Clasificacion_Jornada'] == "⏱️ Caso A: Tiempo Extendido (Cruza Hora Fin de Turno)").sum())
caso_b_cnt = int((df_f['Clasificacion_Jornada'] == "🌙 Caso B: Reactivación Post-Turno (Inicia Después del Turno)").sum())
total_horas_extra_global = df_f['Minutos_Extra_PostTurno'].sum() / 60.0

if excluir_rpa_egam_efectividad:
    denom_global = max(1, total_act - (canc_egam + canc_rpa))
    efectividad_global = (fin_act / denom_global * 100.0) if total_act > 0 else 0.0
else:
    efectividad_global = (fin_act / total_act * 100.0) if total_act > 0 else 0.0

prom_viaje_global = df_f['Minutos_Viaje'].mean() if total_act > 0 else 0.0
prom_faena_global = df_f['Minutos_Duracion'].mean() if total_act > 0 else 0.0

brigadas_activas = df_f['Recurso'].nunique()
dias_unicos = df_f['Fecha_Str'].nunique()

rec_stats = df_f.groupby(['Recurso', 'Sector', 'Zona_Oficial', 'Regla_Horario', 'Horas_Netas_Turno_Base']).agg(
    Dias_Activos=('Fecha_Str', 'nunique'),
    Total_Asignadas=('ID_Actividad', 'count'),
    Finalizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'finalizada').sum()),
    Canceladas=('Estado_Actividad', lambda x: (x.str.lower() == 'cancelada').sum()),
    Canc_EGAM=('Origen_Cancelacion', lambda x: (x == "🖥️ Cancelado por EGAM").sum()),
    Canc_RPA=('Origen_Cancelacion', lambda x: (x == "🤖 Agrupación Automática RPA").sum()),
    Suspendidas=('Estado_Actividad', lambda x: (x.str.lower() == 'suspendida').sum()),
    No_Realizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'no realizado').sum()),
    Min_Ord_Ocupado=('Minutos_En_Jornada', 'sum'),
    Min_Post_Turno=('Minutos_Extra_PostTurno', 'sum'),
    Eventos_Extension_A=('Clasificacion_Jornada', lambda x: (x == "⏱️ Caso A: Tiempo Extendido (Cruza Hora Fin de Turno)").sum()),
    Eventos_Reactivacion_B=('Clasificacion_Jornada', lambda x: (x == "🌙 Caso B: Reactivación Post-Turno (Inicia Después del Turno)").sum()),
    Prom_Viaje_Min=('Minutos_Viaje', 'mean'),
    Prom_Faena_Min=('Minutos_Duracion', 'mean'),
    Prom_Reaccion_Min=('Minutos_Reaccion', 'mean'),
    Prom_Cola_EGAM_Min=('Minutos_Cola_EGAM', 'mean')
).reset_index()

rutina_stats = df_contexto_turno.groupby('Recurso').agg(
    Dias_Turno_Real=('Fecha_Str', 'nunique'),
    Turno_Actual=('Turno_Detectado_Dia', lambda s: s.iloc[-1] if not s.empty else ""),
    Primer_Inicio=('Inicio', lambda s: sorted([str(v) for v in s.dropna() if ':' in str(v)])[0] if any(':' in str(v) for v in s.dropna()) else '--:--'),
    Ultimo_Fin=('Finalización', lambda s: sorted([str(v) for v in s.dropna() if ':' in str(v)])[-1] if any(':' in str(v) for v in s.dropna()) else '--:--')
).reset_index()

rec_stats = pd.merge(rec_stats, rutina_stats, on='Recurso', how='left')

rec_stats['Act_Por_Dia'] = (rec_stats['Total_Asignadas'] / rec_stats['Dias_Activos'].replace(0, 1)).round(1)
rec_stats['Fin_Por_Dia'] = (rec_stats['Finalizadas'] / rec_stats['Dias_Activos'].replace(0, 1)).round(1)

if excluir_rpa_egam_efectividad:
    denom_serie = (rec_stats['Total_Asignadas'] - (rec_stats['Canc_EGAM'] + rec_stats['Canc_RPA'])).replace(0, 1)
    rec_stats['Efectividad_%'] = ((rec_stats['Finalizadas'] / denom_serie) * 100.0).clip(0, 100).round(1)
else:
    rec_stats['Efectividad_%'] = ((rec_stats['Finalizadas'] / rec_stats['Total_Asignadas'].replace(0, 1)) * 100.0).round(1)

def clasificar_semaforo(v):
    if v >= 85.0:
        return "🟢 >= 85% (Óptimo)"
    elif v >= 50.0:
        return "🟡 50% - 84% (Regular)"
    else:
        return "🔴 < 50% (Crítico)"

rec_stats['Semaforo'] = rec_stats['Efectividad_%'].apply(clasificar_semaforo)

if usar_horario_oficial:
    rec_stats['Horas_Netas_Disponibles'] = (rec_stats['Dias_Turno_Real'].replace(0, 1) * rec_stats['Horas_Netas_Turno_Base']).round(2)
else:
    rec_stats['Horas_Netas_Disponibles'] = (rec_stats['Dias_Turno_Real'].replace(0, 1) * horas_turno_manual).round(2)

rec_stats['Horas_En_Jornada'] = (rec_stats['Min_Ord_Ocupado'] / 60.0).round(2)
rec_stats['Horas_Post_Turno'] = (rec_stats['Min_Post_Turno'] / 60.0).round(2)

rec_stats['Horas_Sin_Atender'] = (rec_stats['Horas_Netas_Disponibles'] - rec_stats['Horas_En_Jornada']).apply(lambda x: max(0.0, round(x, 2)))
rec_stats['Prom_Viaje_Min'] = rec_stats['Prom_Viaje_Min'].round(1)
rec_stats['Prom_Faena_Min'] = rec_stats['Prom_Faena_Min'].round(1)
rec_stats['Prom_Reaccion_Min'] = rec_stats['Prom_Reaccion_Min'].fillna(0.0).round(1)
rec_stats['Prom_Cola_EGAM_Min'] = rec_stats['Prom_Cola_EGAM_Min'].fillna(0.0).round(1)


# -----------------------------------------------------------------------------
# 9. ENCABEZADO, TARJETAS KPI Y BANNERS GEMELOS DE DIAGNÓSTICO
# -----------------------------------------------------------------------------
st.markdown("### ⚡ Centro de Control y Seguimiento Diario de Brigadas (BOL)")
st.caption(
    f"Modo activo: **{modo_enfoque}** | Días evaluados: **{dias_unicos}** | "
    f"Brigadas activas: **{brigadas_activas}** | Horario: **{'Oficial por Brigada (Corte exacto fin de turno)' if usar_horario_oficial else 'Manual'}**"
)

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Actividades Filtradas</div>
        <div class="metric-value">{total_act:,}</div>
        <div class="metric-sub">✅ {fin_act} Fin. | ❌ {canc_act} Canc. | ⏸️ {susp_act} Susp.</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    badge_html = get_semaforo_badge(efectividad_global)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Cumplimiento / Efectividad</div>
        <div class="metric-value">{efectividad_global:.1f}%</div>
        <div class="metric-sub">{badge_html}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    prom_dia_brig = rec_stats['Fin_Por_Dia'].mean() if not rec_stats.empty else 0.0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Productividad Diaria</div>
        <div class="metric-value">{prom_dia_brig:.1f}</div>
        <div class="metric-sub">Finalizadas / brigada / día ({rec_stats['Act_Por_Dia'].mean():.1f} asig.)</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Prom. Ruta / Faena</div>
        <div class="metric-value">{prom_viaje_global:.0f}m / {prom_faena_global:.0f}m</div>
        <div class="metric-sub">Viaje prom. vs Atención prom.</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Tiempo Extendido / Extras</div>
        <div class="metric-value">{total_horas_extra_global:.1f} <span style="font-size:1rem;color:#64748b;">hrs</span></div>
        <div class="metric-sub">⏱️ {caso_a_cnt} Ext. | 🌙 {caso_b_cnt} Reactivadas</div>
    </div>
    """, unsafe_allow_html=True)

with k6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Canceladas EGAM / RPA</div>
        <div class="metric-value">{canc_egam + canc_rpa}</div>
        <div class="metric-sub">🖥️ {canc_egam} EGAM | 🤖 {canc_rpa} RPA</div>
    </div>
    """, unsafe_allow_html=True)

# BANNERS GEMELOS EJECUTIVOS SIEMPRE VISIBLES ARRIBA
if not rec_stats.empty:
    col_al1, col_al2 = st.columns(2)
    with col_al1:
        top_sb = rec_stats.sort_values(by='Horas_Sin_Atender', ascending=False).iloc[0]
        criticas_rojas = len(rec_stats[rec_stats['Efectividad_%'] < 50.0])
        st.markdown(f"""
        <div class="alert-standby">
            ⚠️ <strong>Atención de Disponibilidad (Mayor Standby en Turno):</strong><br>
            La brigada con más tiempo sin labor en su horario es <strong>{top_sb['Recurso']}</strong> ({top_sb['Zona_Oficial']} - {top_sb['Turno_Actual']}) 
            con <strong>{top_sb['Horas_Sin_Atender']:.2f} horas</strong> disponibles sin actividad 
            (Laboró {top_sb['Horas_En_Jornada']:.2f} h de {top_sb['Horas_Netas_Disponibles']:.1f} h netas). 
            Brigadas en rojo (&lt;50%): <strong>{criticas_rojas}</strong>.
        </div>
        """, unsafe_allow_html=True)

    with col_al2:
        df_con_extra = rec_stats[rec_stats['Horas_Post_Turno'] > 0].sort_values(by='Horas_Post_Turno', ascending=False)
        if not df_con_extra.empty:
            top_ex = df_con_extra.iloc[0]
            lista_brig_extra = ", ".join([f"{r['Recurso']} ({r['Horas_Post_Turno']:.1f}h)" for _, r in df_con_extra.head(5).iterrows()])
            st.markdown(f"""
            <div class="alert-overtime">
                🌙 <strong>Control de Horas Extras / Tiempo Extendido Post-Turno:</strong><br>
                Se registran <strong>{len(df_con_extra)} brigada(s)</strong> trabajando después de su hora de salida ({total_horas_extra_global:.2f} hrs totales). 
                Mayor extensión: <strong>{top_ex['Recurso']}</strong> con <strong>{top_ex['Horas_Post_Turno']:.2f} h</strong> (cerró a las {top_ex['Ultimo_Fin']}).<br>
                <span style="font-size:0.8rem;color:#4c1d95;">Top Brigadas Post-Turno: {lista_brig_extra}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-overtime">
                🌙 <strong>Control de Horas Extras / Tiempo Extendido Post-Turno:</strong><br>
                Ninguna brigada en la selección actual supera su hora límite de salida de turno.
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 10. PESTAÑAS DE NAVEGACIÓN PROFESIONAL (9 PESTAÑAS DEDICADAS)
# -----------------------------------------------------------------------------
tab_brigadas, tab_post, tab_zonas, tab_labores, tab_tiempos, tab_nodos, tab_obs, tab_mapa, tab_datos = st.tabs([
    "👷 Control Brigadas, Standby y Extras",
    "🌙 Auditoría Post-Turno y Casco Urbano",
    "🗺️ Desempeño Zonas Oficiales",
    "🛠️ Labores Técnicas y Tiempos en Sitio",
    "⏱️ Cola EGAM, Gantt y Disciplina WFM",
    "⚡ Nodos Recurrentes y Radar de Causas",
    "🔍 Observaciones y EGAM/RPA",
    "📍 Mapa y Trazabilidad",
    "📋 Base Consolidada"
])

# ================= TAB 1: CONTROL DE BRIGADAS, STANDBY Y HORAS EXTRAS =================
with tab_brigadas:
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.markdown("##### ⏳ Top 15 Brigadas con Mayor Tiempo Sin Atender en su Turno (Standby Puro)")
        df_top_sb = rec_stats.sort_values(by='Horas_Sin_Atender', ascending=False).head(15)
        fig_sb = px.bar(
            df_top_sb,
            x='Horas_Sin_Atender',
            y='Recurso',
            color='Sector',
            orientation='h',
            text='Horas_Sin_Atender',
            hover_data=['Zona_Oficial', 'Regla_Horario', 'Turno_Actual', 'Horas_En_Jornada', 'Horas_Post_Turno'],
            color_discrete_map={'CENTRO': '#0f172a', 'NORTE': '#2563eb', 'OTRO': '#64748b'},
            labels={'Horas_Sin_Atender': 'Horas Sin Atender en Turno (Standby)', 'Recurso': 'Brigada'}
        )
        fig_sb.update_traces(texttemplate='%{text:.1f} h', textposition='outside')
        fig_sb.update_layout(yaxis=dict(autorange="reversed"), height=390, margin=dict(t=10, b=10, l=10, r=40))
        st.plotly_chart(fig_sb, use_container_width=True)

    with col_b2:
        st.markdown("##### 🌙 Top Brigadas con Tiempo Extendido / Post-Turno (Soporte Horas Extras)")
        df_top_ext = rec_stats[rec_stats['Horas_Post_Turno'] > 0].sort_values(by='Horas_Post_Turno', ascending=False).head(15)
        if not df_top_ext.empty:
            fig_ext = px.bar(
                df_top_ext,
                x='Horas_Post_Turno',
                y='Recurso',
                color='Zona_Oficial',
                orientation='h',
                text='Horas_Post_Turno',
                hover_data=['Turno_Actual', 'Ultimo_Fin', 'Eventos_Extension_A', 'Eventos_Reactivacion_B'],
                labels={'Horas_Post_Turno': 'Horas Después de Fin de Turno', 'Recurso': 'Brigada'}
            )
            fig_ext.update_traces(texttemplate='%{text:.2f} h', textposition='outside')
            fig_ext.update_layout(yaxis=dict(autorange="reversed"), height=390, margin=dict(t=10, b=10, l=10, r=40))
            st.plotly_chart(fig_ext, use_container_width=True)
        else:
            st.info("No hay brigadas con tiempo extendido posterior a su turno en los filtros actuales.")

    st.markdown("##### 📊 Matriz Integral por Brigada (Jornada Ordinaria vs. Standby vs. Horas Extendidas Post-Turno)")
    cols_show_brig = [
        'Recurso', 'Sector', 'Zona_Oficial', 'Regla_Horario', 'Turno_Actual',
        'Semaforo', 'Efectividad_%', 'Total_Asignadas', 'Finalizadas', 'Fin_Por_Dia',
        'Canceladas', 'Canc_EGAM', 'Canc_RPA', 'Suspendidas',
        'Horas_Netas_Disponibles', 'Horas_En_Jornada', 'Horas_Sin_Atender',
        'Horas_Post_Turno', 'Eventos_Extension_A', 'Eventos_Reactivacion_B',
        'Primer_Inicio', 'Ultimo_Fin'
    ]
    st.dataframe(
        rec_stats[cols_show_brig].sort_values(by='Horas_Sin_Atender', ascending=False),
        column_config={
            "Zona_Oficial": "Zona Oficial",
            "Regla_Horario": "Esquema Turno",
            "Turno_Actual": "Turno Día",
            "Semaforo": "Estado Meta",
            "Efectividad_%": st.column_config.ProgressColumn("Efectividad", format="%.1f%%", min_value=0, max_value=100),
            "Total_Asignadas": "Asig.",
            "Fin_Por_Dia": st.column_config.NumberColumn("Fin/Día", format="%.1f"),
            "Canc_EGAM": "Canc. EGAM",
            "Canc_RPA": "Canc. RPA",
            "Horas_Netas_Disponibles": st.column_config.NumberColumn("Turno Neto", format="%.1f h"),
            "Horas_En_Jornada": st.column_config.NumberColumn("Hrs en Turno", format="%.2f h"),
            "Horas_Sin_Atender": st.column_config.NumberColumn("Hrs Standby", format="%.2f h"),
            "Horas_Post_Turno": st.column_config.NumberColumn("Hrs Post-Turno (Extras)", format="%.2f h"),
            "Eventos_Extension_A": "Extens. (Caso A)",
            "Eventos_Reactivacion_B": "Reactiv. (Caso B)",
            "Primer_Inicio": "1er Inicio",
            "Ultimo_Fin": "Último Cierre"
        },
        use_container_width=True,
        hide_index=True
    )

    df_post_inline = df_f[df_f['Minutos_Extra_PostTurno'] > 0].copy()
    if not df_post_inline.empty:
        st.markdown("##### 🕒 Relación Directa de Actividades con Tiempo Extendido / Post-Turno (Soporte para Cliente y Horas Extras)")
        df_post_inline['Horas_Extra_Orden'] = (df_post_inline['Minutos_Extra_PostTurno'] / 60.0).round(2)
        cols_inline = [
            'Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso', 'Turno_Detectado_Dia',
            'Clasificacion_Jornada', 'Entorno_Ubicacion', 'Orden_Trabajo', 'ID_Actividad',
            'Subtipo_Actividad', 'Estado_Actividad', 'Inicio', 'Finalización',
            'Minutos_En_Jornada', 'Minutos_Extra_PostTurno', 'Horas_Extra_Orden', 'Causas_Raiz_Texto', 'Observaciones'
        ]
        st.dataframe(
            df_post_inline[[c for c in cols_inline if c in df_post_inline.columns]].sort_values(by='Minutos_Extra_PostTurno', ascending=False),
            column_config={
                "Fecha_Str": "Fecha",
                "Turno_Detectado_Dia": "Horario Turno",
                "Clasificacion_Jornada": "Tipo Extensión",
                "Entorno_Ubicacion": "Ubicación",
                "Minutos_En_Jornada": st.column_config.NumberColumn("Min. en Turno", format="%.0f m"),
                "Minutos_Extra_PostTurno": st.column_config.NumberColumn("Min. Post-Turno", format="%.0f m"),
                "Horas_Extra_Orden": st.column_config.NumberColumn("Horas Extras Orden", format="%.2f h"),
                "Causas_Raiz_Texto": "Causas Detectadas",
                "Observaciones": st.column_config.TextColumn("Observaciones", width="large")
            },
            use_container_width=True,
            hide_index=True
        )

# ================= TAB 2: AUDITORÍA POST-TURNO Y CASCO URBANO DE MUNICIPIOS =================
with tab_post:
    st.markdown("##### 🌙 Auditoría Detallada de Tiempo Extendido (Caso A) vs. Reactivación Post-Turno (Caso B) y Casco Urbano")
    df_post = df_f[df_f['Minutos_Extra_PostTurno'] > 0].copy()

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if not df_post.empty:
            post_grp = df_post.groupby(['Recurso', 'Clasificacion_Jornada'])['Minutos_Extra_PostTurno'].sum().reset_index()
            post_grp['Horas_Extra'] = (post_grp['Minutos_Extra_PostTurno'] / 60.0).round(2)
            fig_post = px.bar(
                post_grp.sort_values(by='Horas_Extra', ascending=False),
                x='Horas_Extra',
                y='Recurso',
                color='Clasificacion_Jornada',
                orientation='h',
                barmode='stack',
                text='Horas_Extra',
                title="Horas Extendidas / Post-Turno por Brigada (Caso A vs. Caso B)",
                color_discrete_map={
                    "🌙 Caso B: Reactivación Post-Turno (Inicia Después del Turno)": "#7c3aed",
                    "⏱️ Caso A: Tiempo Extendido (Cruza Hora Fin de Turno)": "#f59e0b",
                    "🚨 Caso Excepcional BOLE (Fin de Semana)": "#ef4444"
                }
            )
            fig_post.update_traces(texttemplate='%{text:.2f} h', textposition='outside')
            fig_post.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=35, b=10, l=10, r=40), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_post, use_container_width=True)
        else:
            st.info("No se registran horas post-turno en la selección actual.")

    with col_p2:
        df_muni_urb = df_f[df_f['Zona_Oficial'] != "IBAGUE URBANA"].copy()
        if not df_muni_urb.empty:
            urb_cnt = df_muni_urb.groupby(['Zona_Oficial', 'Entorno_Ubicacion']).size().reset_index(name='Cantidad')
            fig_urb = px.bar(
                urb_cnt,
                x='Zona_Oficial',
                y='Cantidad',
                color='Entorno_Ubicacion',
                barmode='stack',
                title="Municipios y Rurales: Avisos en Casco Urbano vs. Zona Veredal",
                color_discrete_map={
                    "🏘️ Casco Urbano Municipio": "#2563eb",
                    "🌲 Zona Veredal / Rural": "#10b981",
                    "📍 General Municipio": "#94a3b8"
                }
            )
            fig_urb.update_layout(height=360, margin=dict(t=35, b=10, l=10, r=10), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_urb, use_container_width=True)
        else:
            st.info("Selecciona zonas de municipios para ver la proporción Casco Urbano vs. Vereda.")

    st.markdown("---")
    st.markdown("###### 🏘️ Monitor de Avisos Atendidos en el Casco Urbano de los Municipios y Veredas")
    c_u1, c_u2 = st.columns(2)
    with c_u1:
        f_entorno = st.radio(
            "Filtrar por Ubicación en Municipios:",
            options=["Todos los de Municipios", "Solo 🏘️ Casco Urbano Municipio", "Solo 🌲 Zona Veredal / Rural"],
            horizontal=True
        )
    with c_u2:
        solo_post_muni = st.checkbox("Ver únicamente avisos que superaron el horario de turno (Post-Turno / Extras)", value=False)

    df_muni_view = df_f[df_f['Zona_Oficial'] != "IBAGUE URBANA"].copy()
    if f_entorno == "Solo 🏘️ Casco Urbano Municipio":
        df_muni_view = df_muni_view[df_muni_view['Entorno_Ubicacion'] == "🏘️ Casco Urbano Municipio"]
    elif f_entorno == "Solo 🌲 Zona Veredal / Rural":
        df_muni_view = df_muni_view[df_muni_view['Entorno_Ubicacion'] == "🌲 Zona Veredal / Rural"]
    if solo_post_muni:
        df_muni_view = df_muni_view[df_muni_view['Minutos_Extra_PostTurno'] > 0]

    cols_muni_tbl = [
        'Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso', 'Turno_Detectado_Dia',
        'Clasificacion_Jornada', 'Entorno_Ubicacion', 'Orden_Trabajo', 'ID_Actividad',
        'Estado_Actividad', 'Inicio', 'Finalización', 'Minutos_En_Jornada',
        'Minutos_Extra_PostTurno', 'Causas_Raiz_Texto', 'Dirección', 'Descripcion_Orden', 'Observaciones'
    ]
    st.dataframe(
        df_muni_view[[c for c in cols_muni_tbl if c in df_muni_view.columns]],
        use_container_width=True,
        hide_index=True
    )

# ================= TAB 3: DESEMPEÑO POR ZONAS OFICIALES =================
with tab_zonas:
    zona_summary = df_f.groupby(['Sector', 'Zona_Oficial']).agg(
        Brigadas=('Recurso', 'nunique'),
        Total_Actividades=('ID_Actividad', 'count'),
        Finalizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'finalizada').sum()),
        Canceladas=('Estado_Actividad', lambda x: (x.str.lower() == 'cancelada').sum()),
        Suspendidas=('Estado_Actividad', lambda x: (x.str.lower() == 'suspendida').sum()),
        Horas_Viaje=('Minutos_Viaje', lambda x: round(x.sum() / 60.0, 2)),
        Horas_Faena=('Minutos_Duracion', lambda x: round(x.sum() / 60.0, 2)),
        Horas_Extras_Zona=('Minutos_Extra_PostTurno', lambda x: round(x.sum() / 60.0, 2)),
        Prom_Viaje_Min=('Minutos_Viaje', lambda x: round(x.mean(), 1)),
        Prom_Faena_Min=('Minutos_Duracion', lambda x: round(x.mean(), 1))
    ).reset_index()
    zona_summary['Efectividad_%'] = ((zona_summary['Finalizadas'] / zona_summary['Total_Actividades'].replace(0, 1)) * 100.0).round(1)
    zona_summary = zona_summary.sort_values(by='Total_Actividades', ascending=False)

    col_z1, col_z2 = st.columns(2)
    with col_z1:
        st.markdown("##### 🏢 Volumen de Actividades y Estados por Zona Oficial")
        fig_z_vol = px.bar(
            zona_summary,
            x='Zona_Oficial',
            y=['Finalizadas', 'Canceladas', 'Suspendidas'],
            barmode='stack',
            color_discrete_map={'Finalizadas': '#10b981', 'Canceladas': '#ef4444', 'Suspendidas': '#f59e0b'}
        )
        fig_z_vol.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_z_vol, use_container_width=True)

    with col_z2:
        st.markdown("##### 🚗 Comparativa por Zona: Horas en Ruta vs. Horas en Faena vs. Horas Extras")
        fig_z_time = px.bar(
            zona_summary,
            x='Zona_Oficial',
            y=['Horas_Viaje', 'Horas_Faena', 'Horas_Extras_Zona'],
            barmode='group',
            color_discrete_map={'Horas_Viaje': '#3b82f6', 'Horas_Faena': '#0f172a', 'Horas_Extras_Zona': '#7c3aed'}
        )
        fig_z_time.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_z_time, use_container_width=True)

    st.dataframe(zona_summary, use_container_width=True, hide_index=True)

# ================= TAB 4: LABORES TÉCNICAS Y VALIDACIÓN DE 45 MINUTOS =================
with tab_labores:
    st.markdown("##### 🛠️ Validador de Tiempos en Sitio y Tipos de Labor Técnica Ejecutada")
    st.caption("Estándar operativo: El tiempo de duración en sitio (faena) no debe superar los **45 minutos** en revisiones y maniobras estándar.")

    df_lab = df_f[df_f['Categoria_Labor'] == 'Operativa (Daños / OT)'].copy()
    if not df_lab.empty:
        # Evaluar cumplimiento del estándar de 45 minutos
        df_lab['Cumple_Estandar_45m'] = df_lab['Minutos_Duracion'].apply(lambda x: "🟢 Óptimo (< 45 min)" if x <= 45 else "🔴 Excede Estándar (> 45 min)")

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.markdown("###### ⏱️ Tiempo Promedio en Sitio por Tipo de Labor Técnica")
            labor_summary = df_lab.groupby('Labor_Tecnica').agg(
                Cantidad=('ID_Actividad', 'count'),
                Prom_Min_Sitio=('Minutos_Duracion', 'mean'),
                Max_Min_Sitio=('Minutos_Duracion', 'max'),
                Exceden_45m=('Minutos_Duracion', lambda x: (x > 45).sum())
            ).reset_index().sort_values(by='Prom_Min_Sitio', ascending=False)

            fig_lab = px.bar(
                labor_summary,
                x='Prom_Min_Sitio',
                y='Labor_Tecnica',
                orientation='h',
                text='Prom_Min_Sitio',
                color='Prom_Min_Sitio',
                color_continuous_scale='Sunset',
                labels={'Prom_Min_Sitio': 'Minutos Promedio en Sitio', 'Labor_Tecnica': 'Tipo de Labor Técnica'}
            )
            fig_lab.update_traces(texttemplate='%{text:.0f} min', textposition='outside')
            fig_lab.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=10, b=10, l=10, r=40))
            st.plotly_chart(fig_lab, use_container_width=True)

        with col_l2:
            st.markdown("###### 📊 Distribución de Órdenes según Estándar de 45 Minutos")
            est_counts = df_lab['Cumple_Estandar_45m'].value_counts().reset_index()
            est_counts.columns = ['Estado Estándar', 'Total']
            fig_est_45 = px.pie(
                est_counts,
                values='Total',
                names='Estado Estándar',
                hole=0.45,
                color='Estado Estándar',
                color_discrete_map={
                    "🟢 Óptimo (< 45 min)": "#10b981",
                    "🔴 Excede Estándar (> 45 min)": "#ef4444"
                }
            )
            fig_est_45.update_layout(height=360, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_est_45, use_container_width=True)

        st.markdown("###### 📋 Detalle de Órdenes Operativas y Verificación del Estándar en Sitio")
        st.dataframe(
            df_lab[[
                'Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso', 'Orden_Trabajo',
                'ID_Actividad', 'Labor_Tecnica', 'Minutos_Duracion', 'Cumple_Estandar_45m',
                'Nodos_Detectados', 'Causas_Raiz_Texto', 'Observaciones'
            ]],
            column_config={
                "Minutos_Duracion": st.column_config.NumberColumn("Duración Sitio", format="%.0f min"),
                "Cumple_Estandar_45m": "Evaluación 45 min",
                "Causas_Raiz_Texto": "Causas Detectadas",
                "Observaciones": st.column_config.TextColumn("Observaciones del Recurso", width="large")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay actividades operativas de daños u OT en la selección actual para evaluar las labores técnicas.")

# ================= TAB 5: COLA EGAM, GANTT HORARIO Y DISCIPLINA WFM =================
with tab_tiempos:
    st.markdown("##### ⏳ Mejora A: Desglose de Demora — Cola de Despacho EGAM (Generación ➔ Asignación) vs. Reacción Brigada (Asignación ➔ Inicio)")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        cola_df = rec_stats[rec_stats['Prom_Cola_EGAM_Min'] > 0].sort_values(by='Prom_Cola_EGAM_Min', ascending=False).head(15)
        if not cola_df.empty:
            fig_cola = px.bar(
                cola_df,
                x='Prom_Cola_EGAM_Min',
                y='Recurso',
                color='Sector',
                orientation='h',
                text='Prom_Cola_EGAM_Min',
                title="🖥️ Tiempo Promedio en Cola EGAM Antes de Asignar (Minutos)",
                color_discrete_map={'CENTRO': '#0f172a', 'NORTE': '#2563eb'}
            )
            fig_cola.update_traces(texttemplate='%{text:.0f} m', textposition='outside')
            fig_cola.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=35, b=10, l=10, r=40))
            st.plotly_chart(fig_cola, use_container_width=True)
        else:
            st.info("No hay datos de Fecha de Generación vs. Asignación en la selección.")

    with col_t2:
        reac_df = rec_stats[rec_stats['Prom_Reaccion_Min'] > 0].sort_values(by='Prom_Reaccion_Min', ascending=False).head(15)
        if not reac_df.empty:
            fig_reac = px.bar(
                reac_df,
                x='Prom_Reaccion_Min',
                y='Recurso',
                color='Zona_Oficial',
                orientation='h',
                text='Prom_Reaccion_Min',
                title="👷 Tiempo Promedio de Reacción de Brigada tras Asignación (Minutos)"
            )
            fig_reac.update_traces(texttemplate='%{text:.0f} m', textposition='outside')
            fig_reac.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=35, b=10, l=10, r=40))
            st.plotly_chart(fig_reac, use_container_width=True)
        else:
            st.info("No hay registros con diferencia horaria entre asignación e inicio.")

    st.markdown("---")
    st.markdown("##### 📅 Mejora B: Diagrama de Gantt / Línea de Tiempo Horaria (Detector de Vacíos Operativos entre Orden y Orden)")
    df_gantt = df_contexto_turno.dropna(subset=['DT_Inicio', 'DT_Fin']).copy()
    if not df_gantt.empty:
        fig_gantt = px.timeline(
            df_gantt.sort_values(by='Recurso'),
            x_start='DT_Inicio',
            x_end='DT_Fin',
            y='Recurso',
            color='Subtipo_Actividad',
            hover_name='Orden_Trabajo',
            hover_data=['ID_Actividad', 'Estado_Actividad', 'Inicio', 'Finalización', 'Minutos_Viaje', 'Minutos_Duracion', 'Observaciones'],
            height=max(420, df_gantt['Recurso'].nunique() * 24)
        )
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(margin=dict(t=15, b=15, l=10, r=10))
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.info("No hay horas de Inicio y Finalización válidas para construir el diagrama de Gantt.")

    st.markdown("---")
    st.markdown("##### 🛡️ Mejora C: Auditoría de Disciplina en el Aplicativo WFM y Rezagos Operativos")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("###### ⚠️ 1. Rutinas Abiertas sin Cerrar (Únicamente en Estado `Pendiente`)")
        rutinas_pendientes = df_contexto_turno[
            (df_contexto_turno['Subtipo_Actividad'].str.upper().isin(['INICIO TURNO', 'FIN TURNO', 'ALIMENTACIÓN', 'ALIMENTACION'])) &
            (df_contexto_turno['Estado_Actividad'].str.lower().isin(['pendiente', 'iniciada', 'en ruta']))
        ]
        if not rutinas_pendientes.empty:
            st.warning(f"Se detectaron **{len(rutinas_pendientes)}** rutinas de turno que el recurso dejó abiertas en estado Pendiente:")
            st.dataframe(
                rutinas_pendientes[['Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso', 'Subtipo_Actividad', 'Estado_Actividad', 'Inicio', 'Finalización']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ Ninguna brigada dejó su Inicio Turno, Alimentación o Fin Turno abierto en estado Pendiente.")

    with col_w2:
        st.markdown("###### 🔍 2. Anomalías de Rutina (`Inicio/Fin Turno` o `Alimentación` Canceladas / Suspendidas)")
        rutinas_anomalas = df_contexto_turno[
            (df_contexto_turno['Subtipo_Actividad'].str.upper().isin(['INICIO TURNO', 'FIN TURNO', 'ALIMENTACIÓN', 'ALIMENTACION'])) &
            (df_contexto_turno['Estado_Actividad'].str.lower().isin(['cancelada', 'suspendida', 'no realizado']))
        ]
        if not rutinas_anomalas.empty:
            st.info(f"Se registran **{len(rutinas_anomalas)}** actividades de rutina marcadas como Canceladas, Suspendidas o No Realizadas:")
            st.dataframe(
                rutinas_anomalas[['Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso', 'Subtipo_Actividad', 'Estado_Actividad', 'Motivo_Cancelacion', 'Comentarios_Cancelacion', 'Comentarios_Suspension']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No hay rutinas de turno con cancelaciones o suspensiones anómalas.")

    st.markdown("<br>", unsafe_allow_html=True)
    col_w3, col_w4 = st.columns([1.3, 1])
    with col_w3:
        st.markdown("###### 🚨 3. Seguimiento Prioritario: Daños / OT Operativas en Estado `Pendiente` o `Suspendida`")
        operativas_rezago = df_contexto_turno[
            (df_contexto_turno['Categoria_Labor'] == 'Operativa (Daños / OT)') &
            (df_contexto_turno['Estado_Actividad'].str.lower().isin(['pendiente', 'suspendida']))
        ].copy()
        if not operativas_rezago.empty:
            f_est_rez = st.radio(
                "Filtrar rezagos operativos por estado:",
                options=["Todos (Pendientes + Suspendidas)", "Solo Pendientes", "Solo Suspendidas"],
                horizontal=True,
                key="rad_rezago"
            )
            if f_est_rez == "Solo Pendientes":
                operativas_rezago = operativas_rezago[operativas_rezago['Estado_Actividad'].str.lower() == 'pendiente']
            elif f_est_rez == "Solo Suspendidas":
                operativas_rezago = operativas_rezago[operativas_rezago['Estado_Actividad'].str.lower() == 'suspendida']

            cols_rez = [
                'Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso', 'Orden_Trabajo',
                'ID_Actividad', 'Subtipo_Actividad', 'Estado_Actividad',
                'Nodos_Detectados', 'Causas_Raiz_Texto', 'Comentarios_Suspension', 'Observaciones', 'Descripcion_Orden'
            ]
            st.dataframe(
                operativas_rezago[[c for c in cols_rez if c in operativas_rezago.columns]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No hay incidentes ni órdenes operativas pendientes o suspendidas en la selección actual.")

    with col_w4:
        st.markdown("###### 🚫 4. Auditoría de Descargos Inválidos (`00000`) o Finalizadas sin GPS")
        descargo_invalido = df_f[
            (df_f['Numero_Descargo'].str.contains('^0+$', regex=True, na=False)) |
            ((df_f['Estado_Actividad'].str.lower() == 'finalizada') & (df_f['Categoria_Labor'] == 'Operativa (Daños / OT)') & (df_f['Lat'].isna()))
        ]
        if not descargo_invalido.empty:
            st.dataframe(
                descargo_invalido[['Fecha_Str', 'Recurso', 'Orden_Trabajo', 'ID_Actividad', 'Subtipo_Actividad', 'Numero_Descargo', 'Lat', 'Observaciones']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No se detectaron descargos en '00000' ni órdenes operativas finalizadas sin GPS.")

# ================= TAB 6: NODOS RECURRENTES Y RADAR DE CAUSAS =================
with tab_nodos:
    st.markdown("##### ⚡ Detección de Nodos / Equipos Recurrentes y Radar Multicausal de Fallas")
    st.caption("Extrae los nodos y suma todas las causas raíz combinadas en cada aviso.")

    rows_nodos_flat = []
    rows_nodos_causas = []

    for idx, r in df_f.iterrows():
        causas_aviso = r['Lista_Causas_Raiz']
        for nd in r['Lista_Nodos']:
            rows_nodos_flat.append({
                'Nodo_Equipo': nd,
                'Tipo_Equipo': classify_node_type(nd),
                'Sector': r['Sector'],
                'Zona_Oficial': r['Zona_Oficial'],
                'Recurso': r['Recurso'],
                'Fecha_Str': r['Fecha_Str'],
                'Orden_Trabajo': r['Orden_Trabajo'],
                'ID_Actividad': r['ID_Actividad'],
                'Estado_Actividad': r['Estado_Actividad'],
                'Causas_Aviso': " | ".join(causas_aviso),
                'Lista_Causas': causas_aviso,
                'Numero_Descargo': r['Numero_Descargo'],
                'Observaciones': r['Observaciones']
            })
            for c_item in causas_aviso:
                rows_nodos_causas.append({
                    'Nodo_Equipo': nd,
                    'Tipo_Equipo': classify_node_type(nd),
                    'Sector': r['Sector'],
                    'Zona_Oficial': r['Zona_Oficial'],
                    'Recurso': r['Recurso'],
                    'Causa_Raiz': c_item,
                    'ID_Actividad': r['ID_Actividad'],
                    'Orden_Trabajo': r['Orden_Trabajo']
                })

    if rows_nodos_flat:
        df_nodos_exp = pd.DataFrame(rows_nodos_flat)
        df_nc_exp = pd.DataFrame(rows_nodos_causas)

        c_nd1, c_nd2, c_nd3 = st.columns([1, 1.2, 1])
        with c_nd1:
            tipos_eq = ["Todos"] + sorted(df_nodos_exp['Tipo_Equipo'].unique().tolist())
            sel_tipo_eq = st.selectbox("1. Filtrar por Familia de Equipo:", tipos_eq)
        with c_nd2:
            causas_disp_nd = sorted(df_nc_exp['Causa_Raiz'].unique().tolist())
            sel_causas_nd = st.multiselect(
                "2. Hacer Zoom por Causa(s) Raíz:",
                options=causas_disp_nd,
                default=[],
                placeholder="Todas las causas..."
            )
        with c_nd3:
            buscar_nodo = st.text_input("3. Buscar Código Exacto de Nodo:", placeholder="Ej: RB1950, CD23329, S00058...")

        df_nodos_filt = df_nodos_exp.copy()
        df_nc_filt = df_nc_exp.copy()

        if sel_tipo_eq != "Todos":
            df_nodos_filt = df_nodos_filt[df_nodos_filt['Tipo_Equipo'] == sel_tipo_eq]
            df_nc_filt = df_nc_filt[df_nc_filt['Tipo_Equipo'] == sel_tipo_eq]

        if sel_causas_nd:
            df_nodos_filt = df_nodos_filt[df_nodos_filt['Lista_Causas'].apply(lambda lst: any(c in sel_causas_nd for c in lst))]
            df_nc_filt = df_nc_filt[df_nc_filt['Causa_Raiz'].isin(sel_causas_nd)]

        if buscar_nodo.strip():
            q_nd = buscar_nodo.strip().upper()
            df_nodos_filt = df_nodos_filt[df_nodos_filt['Nodo_Equipo'].str.contains(q_nd, na=False)]
            df_nc_filt = df_nc_filt[df_nc_filt['Nodo_Equipo'].str.contains(q_nd, na=False)]

        resumen_nodos = df_nodos_filt.groupby(['Nodo_Equipo', 'Tipo_Equipo', 'Sector', 'Zona_Oficial']).agg(
            Veces_Intervenido=('ID_Actividad', 'count'),
            Causas_Acumuladas=('Lista_Causas', lambda s: " | ".join(sorted({c for lst in s for c in lst}))),
            Ordenes_Asociadas=('Orden_Trabajo', lambda s: ", ".join(sorted(set(s)))),
            Brigadas_Que_Asistieron=('Recurso', lambda s: ", ".join(sorted(set(s)))),
            Fechas=('Fecha_Str', lambda s: ", ".join(sorted(set(s))))
        ).reset_index().sort_values(by='Veces_Intervenido', ascending=False)

        resumen_nodos['Accion_Recomendada'] = resumen_nodos['Causas_Acumuladas'].apply(recommend_action_from_causes)

        col_ng1, col_ng2 = st.columns([1, 1.45])
        with col_ng1:
            st.markdown("###### 📊 Porcentaje por Familia (`RB/RC`, `PF/6`, `S`, `CD`)")
            tipo_cnt = resumen_nodos.groupby('Tipo_Equipo')['Veces_Intervenido'].sum().reset_index()
            fig_tp_nd = px.pie(
                tipo_cnt,
                values='Veces_Intervenido',
                names='Tipo_Equipo',
                hole=0.45,
                color='Tipo_Equipo',
                color_discrete_map={
                    "Reconectador (RB / RC)": "#2563eb",
                    "Cortacircuito / Transformador (CD)": "#f59e0b",
                    "Seccionamiento (S)": "#10b981",
                    "Punto Físico / Nodo (6 / PF)": "#7c3aed"
                }
            )
            fig_tp_nd.update_traces(textposition='inside', textinfo='percent+label+value')
            fig_tp_nd.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15), height=390, margin=dict(t=15, b=40, l=10, r=10))
            st.plotly_chart(fig_tp_nd, use_container_width=True)

        with col_ng2:
            st.markdown("###### 🔥 Top 20 Nodos Recurrentes Desglosados por Causa Raíz (`Nodo_Equipo` en Eje X)")
            top_20_names = resumen_nodos.head(20)['Nodo_Equipo'].tolist()
            df_top20_nc = df_nc_filt[df_nc_filt['Nodo_Equipo'].isin(top_20_names)].groupby(
                ['Nodo_Equipo', 'Causa_Raiz', 'Zona_Oficial']
            ).size().reset_index(name='Incidencias')

            fig_nodos = px.bar(
                df_top20_nc,
                x='Nodo_Equipo',
                y='Incidencias',
                color='Causa_Raiz',
                barmode='stack',
                text='Incidencias',
                category_orders={'Nodo_Equipo': top_20_names},
                hover_data=['Zona_Oficial'],
                color_discrete_map=COLORES_CAUSAS,
                labels={'Nodo_Equipo': 'Código Nodo / Equipo', 'Incidencias': 'Cantidad'}
            )
            fig_nodos.update_layout(xaxis_tickangle=-45, height=390, margin=dict(t=15, b=40, l=10, r=10), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_nodos, use_container_width=True)

        st.markdown("---")
        col_rad1, col_rad2 = st.columns([1, 1.35])
        with col_rad1:
            st.markdown("###### 🎯 Radar Multicausal de Fallas en Nodos")
            radar_cnt = df_nc_filt['Causa_Raiz'].value_counts().reset_index()
            radar_cnt.columns = ['Causa', 'Frecuencia']
            if not radar_cnt.empty:
                fig_radar = px.line_polar(
                    radar_cnt,
                    r='Frecuencia',
                    theta='Causa',
                    line_close=True,
                    markers=True
                )
                fig_radar.update_traces(fill='toself', line_color='#2563eb')
                fig_radar.update_layout(height=360, margin=dict(t=25, b=25, l=40, r=40))
                st.plotly_chart(fig_radar, use_container_width=True)

        with col_rad2:
            st.markdown("###### 🗺️ Causas de Falla en Nodos por Zona Oficial")
            zona_causa_cnt = df_nc_filt.groupby(['Zona_Oficial', 'Causa_Raiz']).size().reset_index(name='Eventos')
            fig_zc = px.bar(
                zona_causa_cnt,
                x='Zona_Oficial',
                y='Eventos',
                color='Causa_Raiz',
                barmode='stack',
                text='Eventos',
                color_discrete_map=COLORES_CAUSAS,
                labels={'Zona_Oficial': 'Zona Oficial / Municipio', 'Eventos': 'Frecuencia de Causa'}
            )
            fig_zc.update_layout(xaxis_tickangle=-35, height=360, margin=dict(t=15, b=30, l=10, r=10), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_zc, use_container_width=True)

        st.markdown("###### 📋 Priorización de Nodos y Acción Especializada Recomendada")
        st.dataframe(
            resumen_nodos[[
                'Nodo_Equipo', 'Tipo_Equipo', 'Sector', 'Zona_Oficial',
                'Veces_Intervenido', 'Causas_Acumuladas', 'Accion_Recomendada',
                'Brigadas_Que_Asistieron', 'Ordenes_Asociadas', 'Fechas'
            ]],
            column_config={
                "Nodo_Equipo": "Nodo / Equipo",
                "Veces_Intervenido": "Veces",
                "Causas_Acumuladas": st.column_config.TextColumn("Causas Detectadas", width="medium"),
                "Accion_Recomendada": st.column_config.TextColumn("Acción Especializada Sugerida", width="large")
            },
            use_container_width=True,
            hide_index=True
        )

        with st.expander("🔎 Ver Detalle Técnico Completo de las Órdenes por Nodo y Causa"):
            st.dataframe(
                df_nodos_filt.drop(columns=['Lista_Causas'], errors='ignore'),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No se detectaron códigos de nodos en la selección actual.")

# ================= TAB 7: OBSERVACIONES Y AUDITORÍA DE CANCELADOS EGAM/RPA =================
with tab_obs:
    st.markdown("##### 🚫 Auditoría de Actividades Canceladas: Gestión EGAM vs. Agrupación RPA vs. Operativo")
    df_canc_only = df_f[df_f['Estado_Actividad'].str.lower() == 'cancelada'].copy()

    if not df_canc_only.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            orig_counts = df_canc_only['Origen_Cancelacion'].value_counts().reset_index()
            orig_counts.columns = ['Responsable / Origen Cancelación', 'Cantidad']
            fig_orig_c = px.bar(
                orig_counts,
                x='Cantidad',
                y='Responsable / Origen Cancelación',
                orientation='h',
                color='Responsable / Origen Cancelación',
                text='Cantidad'
            )
            fig_orig_c.update_traces(textposition='outside')
            fig_orig_c.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=300, margin=dict(t=10, b=10, l=10, r=40))
            st.plotly_chart(fig_orig_c, use_container_width=True)

        with col_c2:
            mot_counts = df_canc_only['Motivo_Cancelacion'].replace('', 'Sin Motivo').value_counts().head(10).reset_index()
            mot_counts.columns = ['Motivo Oficial WFM', 'Cantidad']
            fig_mot_c = px.pie(mot_counts, values='Cantidad', names='Motivo Oficial WFM', hole=0.45)
            fig_mot_c.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_mot_c, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🔎 Buscador Rápido por Orden de Trabajo, ID de Actividad, Causa Raíz y Observaciones")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        buscar_ot_obs = st.text_input("📋 Buscar por Orden de Trabajo o ID Actividad:", "")
    with col_s2:
        palabra_clave = st.text_input("📝 Buscar palabra clave en Observaciones / Comentarios:", "")
    with col_s3:
        orig_disp = ["Todos"] + sorted(df_f['Origen_Cancelacion'].unique().tolist())
        sel_orig_canc = st.selectbox("Filtrar por Origen de Cancelación:", orig_disp)

    df_obs_view = df_f.copy()
    if buscar_ot_obs.strip():
        q_ot = buscar_ot_obs.strip()
        df_obs_view = df_obs_view[
            df_obs_view['Orden_Trabajo'].str.contains(q_ot, case=False, na=False) |
            df_obs_view['ID_Actividad'].str.contains(q_ot, case=False, na=False)
        ]
    if palabra_clave.strip():
        kw = palabra_clave.strip()
        mask_kw = (
            df_obs_view['Observaciones'].str.contains(kw, case=False, na=False) |
            df_obs_view['Descripcion_Orden'].str.contains(kw, case=False, na=False) |
            df_obs_view['Comentarios_Suspension'].str.contains(kw, case=False, na=False) |
            df_obs_view['Comentarios_Cancelacion'].str.contains(kw, case=False, na=False)
        )
        df_obs_view = df_obs_view[mask_kw]
    if sel_orig_canc != "Todos":
        df_obs_view = df_obs_view[df_obs_view['Origen_Cancelacion'] == sel_orig_canc]

    cols_obs_table = [c for c in [
        'Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso',
        'Orden_Trabajo', 'ID_Actividad', 'Subtipo_Actividad',
        'Estado_Actividad', 'Clasificacion_Jornada', 'Origen_Cancelacion',
        'Nodos_Detectados', 'Causas_Raiz_Texto',
        'Observaciones', 'Comentarios_Cancelacion', 'Comentarios_Suspension', 'Descripcion_Orden'
    ] if c in df_obs_view.columns]
    
    st.dataframe(df_obs_view[cols_obs_table], use_container_width=True, hide_index=True)

# ================= TAB 8: MAPA GEOGRÁFICO Y TRAZABILIDAD DE RUTA =================
with tab_mapa:
    st.markdown("##### 📍 Georreferenciación, Buscador de OT y Trazabilidad de Ruta por Brigada")
    df_map = df_f.dropna(subset=['Lat', 'Lon']).copy()
    
    if not df_map.empty:
        col_m1, col_m2, col_m3 = st.columns([1.2, 1.2, 1])
        with col_m1:
            ot_texto_map = st.text_input("🔎 Buscar Orden de Trabajo o ID en el Mapa:", "")
        with col_m2:
            lista_ots_mapa = ["Todas"] + sorted([
                f"{r['Orden_Trabajo']} | ID:{r['ID_Actividad']} ({r['Recurso']})"
                for _, r in df_map.iterrows()
            ])
            sel_ot_dropdown = st.selectbox("📌 O selecciona una Orden de la lista:", lista_ots_mapa)
        with col_m3:
            st.markdown("<br>", unsafe_allow_html=True)
            ver_trazabilidad = st.checkbox("🛣️ Ver Trazabilidad / Orden de Atención", value=False)

        zoom_level = 8.5
        if ot_texto_map.strip():
            q_m = ot_texto_map.strip()
            df_map = df_map[
                df_map['Orden_Trabajo'].str.contains(q_m, case=False, na=False) |
                df_map['ID_Actividad'].str.contains(q_m, case=False, na=False)
            ]
            zoom_level = 13.5
        elif sel_ot_dropdown != "Todas":
            id_sel = re.search(r'ID:([^\s]+)', sel_ot_dropdown)
            if id_sel:
                df_map = df_map[df_map['ID_Actividad'] == id_sel.group(1)]
                zoom_level = 14.5

        if not df_map.empty:
            if ver_trazabilidad:
                df_map['Hora_Orden'] = df_map['Inicio'].fillna('23:59').astype(str)
                df_map = df_map.sort_values(by=['Recurso', 'Fecha_Str', 'Hora_Orden']).reset_index(drop=True)
                df_map['Orden_Secuencia'] = df_map.groupby(['Recurso', 'Fecha_Str']).cumcount() + 1
                df_map['Etiqueta_Parada'] = "Parada #" + df_map['Orden_Secuencia'].astype(str) + " (" + df_map['Inicio'].fillna('--:--').astype(str) + ")"

            color_map_estados = {'Finalizada': '#10b981', 'Cancelada': '#ef4444', 'Suspendida': '#f59e0b', 'No realizado': '#64748b'}
            hover_cols_map = ['Orden_Trabajo', 'ID_Actividad', 'Zona_Oficial', 'Clasificacion_Jornada', 'Inicio', 'Finalización', 'Minutos_Viaje', 'Minutos_Duracion', 'Nodos_Detectados', 'Causas_Raiz_Texto', 'Observaciones']
            if ver_trazabilidad:
                hover_cols_map = ['Etiqueta_Parada'] + hover_cols_map

            if hasattr(px, "scatter_map"):
                if ver_trazabilidad and len(df_map) > 1:
                    fig_map = px.line_map(df_map, lat='Lat', lon='Lon', color='Recurso', hover_name='Etiqueta_Parada', hover_data=hover_cols_map, zoom=zoom_level, height=540)
                    fig_map.update_traces(mode="lines+markers+text", text=df_map['Orden_Secuencia'].astype(str), textposition="top right")
                else:
                    fig_map = px.scatter_map(df_map, lat='Lat', lon='Lon', color='Estado_Actividad', hover_name='Recurso', hover_data=hover_cols_map, color_discrete_map=color_map_estados, zoom=zoom_level, height=540)
                fig_map.update_layout(map_style="open-street-map", margin=dict(t=0, b=0, l=0, r=0))
            else:
                if ver_trazabilidad and len(df_map) > 1:
                    fig_map = px.line_mapbox(df_map, lat='Lat', lon='Lon', color='Recurso', hover_name='Etiqueta_Parada', hover_data=hover_cols_map, zoom=zoom_level, height=540)
                    fig_map.update_traces(mode="lines+markers+text", text=df_map['Orden_Secuencia'].astype(str), textposition="top right")
                else:
                    fig_map = px.scatter_mapbox(df_map, lat='Lat', lon='Lon', color='Estado_Actividad', hover_name='Recurso', hover_data=hover_cols_map, color_discrete_map=color_map_estados, zoom=zoom_level, height=540)
                fig_map.update_layout(mapbox_style="open-street-map", margin=dict(t=0, b=0, l=0, r=0))

            st.plotly_chart(fig_map, use_container_width=True)

            if ver_trazabilidad:
                st.dataframe(df_map[['Orden_Secuencia', 'Recurso', 'Fecha_Str', 'Orden_Trabajo', 'ID_Actividad', 'Clasificacion_Jornada', 'Inicio', 'Finalización', 'Minutos_Viaje', 'Minutos_Duracion', 'Causas_Raiz_Texto', 'Observaciones']], use_container_width=True, hide_index=True)

# ================= TAB 9: BASE CONSOLIDADA Y AUDITORÍA =================
with tab_datos:
    st.markdown("##### 📋 Registros Consolidados con Clasificación de Turno, Horas Extras, Cola EGAM, Nodos, Causas y Observaciones")
    cols_auditoria = [c for c in [
        'Fecha_Str', 'Anio', 'Mes_Nombre', 'Sector', 'Zona_Oficial', 'Recurso',
        'Turno_Detectado_Dia', 'Clasificacion_Jornada', 'Entorno_Ubicacion',
        'Orden_Trabajo', 'ID_Actividad', 'Numero_Descargo', 'Subtipo_Actividad', 'Estado_Actividad',
        'Origen_Cancelacion', 'Nodos_Detectados', 'Causas_Raiz_Texto',
        'Fecha_Generacion', 'Hora_Asignacion', 'Inicio', 'Finalización',
        'Minutos_Cola_EGAM', 'Minutos_Reaccion', 'Minutos_Viaje', 'Minutos_Duracion',
        'Minutos_En_Jornada', 'Minutos_Extra_PostTurno',
        'Observaciones', 'Descripcion_Orden', 'Motivo_Cancelacion',
        'Comentarios_Cancelacion', 'Comentarios_Suspension'
    ] if c in df_f.columns]
    
    st.dataframe(df_f[cols_auditoria], use_container_width=True, hide_index=True)
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_consolidado = df_f[cols_auditoria].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Registros Filtrados (CSV)",
            data=csv_consolidado,
            file_name="auditoria_actividades_bol.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        csv_resumen = rec_stats.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Resumen de Brigadas, Standby y Extras (CSV)",
            data=csv_resumen,
            file_name="resumen_brigadas_bol.csv",
            mime="text/csv",
            use_container_width=True
        )
