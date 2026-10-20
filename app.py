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
URL_GOOGLE_DRIVE_DEFAULT = "https://drive.google.com/file/d/TU_ID_DE_ARCHIVO/view?usp=sharing"

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
        padding: 16px 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04);
        margin-bottom: 12px;
    }
    .metric-title {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.7rem;
        font-weight: 800;
        margin-top: 4px;
    }
    .metric-sub {
        color: #334155;
        font-size: 0.78rem;
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
    .alert-banner {
        background-color: #ffffff;
        border-left: 5px solid #0f172a;
        padding: 14px 18px;
        border-radius: 8px;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 6px;
        padding: 8px 14px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
        color: #334155;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-color: #0f172a !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MAESTRO OFICIAL DE RECURSOS, SECTORES Y ZONAS
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

MESES_ES = {
    1: "01 - Enero", 2: "02 - Febrero", 3: "03 - Marzo", 4: "04 - Abril",
    5: "05 - Mayo", 6: "06 - Junio", 7: "07 - Julio", 8: "08 - Agosto",
    9: "09 - Septiembre", 10: "10 - Octubre", 11: "11 - Noviembre", 12: "12 - Diciembre"
}

ACTIVIDADES_RUTINA = [
    "INICIO TURNO", "FIN TURNO", "ALIMENTACIÓN", "ALIMENTACION",
    "FORMACIONES", "TIEMPO NO PRODUCTIVO"
]

# -----------------------------------------------------------------------------
# 4. FUNCIONES DE LECTURA Y PROCESAMIENTO (APARTADO DE LECTURA INTACTO)
# -----------------------------------------------------------------------------
def convert_time_to_minutes(time_val):
    """Convierte formato HH:MM o numérico a minutos."""
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


def parse_google_drive_url(url: str) -> str:
    """Convierte enlaces compartidos de Google Drive en descarga directa."""
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
    """Extrae el código base de la brigada (ej. 'BOLV-399 (Apoyo)' -> 'BOLV-399', 'BOLM 371' -> 'BOLM-371')."""
    if pd.isna(recurso_str):
        return "SIN RECURSO"
    s = str(recurso_str).upper().strip()
    s = re.sub(r'^(BOL[A-Z])\s+(\d+)', r'\1-\2', s)
    match = re.search(r'(BOL[A-Z]-\d+)', s)
    if match:
        return match.group(1)
    return s


def extract_lat_lon(coord_str):
    """Extrae latitud y longitud de cadenas tipo 'lat:4.4463,lng:-75.2316'."""
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
    """Calcula minutos entre 'Hora de asignación' e 'Inicio'."""
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
    """Clasifica automáticamente los hallazgos reportados en Observaciones."""
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


def classify_cancelacion(row):
    """Clasifica el origen de las actividades canceladas (EGAM, Agrupación RPA, ADMS-INC, Operativo)."""
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
    """
    Extrae nodos/equipos que empiezan por 6, PF, RB, RC, CD o S tal cual fueron escritos
    sin alterar ningún carácter del código reportado.
    """
    textos = [
        str(row.get('Observaciones', '')),
        str(row.get('Comentarios_Suspension', '')),
        str(row.get('Comentarios_No_Realizado', '')),
        str(row.get('Comentarios_Cancelacion', '')),
        str(row.get('Descripcion_Orden', ''))
    ]
    full_text = " ".join([t for t in textos if t and t != 'nan']).upper()
    if not full_text.strip():
        return []
    
    # Busca nodos que inicien por PF6..., 6... (6 a 10 caracteres), RB..., RC..., CD..., S... (4 a 7 dígitos)
    pattern = r'\b(?:PF6\d{5,9}[A-Z0-9-]*|6\d{5,9}[A-Z0-9-]*|RB\d{2,6}[A-Z0-9-]*|RC\d{2,6}[A-Z0-9-]*|CD\d{3,7}[A-Z0-9-]*|S\d{4,6}[A-Z0-9-]*)\b'
    found = re.findall(pattern, full_text)
    # Conservar únicos en orden de aparición tal cual están escritos
    return list(dict.fromkeys(found))


def classify_node_type(node_code: str) -> str:
    """Clasifica el tipo de equipo según su prefijo."""
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
    """Estandariza columnas, cruza con el Maestro Oficial de Zonas y calcula métricas."""
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
        'Hora de asignación de actividad': 'Hora_Asignacion',
        'Ubicación Inicio Actividad': 'Ubicacion_Inicio',
        'Ubicación Completado': 'Ubicacion_Fin'
    }
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)

    # Asegurar columna Orden_Trabajo e ID_Actividad limpias
    if 'Orden_Trabajo' not in df.columns:
        df['Orden_Trabajo'] = 'Sin OT'
    else:
        df['Orden_Trabajo'] = df['Orden_Trabajo'].fillna('Sin OT').astype(str).str.strip()

    if 'ID_Actividad' not in df.columns:
        df['ID_Actividad'] = df.index.astype(str)
    else:
        df['ID_Actividad'] = df['ID_Actividad'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

    # Normalizar Recurso y cruzar con Maestro de Zonas Oficial
    if 'Recurso' in df.columns:
        df['Recurso'] = df['Recurso'].fillna('Sin Recurso').astype(str).str.strip()
    else:
        df['Recurso'] = 'Sin Recurso'
        
    df['Recurso_Base'] = df['Recurso'].apply(normalize_recurso_key)

    sectores_asignados = []
    zonas_asignadas = []
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
        sectores_asignados.append(sec_of)
        zonas_asignadas.append(zon_of)

    df['Sector'] = sectores_asignados
    df['Zona_Oficial'] = zonas_asignadas

    # Procesar Fechas (Año, Mes, Día)
    if 'Fecha' in df.columns:
        fechas_dt = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Fecha_Str'] = fechas_dt.dt.strftime('%Y-%m-%d').fillna('Sin Fecha')
        df['Anio'] = fechas_dt.dt.year.fillna(0).astype(int).astype(str).replace('0', 'Sin Año')
        df['Mes_Num'] = fechas_dt.dt.month.fillna(0).astype(int)
        df['Mes_Nombre'] = df['Mes_Num'].map(MESES_ES).fillna('Sin Mes')
    else:
        df['Fecha_Str'] = 'Sin Fecha'
        df['Anio'] = 'Sin Año'
        df['Mes_Nombre'] = 'Sin Mes'

    # Tiempos en minutos
    df['Minutos_Viaje'] = df['Tiempo_Viaje_Raw'].apply(convert_time_to_minutes) if 'Tiempo_Viaje_Raw' in df.columns else 0.0
    df['Minutos_Duracion'] = df['Duracion_Raw'].apply(convert_time_to_minutes) if 'Duracion_Raw' in df.columns else 0.0

    # Estado de Actividad
    if 'Estado_Actividad' in df.columns:
        df['Estado_Actividad'] = df['Estado_Actividad'].fillna('No Definido').astype(str).str.strip().str.capitalize()
    else:
        df['Estado_Actividad'] = 'No Definido'

    # Subtipo de Actividad (Tipo de actividad.1) y Categoría (Operativa vs Rutina)
    if 'Subtipo_Actividad' not in df.columns:
        df['Subtipo_Actividad'] = df.get('Tipo_Actividad_Base', 'General')
    df['Subtipo_Actividad'] = df['Subtipo_Actividad'].fillna('General').astype(str).str.strip()

    df['Categoria_Labor'] = df['Subtipo_Actividad'].apply(
        lambda x: 'Rutina / Administrativa' if str(x).upper() in ACTIVIDADES_RUTINA else 'Operativa (Daños / OT)'
    )

    # Observaciones y clasificaciones
    for c_txt in ['Observaciones', 'Comentarios_Cancelacion', 'Comentarios_Suspension', 'Comentarios_No_Realizado', 'Motivo_Cancelacion', 'Descripcion_Orden']:
        if c_txt not in df.columns:
            df[c_txt] = ''
        else:
            df[c_txt] = df[c_txt].fillna('').astype(str)

    df['Etiqueta_Hallazgo'] = df['Observaciones'].apply(classify_observaciones)
    df['Origen_Cancelacion'] = df.apply(classify_cancelacion, axis=1)

    # Nodos / Equipos extraídos tal cual
    df['Lista_Nodos'] = df.apply(extract_nodes_preserve_exact, axis=1)
    df['Nodos_Detectados'] = df['Lista_Nodos'].apply(lambda lst: ", ".join(lst) if lst else "")

    # Tiempo de reacción
    df['Minutos_Reaccion'] = df.apply(calc_reaction_minutes, axis=1)

    # Coordenadas Geográficas
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
    """Descarga y concatena las hojas del Excel desde el URL de Drive."""
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
    """Retorna etiqueta HTML según regla: >=85% Verde, 50-84.9% Amarillo, <50% Rojo."""
    if val >= 85.0:
        return f'<span class="badge-green">🟢 {val:.1f}% (Óptimo)</span>'
    elif val >= 50.0:
        return f'<span class="badge-yellow">🟡 {val:.1f}% (Seguimiento)</span>'
    else:
        return f'<span class="badge-red">🔴 {val:.1f}% (Crítico)</span>'


def multiselect_with_all(label, options, key_prefix, default_all=True):
    """Crea un multiselect limpio donde vacío selecciona todos los elementos disponibles."""
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
    st.caption("Gestión en Tiempo Real de Brigadas")
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
    st.markdown("**2. Parámetros de Turno y Labor**")
    
    modo_enfoque = st.radio(
        "Enfoque de Actividades:",
        options=[
            "Solo Operativas (Daños / OT)",
            "Todas las Actividades Consolidadas",
            "Solo Rutina / Administrativas"
        ],
        index=0,
        help="Separa las órdenes reales de terreno (Incidentes, MT, OT) de las actividades de rutina (Inicio/Fin turno, Alimentación, Charlas)."
    )
    
    horas_turno = st.slider(
        "Jornada Laboral por Día Activo (Horas):",
        min_value=6.0,
        max_value=12.0,
        value=8.0,
        step=0.5
    )
    
    descontar_almuerzo = st.checkbox(
        "Descontar tiempo de 'Alimentación' de la jornada disponible",
        value=True
    )

    excluir_rpa_egam_efectividad = st.checkbox(
        "Excluir canceladas por EGAM / RPA del cálculo de Efectividad",
        value=False,
        help="Si lo activas, las órdenes canceladas por sistema RPA o consola EGAM no castigan el % de cumplimiento de la brigada."
    )

    st.markdown("---")
    st.markdown("**3. Filtros de Tiempo (Multiselección)**")
    
    sel_anios = multiselect_with_all("Año(s):", df_raw['Anio'].unique(), "anio")
    df_f = df_raw[df_raw['Anio'].isin(sel_anios)].copy()
    
    sel_meses = multiselect_with_all("Mes(es):", df_f['Mes_Nombre'].unique(), "mes")
    df_f = df_f[df_f['Mes_Nombre'].isin(sel_meses)].copy()
    
    sel_fechas = multiselect_with_all("Día(s) / Fecha(s):", df_f['Fecha_Str'].unique(), "fecha")
    df_f = df_f[df_f['Fecha_Str'].isin(sel_fechas)].copy()

    st.markdown("---")
    st.markdown("**4. Filtros Geográficos y Operativos**")
    
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
noreal_act = int((df_f['Estado_Actividad'].str.lower() == 'no realizado').sum())

# Contabilizar canceladas por EGAM y RPA
canc_egam = int((df_f['Origen_Cancelacion'] == "🖥️ Cancelado por EGAM").sum())
canc_rpa = int((df_f['Origen_Cancelacion'] == "🤖 Agrupación Automática RPA").sum())

if excluir_rpa_egam_efectividad:
    denom_global = max(1, total_act - (canc_egam + canc_rpa))
    efectividad_global = (fin_act / denom_global * 100.0) if total_act > 0 else 0.0
else:
    efectividad_global = (fin_act / total_act * 100.0) if total_act > 0 else 0.0

prom_viaje_global = df_f['Minutos_Viaje'].mean() if total_act > 0 else 0.0
prom_faena_global = df_f['Minutos_Duracion'].mean() if total_act > 0 else 0.0
prom_reaccion_global = df_f['Minutos_Reaccion'].dropna().mean() if not df_f['Minutos_Reaccion'].dropna().empty else 0.0

brigadas_activas = df_f['Recurso'].nunique()
dias_unicos = df_f['Fecha_Str'].nunique()

# Agrupación por Brigada
rec_stats = df_f.groupby(['Recurso', 'Sector', 'Zona_Oficial']).agg(
    Dias_Activos=('Fecha_Str', 'nunique'),
    Total_Asignadas=('ID_Actividad', 'count'),
    Finalizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'finalizada').sum()),
    Canceladas=('Estado_Actividad', lambda x: (x.str.lower() == 'cancelada').sum()),
    Canc_EGAM=('Origen_Cancelacion', lambda x: (x == "🖥️ Cancelado por EGAM").sum()),
    Canc_RPA=('Origen_Cancelacion', lambda x: (x == "🤖 Agrupación Automática RPA").sum()),
    Suspendidas=('Estado_Actividad', lambda x: (x.str.lower() == 'suspendida').sum()),
    No_Realizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'no realizado').sum()),
    Min_Viaje_Total=('Minutos_Viaje', 'sum'),
    Min_Faena_Total=('Minutos_Duracion', 'sum'),
    Prom_Viaje_Min=('Minutos_Viaje', 'mean'),
    Prom_Faena_Min=('Minutos_Duracion', 'mean'),
    Prom_Reaccion_Min=('Minutos_Reaccion', 'mean')
).reset_index()

rutina_stats = df_contexto_turno.groupby('Recurso').agg(
    Dias_Turno_Real=('Fecha_Str', 'nunique'),
    Min_Alimentacion=('Minutos_Duracion', lambda s: s[df_contexto_turno.loc[s.index, 'Subtipo_Actividad'].str.upper().isin(['ALIMENTACIÓN', 'ALIMENTACION'])].sum()),
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

rec_stats['Horas_Turno_Periodo'] = (rec_stats['Dias_Turno_Real'].replace(0, 1) * horas_turno).round(2)
rec_stats['Horas_Almuerzo'] = (rec_stats['Min_Alimentacion'] / 60.0).round(2)
rec_stats['Horas_Ocupadas'] = ((rec_stats['Min_Viaje_Total'] + rec_stats['Min_Faena_Total']) / 60.0).round(2)

if descontar_almuerzo:
    horas_disp_neta = rec_stats['Horas_Turno_Periodo'] - rec_stats['Horas_Almuerzo']
else:
    horas_disp_neta = rec_stats['Horas_Turno_Periodo']

rec_stats['Horas_Sin_Atender'] = (horas_disp_neta - rec_stats['Horas_Ocupadas']).apply(lambda x: max(0.0, round(x, 2)))
rec_stats['Prom_Viaje_Min'] = rec_stats['Prom_Viaje_Min'].round(1)
rec_stats['Prom_Faena_Min'] = rec_stats['Prom_Faena_Min'].round(1)
rec_stats['Prom_Reaccion_Min'] = rec_stats['Prom_Reaccion_Min'].fillna(0.0).round(1)


# -----------------------------------------------------------------------------
# 9. ENCABEZADO Y TARJETAS KPI PRINCIPALES
# -----------------------------------------------------------------------------
st.markdown("### ⚡ Centro de Control y Seguimiento Diario de Brigadas (BOL)")
st.caption(
    f"Modo activo: **{modo_enfoque}** | Días evaluados: **{dias_unicos}** | "
    f"Brigadas activas: **{brigadas_activas}** | Meta de Cumplimiento: **≥ 85%**"
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
        <div class="metric-title">Prom. Desplazamiento</div>
        <div class="metric-value">{prom_viaje_global:.0f} <span style="font-size:1rem;color:#64748b;">min</span></div>
        <div class="metric-sub">Total ruta: {(df_f['Minutos_Viaje'].sum()/60):.1f} hrs</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Prom. Atención (Faena)</div>
        <div class="metric-value">{prom_faena_global:.0f} <span style="font-size:1rem;color:#64748b;">min</span></div>
        <div class="metric-sub">Total labor: {(df_f['Minutos_Duracion'].sum()/60):.1f} hrs</div>
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


# -----------------------------------------------------------------------------
# 10. PESTAÑAS DE NAVEGACIÓN PROFESIONAL (7 PESTAÑAS ESPECIALIZADAS)
# -----------------------------------------------------------------------------
tab_brigadas, tab_zonas, tab_tiempos, tab_nodos, tab_obs, tab_mapa, tab_datos = st.tabs([
    "👷 Control Brigadas y Standby",
    "🗺️ Desempeño Zonas Oficiales",
    "⏱️ Tiempos y Reacción",
    "⚡ Nodos y Equipos Recurrentes",
    "🔍 Observaciones y Cancelados EGAM/RPA",
    "📍 Mapa y Trazabilidad de Ruta",
    "📋 Base Consolidada"
])

# ================= TAB 1: CONTROL DE BRIGADAS Y STANDBY =================
with tab_brigadas:
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.markdown("##### ⏳ Top 15 Brigadas con Mayor Tiempo Sin Atender (Standby en Horas)")
        df_top_sb = rec_stats.sort_values(by='Horas_Sin_Atender', ascending=False).head(15)
        fig_sb = px.bar(
            df_top_sb,
            x='Horas_Sin_Atender',
            y='Recurso',
            color='Sector',
            orientation='h',
            text='Horas_Sin_Atender',
            hover_data=['Zona_Oficial', 'Horas_Ocupadas', 'Total_Asignadas', 'Finalizadas'],
            color_discrete_map={'CENTRO': '#1e293b', 'NORTE': '#2563eb', 'OTRO': '#64748b'},
            labels={'Horas_Sin_Atender': 'Horas Sin Atender (Standby)', 'Recurso': 'Brigada'}
        )
        fig_sb.update_traces(texttemplate='%{text:.1f} h', textposition='outside')
        fig_sb.update_layout(yaxis=dict(autorange="reversed"), height=400, margin=dict(t=10, b=10, l=10, r=40))
        st.plotly_chart(fig_sb, use_container_width=True)

    with col_b2:
        st.markdown("##### 🎯 Cumplimiento de Efectividad por Brigada (Semáforo Oficial)")
        df_top_ef = rec_stats.sort_values(by='Efectividad_%', ascending=True).head(15)
        fig_ef = px.bar(
            df_top_ef,
            x='Efectividad_%',
            y='Recurso',
            color='Semaforo',
            orientation='h',
            text='Efectividad_%',
            hover_data=['Zona_Oficial', 'Finalizadas', 'Total_Asignadas'],
            color_discrete_map={
                "🟢 >= 85% (Óptimo)": "#10b981",
                "🟡 50% - 84% (Regular)": "#f59e0b",
                "🔴 < 50% (Crítico)": "#ef4444"
            },
            labels={'Efectividad_%': '% Cumplimiento / Efectividad', 'Recurso': 'Brigada'}
        )
        fig_ef.add_vline(x=85, line_dash="dash", line_color="#166534", annotation_text="Meta 85%")
        fig_ef.add_vline(x=50, line_dash="dot", line_color="#991b1b", annotation_text="Mín 50%")
        fig_ef.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_ef.update_layout(height=400, margin=dict(t=10, b=10, l=10, r=40), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_ef, use_container_width=True)

    st.markdown("##### 📊 Matriz Integral de Control por Brigada")
    cols_show_brig = [
        'Recurso', 'Sector', 'Zona_Oficial', 'Semaforo', 'Efectividad_%',
        'Dias_Activos', 'Total_Asignadas', 'Finalizadas', 'Fin_Por_Dia',
        'Canceladas', 'Canc_EGAM', 'Canc_RPA', 'Suspendidas', 'No_Realizadas',
        'Prom_Viaje_Min', 'Prom_Faena_Min', 'Prom_Reaccion_Min',
        'Horas_Ocupadas', 'Horas_Sin_Atender', 'Primer_Inicio', 'Ultimo_Fin'
    ]
    st.dataframe(
        rec_stats[cols_show_brig].sort_values(by='Horas_Sin_Atender', ascending=False),
        column_config={
            "Zona_Oficial": "Zona Asignada",
            "Semaforo": "Estado Meta",
            "Efectividad_%": st.column_config.ProgressColumn("Efectividad (%)", format="%.1f%%", min_value=0, max_value=100),
            "Dias_Activos": "Días",
            "Total_Asignadas": "Asignadas",
            "Fin_Por_Dia": st.column_config.NumberColumn("Fin. / Día", format="%.1f"),
            "Canc_EGAM": "Canc. EGAM",
            "Canc_RPA": "Canc. RPA",
            "Prom_Viaje_Min": st.column_config.NumberColumn("Viaje Prom.", format="%.0f min"),
            "Prom_Faena_Min": st.column_config.NumberColumn("Faena Prom.", format="%.0f min"),
            "Prom_Reaccion_Min": st.column_config.NumberColumn("Reacción", format="%.0f min"),
            "Horas_Ocupadas": st.column_config.NumberColumn("Hrs Labor", format="%.2f h"),
            "Horas_Sin_Atender": st.column_config.NumberColumn("Hrs Standby", format="%.2f h"),
            "Primer_Inicio": "1er Inicio",
            "Ultimo_Fin": "Último Cierre"
        },
        use_container_width=True,
        hide_index=True
    )

# ================= TAB 2: DESEMPEÑO POR ZONAS OFICIALES =================
with tab_zonas:
    zona_summary = df_f.groupby(['Sector', 'Zona_Oficial']).agg(
        Brigadas=('Recurso', 'nunique'),
        Total_Actividades=('ID_Actividad', 'count'),
        Finalizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'finalizada').sum()),
        Canceladas=('Estado_Actividad', lambda x: (x.str.lower() == 'cancelada').sum()),
        Suspendidas=('Estado_Actividad', lambda x: (x.str.lower() == 'suspendida').sum()),
        Horas_Viaje=('Minutos_Viaje', lambda x: round(x.sum() / 60.0, 2)),
        Horas_Faena=('Minutos_Duracion', lambda x: round(x.sum() / 60.0, 2)),
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
            color_discrete_map={'Finalizadas': '#10b981', 'Canceladas': '#ef4444', 'Suspendidas': '#f59e0b'},
            labels={'value': 'Cantidad de Actividades', 'Zona_Oficial': 'Zona Oficial'}
        )
        fig_z_vol.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_z_vol, use_container_width=True)

    with col_z2:
        st.markdown("##### 🚗 Comparativa por Zona: Horas en Ruta (Viaje) vs. Horas en Atención (Faena)")
        fig_z_time = px.bar(
            zona_summary,
            x='Zona_Oficial',
            y=['Horas_Viaje', 'Horas_Faena'],
            barmode='group',
            color_discrete_map={'Horas_Viaje': '#3b82f6', 'Horas_Faena': '#0f172a'},
            labels={'value': 'Horas Acumuladas', 'Zona_Oficial': 'Zona Oficial'}
        )
        fig_z_time.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_z_time, use_container_width=True)

    st.markdown("##### 📋 Resumen Ejecutivo por Zona Oficial")
    st.dataframe(
        zona_summary,
        column_config={
            "Efectividad_%": st.column_config.ProgressColumn("Efectividad (%)", format="%.1f%%", min_value=0, max_value=100),
            "Prom_Viaje_Min": st.column_config.NumberColumn("Prom. Viaje", format="%.1f min"),
            "Prom_Faena_Min": st.column_config.NumberColumn("Prom. Faena", format="%.1f min"),
            "Horas_Viaje": st.column_config.NumberColumn("Total Viaje", format="%.2f h"),
            "Horas_Faena": st.column_config.NumberColumn("Total Faena", format="%.2f h")
        },
        use_container_width=True,
        hide_index=True
    )

# ================= TAB 3: TIEMPOS, REACCIÓN Y TRAZA HORARIA =================
with tab_tiempos:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("##### ⚡ Tiempo Promedio de Reacción por Brigada (Asignación ➔ Inicio)")
        reac_df = rec_stats[rec_stats['Prom_Reaccion_Min'] > 0].sort_values(by='Prom_Reaccion_Min', ascending=False).head(15)
        if not reac_df.empty:
            fig_reac = px.bar(
                reac_df,
                x='Prom_Reaccion_Min',
                y='Recurso',
                color='Zona_Oficial',
                orientation='h',
                text='Prom_Reaccion_Min',
                labels={'Prom_Reaccion_Min': 'Minutos Promedio de Reacción', 'Recurso': 'Brigada'}
            )
            fig_reac.update_traces(texttemplate='%{text:.0f} min', textposition='outside')
            fig_reac.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=10, b=10, l=10, r=40))
            st.plotly_chart(fig_reac, use_container_width=True)
        else:
            st.info("No hay registros con diferencia horaria entre asignación e inicio en esta selección.")

    with col_t2:
        st.markdown("##### 📊 Desglose por Tipo de Actividad (`Tipo de actividad.1`)")
        sub_counts = df_f.groupby(['Subtipo_Actividad', 'Estado_Actividad']).size().reset_index(name='Cantidad')
        fig_sub = px.bar(
            sub_counts,
            x='Cantidad',
            y='Subtipo_Actividad',
            color='Estado_Actividad',
            orientation='h',
            barmode='stack',
            color_discrete_map={'Finalizada': '#10b981', 'Cancelada': '#ef4444', 'Suspendida': '#f59e0b', 'No realizado': '#64748b'}
        )
        fig_sub.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown("##### 📈 Comportamiento Diario de Actividades (Evolución Temporal)")
    diario_df = df_f.groupby(['Fecha_Str', 'Estado_Actividad']).size().reset_index(name='Cantidad')
    fig_evol = px.bar(
        diario_df,
        x='Fecha_Str',
        y='Cantidad',
        color='Estado_Actividad',
        barmode='group',
        color_discrete_map={'Finalizada': '#10b981', 'Cancelada': '#ef4444', 'Suspendida': '#f59e0b', 'No realizado': '#64748b'},
        labels={'Fecha_Str': 'Fecha Operativa', 'Cantidad': 'N° de Actividades'}
    )
    fig_evol.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_evol, use_container_width=True)

# ================= TAB 4: NODOS Y EQUIPOS RECURRENTES =================
with tab_nodos:
    st.markdown("##### ⚡ Detección de Nodos / Equipos Recurrentes para Visita Especializada")
    st.caption("Extrae exactamente tal cual fueron reportados los códigos que inician por **6**, **PF**, **RB**, **RC**, **CD** o **S** en Observaciones, Comentarios y Descripción.")

    # Expandir filas con nodos detectados
    rows_nodos = []
    for idx, r in df_f.iterrows():
        for nd in r['Lista_Nodos']:
            rows_nodos.append({
                'Nodo_Equipo': nd,
                'Tipo_Equipo': classify_node_type(nd),
                'Sector': r['Sector'],
                'Zona_Oficial': r['Zona_Oficial'],
                'Recurso': r['Recurso'],
                'Fecha_Str': r['Fecha_Str'],
                'Orden_Trabajo': r['Orden_Trabajo'],
                'ID_Actividad': r['ID_Actividad'],
                'Estado_Actividad': r['Estado_Actividad'],
                'Observaciones': r['Observaciones'],
                'Comentarios_Suspension': r['Comentarios_Suspension'],
                'Descripcion_Orden': r['Descripcion_Orden']
            })

    if rows_nodos:
        df_nodos_exp = pd.DataFrame(rows_nodos)
        
        # Filtro rápido por tipo de equipo o código específico
        c_nd1, c_nd2 = st.columns([1, 1])
        with c_nd1:
            tipos_eq = ["Todos"] + sorted(df_nodos_exp['Tipo_Equipo'].unique().tolist())
            sel_tipo_eq = st.selectbox("Filtrar por Familia de Equipo:", tipos_eq)
        with c_nd2:
            buscar_nodo = st.text_input("Buscar código exacto de Nodo/Equipo (ej. RB1950, CD23329, 65922036):", "")

        df_nodos_filt = df_nodos_exp.copy()
        if sel_tipo_eq != "Todos":
            df_nodos_filt = df_nodos_filt[df_nodos_filt['Tipo_Equipo'] == sel_tipo_eq]
        if buscar_nodo.strip():
            df_nodos_filt = df_nodos_filt[df_nodos_filt['Nodo_Equipo'].str.contains(buscar_nodo.strip().upper(), na=False)]

        # Agrupar recurrencia por Nodo
        resumen_nodos = df_nodos_filt.groupby(['Nodo_Equipo', 'Tipo_Equipo', 'Sector', 'Zona_Oficial']).agg(
            Veces_Intervenido=('ID_Actividad', 'count'),
            Ordenes_Asociadas=('Orden_Trabajo', lambda s: ", ".join(sorted(set(s)))),
            Brigadas_Que_Asistieron=('Recurso', lambda s: ", ".join(sorted(set(s)))),
            Fechas=('Fecha_Str', lambda s: ", ".join(sorted(set(s)))),
            Estados=('Estado_Actividad', lambda s: ", ".join(sorted(set(s))))
        ).reset_index().sort_values(by='Veces_Intervenido', ascending=False)

        col_ng1, col_ng2 = st.columns([1.2, 1])
        with col_ng1:
            st.markdown("###### 🔥 Top 15 Nodos / Equipos con Mayor Reincidencia")
            fig_nodos = px.bar(
                resumen_nodos.head(15),
                x='Veces_Intervenido',
                y='Nodo_Equipo',
                color='Tipo_Equipo',
                orientation='h',
                text='Veces_Intervenido',
                hover_data=['Zona_Oficial', 'Brigadas_Que_Asistieron']
            )
            fig_nodos.update_traces(textposition='outside')
            fig_nodos.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=10, b=10, l=10, r=40))
            st.plotly_chart(fig_nodos, use_container_width=True)

        with col_ng2:
            st.markdown("###### 📊 Distribución por Tipo de Elemento de Red")
            tipo_cnt = resumen_nodos.groupby('Tipo_Equipo')['Veces_Intervenido'].sum().reset_index()
            fig_tp_nd = px.pie(tipo_cnt, values='Veces_Intervenido', names='Tipo_Equipo', hole=0.45)
            fig_tp_nd.update_layout(height=360, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_tp_nd, use_container_width=True)

        st.markdown("###### 📋 Priorización de Nodos para Programar Visita Especializada")
        st.dataframe(resumen_nodos, use_container_width=True, hide_index=True)

        with st.expander("🔎 Ver Detalle Técnico Completo de las Órdenes por Nodo"):
            st.dataframe(df_nodos_filt, use_container_width=True, hide_index=True)
    else:
        st.info("No se detectaron códigos de nodos (6..., PF..., RB..., RC..., CD..., S...) en la selección actual.")

# ================= TAB 5: OBSERVACIONES Y AUDITORÍA DE CANCELADOS EGAM/RPA =================
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
                text='Cantidad',
                title="Clasificación de Canceladas (EGAM, RPA y Operativo)"
            )
            fig_orig_c.update_traces(textposition='outside')
            fig_orig_c.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=320, margin=dict(t=35, b=10, l=10, r=40))
            st.plotly_chart(fig_orig_c, use_container_width=True)

        with col_c2:
            mot_counts = df_canc_only['Motivo_Cancelacion'].replace('', 'Sin Motivo').value_counts().head(10).reset_index()
            mot_counts.columns = ['Motivo Oficial WFM', 'Cantidad']
            fig_mot_c = px.pie(mot_counts, values='Cantidad', names='Motivo Oficial WFM', hole=0.45, title="Motivo de Cancelación en Sistema")
            fig_mot_c.update_layout(height=320, margin=dict(t=35, b=10, l=10, r=10))
            st.plotly_chart(fig_mot_c, use_container_width=True)
    else:
        st.info("No hay actividades en estado 'Cancelada' dentro de los filtros actuales.")

    st.markdown("---")
    st.markdown("##### 🔎 Buscador Rápido por Orden de Trabajo, ID de Actividad y Observaciones")
    
    col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
    with col_s1:
        buscar_ot_obs = st.text_input(
            "📋 Buscar por Orden de Trabajo o ID Actividad:",
            placeholder="Ej: 146616419 o ADMS-INC o 44532903..."
        )
    with col_s2:
        palabra_clave = st.text_input(
            "📝 Buscar palabra clave en Observaciones / Comentarios:",
            placeholder="Ej: cañuela, vegetación, L.V, lluvias, EGAM, RPA..."
        )
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

    st.caption(f"Mostrando **{len(df_obs_view)}** registros coincidentes.")

    cols_obs_table = [c for c in [
        'Fecha_Str', 'Sector', 'Zona_Oficial', 'Recurso',
        'Orden_Trabajo', 'ID_Actividad', 'Subtipo_Actividad',
        'Estado_Actividad', 'Origen_Cancelacion', 'Nodos_Detectados',
        'Etiqueta_Hallazgo', 'Observaciones',
        'Comentarios_Cancelacion', 'Comentarios_Suspension', 'Descripcion_Orden'
    ] if c in df_obs_view.columns]
    
    st.dataframe(
        df_obs_view[cols_obs_table],
        column_config={
            "Fecha_Str": "Fecha",
            "Orden_Trabajo": "Orden de Trabajo",
            "ID_Actividad": "ID Actividad",
            "Origen_Cancelacion": "Clasificación Cancelado",
            "Nodos_Detectados": "Nodos / Equipos",
            "Observaciones": st.column_config.TextColumn("Observaciones del Recurso", width="large")
        },
        use_container_width=True,
        hide_index=True
    )

# ================= TAB 6: MAPA GEOGRÁFICO Y TRAZABILIDAD DE RUTA =================
with tab_mapa:
    st.markdown("##### 📍 Georreferenciación, Buscador de OT y Trazabilidad de Ruta por Brigada")
    df_map = df_f.dropna(subset=['Lat', 'Lon']).copy()
    
    if not df_map.empty:
        col_m1, col_m2, col_m3 = st.columns([1.2, 1.2, 1])
        with col_m1:
            ot_texto_map = st.text_input(
                "🔎 Buscar Orden de Trabajo o ID en el Mapa (Texto libre):",
                placeholder="Escribe el número de OT o ID..."
            )
        with col_m2:
            lista_ots_mapa = ["Todas"] + sorted([
                f"{r['Orden_Trabajo']} | ID:{r['ID_Actividad']} ({r['Recurso']})"
                for _, r in df_map.iterrows()
            ])
            sel_ot_dropdown = st.selectbox("📌 O selecciona una Orden específica de la lista:", lista_ots_mapa)
        with col_m3:
            st.markdown("<br>", unsafe_allow_html=True)
            ver_trazabilidad = st.checkbox(
                "🛣️ Ver Trazabilidad / Orden de Atención",
                value=False,
                help="Ordena cronológicamente los avisos atendidos por la brigada y dibuja la ruta seguida."
            )

        # Aplicar filtro de búsqueda de OT en el mapa
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

        if df_map.empty:
            st.warning("No se encontraron coordenadas para esa Orden de Trabajo específica.")
        else:
            # Si se activa la trazabilidad, ordenar por Fecha e Inicio y calcular secuencia
            if ver_trazabilidad:
                df_map['Hora_Orden'] = df_map['Inicio'].fillna('23:59').astype(str)
                df_map = df_map.sort_values(by=['Recurso', 'Fecha_Str', 'Hora_Orden']).reset_index(drop=True)
                df_map['Orden_Secuencia'] = df_map.groupby(['Recurso', 'Fecha_Str']).cumcount() + 1
                df_map['Etiqueta_Parada'] = "Parada #" + df_map['Orden_Secuencia'].astype(str) + " (" + df_map['Inicio'].fillna('--:--').astype(str) + ")"

            color_map_estados = {
                'Finalizada': '#10b981',
                'Cancelada': '#ef4444',
                'Suspendida': '#f59e0b',
                'No realizado': '#64748b'
            }

            hover_cols_map = ['Orden_Trabajo', 'ID_Actividad', 'Zona_Oficial', 'Subtipo_Actividad', 'Inicio', 'Finalización', 'Minutos_Viaje', 'Minutos_Duracion', 'Nodos_Detectados', 'Observaciones']
            if ver_trazabilidad:
                hover_cols_map = ['Etiqueta_Parada'] + hover_cols_map

            # Renderizar mapa compatible con Plotly 5 y Plotly 6+
            if hasattr(px, "scatter_map"):
                if ver_trazabilidad and len(df_map) > 1:
                    fig_map = px.line_map(
                        df_map,
                        lat='Lat',
                        lon='Lon',
                        color='Recurso',
                        hover_name='Etiqueta_Parada',
                        hover_data=hover_cols_map,
                        zoom=zoom_level,
                        height=540
                    )
                    fig_map.update_traces(mode="lines+markers+text", text=df_map['Orden_Secuencia'].astype(str), textposition="top right")
                else:
                    fig_map = px.scatter_map(
                        df_map,
                        lat='Lat',
                        lon='Lon',
                        color='Estado_Actividad',
                        hover_name='Recurso',
                        hover_data=hover_cols_map,
                        color_discrete_map=color_map_estados,
                        zoom=zoom_level,
                        height=540
                    )
                fig_map.update_layout(map_style="open-street-map", margin=dict(t=0, b=0, l=0, r=0))
            else:
                if ver_trazabilidad and len(df_map) > 1:
                    fig_map = px.line_mapbox(
                        df_map,
                        lat='Lat',
                        lon='Lon',
                        color='Recurso',
                        hover_name='Etiqueta_Parada',
                        hover_data=hover_cols_map,
                        zoom=zoom_level,
                        height=540
                    )
                    fig_map.update_traces(mode="lines+markers+text", text=df_map['Orden_Secuencia'].astype(str), textposition="top right")
                else:
                    fig_map = px.scatter_mapbox(
                        df_map,
                        lat='Lat',
                        lon='Lon',
                        color='Estado_Actividad',
                        hover_name='Recurso',
                        hover_data=hover_cols_map,
                        color_discrete_map=color_map_estados,
                        zoom=zoom_level,
                        height=540
                    )
                fig_map.update_layout(mapbox_style="open-street-map", margin=dict(t=0, b=0, l=0, r=0))

            st.plotly_chart(fig_map, use_container_width=True)

            if ver_trazabilidad:
                st.markdown("###### 🛣️ Secuencia Cronológica de Atención (Trazabilidad Paso a Paso)")
                cols_traza = [
                    'Orden_Secuencia', 'Recurso', 'Fecha_Str', 'Orden_Trabajo', 'ID_Actividad',
                    'Subtipo_Actividad', 'Estado_Actividad', 'Hora_Asignacion', 'Inicio', 'Finalización',
                    'Minutos_Viaje', 'Minutos_Duracion', 'Nodos_Detectados', 'Observaciones'
                ]
                st.dataframe(
                    df_map[[c for c in cols_traza if c in df_map.columns]],
                    column_config={
                        "Orden_Secuencia": "Parada #",
                        "Fecha_Str": "Fecha",
                        "Orden_Trabajo": "Orden de Trabajo",
                        "Minutos_Viaje": st.column_config.NumberColumn("Viaje (min)", format="%.0f"),
                        "Minutos_Duracion": st.column_config.NumberColumn("Faena (min)", format="%.0f"),
                        "Observaciones": st.column_config.TextColumn("Observaciones", width="large")
                    },
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("No se encontraron coordenadas geográficas válidas ('lat:...,lng:...') en los registros filtrados.")

# ================= TAB 7: BASE CONSOLIDADA Y AUDITORÍA =================
with tab_datos:
    st.markdown("##### 📋 Registros Consolidados con Orden de Trabajo, Nodos y Observaciones")
    
    cols_auditoria = [c for c in [
        'Fecha_Str', 'Anio', 'Mes_Nombre', 'Sector', 'Zona_Oficial', 'Recurso',
        'Orden_Trabajo', 'ID_Actividad', 'Subtipo_Actividad', 'Estado_Actividad',
        'Origen_Cancelacion', 'Nodos_Detectados',
        'Hora_Asignacion', 'Inicio', 'Finalización',
        'Minutos_Reaccion', 'Minutos_Viaje', 'Minutos_Duracion',
        'Observaciones', 'Descripcion_Orden', 'Motivo_Cancelacion',
        'Comentarios_Cancelacion', 'Comentarios_Suspension', 'Comentarios_No_Realizado', 'Zona_Trabajo_WFM'
    ] if c in df_f.columns]
    
    st.dataframe(
        df_f[cols_auditoria],
        column_config={
            "Fecha_Str": "Fecha",
            "Anio": "Año",
            "Mes_Nombre": "Mes",
            "Zona_Oficial": "Zona Oficial",
            "Orden_Trabajo": "Orden de Trabajo",
            "ID_Actividad": "ID Actividad",
            "Subtipo_Actividad": "Tipo Actividad.1",
            "Estado_Actividad": "Estado",
            "Origen_Cancelacion": "Origen Cancelado",
            "Nodos_Detectados": "Nodos / Equipos",
            "Minutos_Reaccion": st.column_config.NumberColumn("Reacción (min)", format="%.0f"),
            "Minutos_Viaje": st.column_config.NumberColumn("Viaje (min)", format="%.0f"),
            "Minutos_Duracion": st.column_config.NumberColumn("Duración (min)", format="%.0f"),
            "Observaciones": st.column_config.TextColumn("Observaciones del Recurso", width="large")
        },
        use_container_width=True,
        hide_index=True
    )
    
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
            label="📥 Descargar Resumen por Brigada (CSV)",
            data=csv_resumen,
            file_name="resumen_brigadas_bol.csv",
            mime="text/csv",
            use_container_width=True
        )
