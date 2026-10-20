import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import io
import requests

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL ENLACE DE GOOGLE DRIVE (PEGA AQUÍ TU ENLACE CORPORATIVO)
# -----------------------------------------------------------------------------
# Asegúrate de que el archivo en Drive tenga acceso: "Cualquier persona con el enlace puede ver"
URL_GOOGLE_DRIVE_DEFAULT = "https://docs.google.com/spreadsheets/d/1e80JLTk3YW7c6yxNwiMXq7_5XtpvGd9s/edit?usp=sharing&ouid=116051950038931432257&rtpof=true&sd=true"

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tablero Operativo BOL | Seguimiento y Tiempos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILOS CSS PROFESIONALES Y ELEGANTES (ESTILO EJECUTIVO)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-title {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-sub {
        color: #2563eb;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 2px;
    }
    .alert-card {
        background-color: #fff7ed;
        border-left: 4px solid #f97316;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 6px;
        padding: 8px 18px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
        color: #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# FUNCIONES DE LECTURA Y CONVERSIÓN (LÓGICA BLINDADA INTACTA)
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


def clean_dataframe(df: pd.DataFrame, source_name: str = "") -> pd.DataFrame:
    """Estandariza columnas, asigna sector y convierte tiempos a minutos."""
    if df.empty:
        return df
    
    df = df.copy()
    
    col_mapping = {
        'Estado de actividad': 'Estado_Actividad',
        'Tiempo de viaje': 'Tiempo_Viaje_Raw',
        'Duración': 'Duracion_Raw',
        'ID de actividad': 'ID_Actividad',
        'Zona de trabajo': 'Zona_Trabajo',
        'Tipo de actividad': 'Tipo_Actividad',
        'Descripción de la orden': 'Descripcion_Orden',
        'Motivo de Cancelación': 'Motivo_Cancelacion',
        'Comentarios de Cancelación': 'Comentarios_Cancelacion',
        'Comentarios de Suspensión': 'Comentarios_Suspension'
    }
    for old_col, new_col in col_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
            
    # Garantizar columna Sector
    if 'Sector' not in df.columns:
        if 'NORTE' in source_name.upper():
            df['Sector'] = 'Norte'
        elif 'CENTRO' in source_name.upper():
            df['Sector'] = 'Centro'
        else:
            df['Sector'] = 'Sin Asignar'
    else:
        df['Sector'] = df['Sector'].fillna('Sin Asignar').astype(str).str.title()
        
    # Conversión a minutos
    if 'Tiempo_Viaje_Raw' in df.columns:
        df['Minutos_Viaje'] = df['Tiempo_Viaje_Raw'].apply(convert_time_to_minutes)
    else:
        df['Minutos_Viaje'] = 0.0

    if 'Duracion_Raw' in df.columns:
        df['Minutos_Duracion'] = df['Duracion_Raw'].apply(convert_time_to_minutes)
    else:
        df['Minutos_Duracion'] = 0.0
        
    if 'Estado_Actividad' in df.columns:
        df['Estado_Actividad'] = df['Estado_Actividad'].fillna('No Definido').astype(str).str.strip().str.capitalize()
        
    if 'Recurso' in df.columns:
        df['Recurso'] = df['Recurso'].fillna('Sin Recurso').astype(str).str.strip()

    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.strftime('%Y-%m-%d')

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


# -----------------------------------------------------------------------------
# BARRA LATERAL: CONTROL DE DATOS Y PARÁMETROS OPERATIVOS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ Control Operativo BOL")
    st.caption("Seguimiento de Desplazamientos y Faena")
    st.markdown("---")
    
    st.markdown("**1. Parámetro de Turno**")
    horas_turno = st.slider(
        "Jornada laboral por turno (Horas):",
        min_value=6.0,
        max_value=12.0,
        value=8.0,
        step=0.5,
        help="Base para calcular el tiempo improductivo / disponible sin atender de cada cuadrilla."
    )
    minutos_turno = horas_turno * 60.0

    st.markdown("---")
    st.markdown("**2. Origen del Archivo (Google Drive)**")
    drive_url = st.text_input(
        "URL del Excel en Drive:",
        value=URL_GOOGLE_DRIVE_DEFAULT,
        help="Pega aquí el enlace de tu archivo corporativo compartido."
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_btn2:
        if st.button("Limpiar Caché", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# -----------------------------------------------------------------------------
# CARGA DE DATOS
# -----------------------------------------------------------------------------
if not drive_url or "TU_ID_DE_ARCHIVO" in drive_url:
    st.info("ℹ️ Para iniciar, pega el enlace de tu archivo Excel de Google Drive en la casilla de la barra lateral izquierda.")
    st.stop()

with st.spinner("Sincronizando con Google Drive..."):
    df_raw, err = load_data_from_url(drive_url)

if err:
    st.error(f"Error al conectar con Google Drive: {err}")
    st.warning("Verifica que en Google Drive el enlace esté configurado con acceso: 'Cualquier persona que tenga el vínculo (Lector)'.")
    st.stop()

if df_raw is None or df_raw.empty:
    st.warning("El archivo descargado no contiene registros válidos.")
    st.stop()


# -----------------------------------------------------------------------------
# FILTROS OPERATIVOS DINÁMICOS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("**3. Filtros de Gestión**")
    
    # Filtro Fecha
    fechas_disp = ["Todas"] + sorted([str(f) for f in df_raw['Fecha'].dropna().unique() if str(f).strip()])
    sel_fecha = st.selectbox("Fecha:", fechas_disp)
    
    df_filtered = df_raw.copy()
    if sel_fecha != "Todas":
        df_filtered = df_filtered[df_filtered['Fecha'] == sel_fecha]

    # Filtro Sector
    sectores_disp = ["Todos"] + sorted([str(s) for s in df_filtered['Sector'].dropna().unique() if str(s).strip()])
    sel_sector = st.selectbox("Sector:", sectores_disp)
    if sel_sector != "Todos":
        df_filtered = df_filtered[df_filtered['Sector'] == sel_sector]
        
    # Filtro Recurso (Cuadrilla BOL)
    recursos_disp = ["Todos"] + sorted([str(r) for r in df_filtered['Recurso'].dropna().unique() if str(r).strip()])
    sel_recurso = st.selectbox("Recurso / Cuadrilla BOL:", recursos_disp)
    if sel_recurso != "Todos":
        df_filtered = df_filtered[df_filtered['Recurso'] == sel_recurso]
        
    # Filtro Estado
    estados_disp = ["Todos"] + sorted([str(e) for e in df_filtered['Estado_Actividad'].dropna().unique() if str(e).strip()])
    sel_estado = st.selectbox("Estado de Actividad:", estados_disp)
    if sel_estado != "Todos":
        df_filtered = df_filtered[df_filtered['Estado_Actividad'] == sel_estado]
# -----------------------------------------------------------------------------
# TABLERO PRINCIPAL: MÉTRICAS EJECUTIVAS (SCORECARD)
# -----------------------------------------------------------------------------
st.markdown("### 📊 Monitoreo Operativo de Cuadrillas BOL")
st.caption(f"Filtros activos: Fecha: **{sel_fecha}** | Sector: **{sel_sector}** | Cuadrilla: **{sel_recurso}** | Jornada base: **{horas_turno} horas/turno**")

total_actividades = len(df_filtered)
finalizadas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'finalizada'])
canceladas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'cancelada'])
suspendidas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'suspendida'])
no_realizadas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'no realizado'])

# Cálculo de Efectividad
tasa_efectividad = (finalizadas / total_actividades * 100) if total_actividades > 0 else 0.0

# Promedios de tiempos en minutos
prom_viaje = df_filtered['Minutos_Viaje'].mean() if total_actividades > 0 else 0.0
prom_faena = df_filtered['Minutos_Duracion'].mean() if total_actividades > 0 else 0.0

# Cuadrillas activas
cuadrillas_activas = df_filtered['Recurso'].nunique()
actividades_por_cuadrilla = (total_actividades / cuadrillas_activas) if cuadrillas_activas > 0 else 0.0

# Fila de KPIs
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Actividades</div>
        <div class="metric-value">{total_actividades:,}</div>
        <div class="metric-sub">{cuadrillas_activas} cuadrillas activas</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Efectividad Operativa</div>
        <div class="metric-value">{tasa_efectividad:.1f}%</div>
        <div class="metric-sub">{finalizadas} de {total_actividades} finalizadas</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Prom. Desplazamiento</div>
        <div class="metric-value">{prom_viaje:.0f} <span style="font-size:1.1rem;color:#64748b;">min</span></div>
        <div class="metric-sub">Tiempo en ruta por daño</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Prom. Atención (Faena)</div>
        <div class="metric-value">{prom_faena:.0f} <span style="font-size:1.1rem;color:#64748b;">min</span></div>
        <div class="metric-sub">Tiempo de labor en sitio</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Promedio por Cuadrilla</div>
        <div class="metric-value">{actividades_por_cuadrilla:.1f}</div>
        <div class="metric-sub">Órdenes / cuadrilla / día</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# CÁLCULO DE RENDIMIENTO Y TIEMPO SIN ATENDER POR RECURSO
# -----------------------------------------------------------------------------
rec_group = df_filtered.groupby('Recurso').agg(
    Total_Asignadas=('ID_Actividad', 'count'),
    Finalizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'finalizada').sum()),
    Canceladas=('Estado_Actividad', lambda x: (x.str.lower() == 'cancelada').sum()),
    Suspendidas=('Estado_Actividad', lambda x: (x.str.lower() == 'suspendida').sum()),
    No_Realizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'no realizado').sum()),
    Minutos_Viaje_Total=('Minutos_Viaje', 'sum'),
    Minutos_Faena_Total=('Minutos_Duracion', 'sum'),
    Prom_Viaje_Min=('Minutos_Viaje', 'mean'),
    Prom_Faena_Min=('Minutos_Duracion', 'mean')
).reset_index()

# Efectividad por cuadrilla
rec_group['Efectividad_%'] = ((rec_group['Finalizadas'] / rec_group['Total_Asignadas']) * 100).round(1)

# Tiempo total ocupado (Viaje + Faena) en horas
rec_group['Horas_Ocupadas'] = ((rec_group['Minutos_Viaje_Total'] + rec_group['Minutos_Faena_Total']) / 60.0).round(2)

# Tiempo sin atender / disponible (Standby) en horas
rec_group['Horas_Sin_Atender'] = (horas_turno - rec_group['Horas_Ocupadas']).apply(lambda x: max(0.0, round(x, 2)))
rec_group['Minutos_Sin_Atender'] = (rec_group['Horas_Sin_Atender'] * 60).round(0)

# Alerta del recurso con más tiempo sin atender
top_ocioso = rec_group.sort_values(by='Horas_Sin_Atender', ascending=False).iloc[0] if not rec_group.empty else None

if top_ocioso is not None and top_ocioso['Horas_Sin_Atender'] > 0:
    st.markdown(f"""
    <div class="alert-card">
        ⚠️ <strong>Atención de Disponibilidad:</strong> La cuadrilla con mayor tiempo sin labor registrada es 
        <strong>{top_ocioso['Recurso']}</strong> con <strong>{top_ocioso['Horas_Sin_Atender']} horas</strong> 
        ({top_ocioso['Minutos_Sin_Atender']:.0f} min) disponibles o en standby dentro del turno de {horas_turno} horas. 
        (Atendió {top_ocioso['Total_Asignadas']} actividades, de las cuales finalizó {top_ocioso['Finalizadas']}).
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PESTAÑAS DE ANÁLISIS OPERATIVO
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "👷 Rendimiento y Tiempos por Cuadrilla",
    "⏱️ Matriz de Desplazamiento y Faena",
    "📈 Comportamiento y Actividades por Día",
    "📋 Detalle de Registros y Auditoría"
])

# ----------------- TAB 1: RENDIMIENTO POR CUADRILLA -----------------
with tab1:
    col_t1a, col_t1b = st.columns([1, 1])
    
    with col_t1a:
        st.markdown("##### Ranking de Recursos con Mayor Tiempo Sin Atender (Standby)")
        ranking_ocioso = rec_group.sort_values(by='Horas_Sin_Atender', ascending=False).head(12)
        fig_ocioso = px.bar(
            ranking_ocioso,
            x='Horas_Sin_Atender',
            y='Recurso',
            orientation='h',
            labels={'Horas_Sin_Atender': 'Horas Sin Atender (Turno no ocupado)', 'Recurso': 'Cuadrilla'},
            color='Horas_Sin_Atender',
            color_continuous_scale='Oranges'
        )
        fig_ocioso.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_ocioso, use_container_width=True)
        
    with col_t1b:
        st.markdown("##### Volumen de Actividades por Estado por Cuadrilla (Top 12)")
        top_vol = rec_group.sort_values(by='Total_Asignadas', ascending=False).head(12)
        fig_est = px.bar(
            top_vol,
            x='Recurso',
            y=['Finalizadas', 'Canceladas', 'Suspendidas', 'No_Realizadas'],
            barmode='stack',
            color_discrete_map={
                'Finalizadas': '#10b981',
                'Canceladas': '#ef4444',
                'Suspendidas': '#f59e0b',
                'No_Realizadas': '#64748b'
            }
        )
        fig_est.update_layout(height=360, margin=dict(t=10, b=10, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_est, use_container_width=True)

    st.markdown("##### Tabla de Control y Efectividad por Cuadrilla")
    cols_tabla = [
        'Recurso', 'Total_Asignadas', 'Finalizadas', 'Canceladas', 'Suspendidas',
        'Efectividad_%', 'Prom_Viaje_Min', 'Prom_Faena_Min', 'Horas_Ocupadas', 'Horas_Sin_Atender'
    ]
    st.dataframe(
        rec_group[cols_tabla].sort_values(by='Total_Asignadas', ascending=False),
        column_config={
            "Efectividad_%": st.column_config.ProgressColumn("Efectividad", format="%.1f%%", min_value=0, max_value=100),
            "Prom_Viaje_Min": st.column_config.NumberColumn("Prom. Viaje", format="%.0f min"),
            "Prom_Faena_Min": st.column_config.NumberColumn("Prom. Faena", format="%.0f min"),
            "Horas_Ocupadas": st.column_config.NumberColumn("Horas en Labor", format="%.2f h"),
            "Horas_Sin_Atender": st.column_config.NumberColumn("Horas Standby", format="%.2f h")
        },
        use_container_width=True,
        hide_index=True
    )

# ----------------- TAB 2: MATRIZ DE DESPLAZAMIENTOS -----------------
with tab2:
    col_d1, col_d2 = st.columns([1, 1])
    
    with col_d1:
        st.markdown("##### Distribución: Tiempo de Viaje vs. Tiempo de Atención")
        fig_scatter = px.scatter(
            df_filtered,
            x='Minutos_Viaje',
            y='Minutos_Duracion',
            color='Sector',
            size='Minutos_Duracion',
            hover_data=['Recurso', 'Estado_Actividad'],
            labels={'Minutos_Viaje': 'Minutos en Ruta (Viaje)', 'Minutos_Duracion': 'Minutos en Faena (Atención)'},
            color_discrete_sequence=['#2563eb', '#10b981', '#f59e0b']
        )
        fig_scatter.update_layout(height=360, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_d2:
        st.markdown("##### Cuadrillas con Mayor Tiempo Promedio de Desplazamiento")
        top_viajeras = rec_group.sort_values(by='Prom_Viaje_Min', ascending=False).head(12)
        fig_viajeras = px.bar(
            top_viajeras,
            x='Prom_Viaje_Min',
            y='Recurso',
            orientation='h',
            labels={'Prom_Viaje_Min': 'Minutos Promedio en Ruta'},
            color='Prom_Viaje_Min',
            color_continuous_scale='Blues'
        )
        fig_viajeras.update_layout(yaxis=dict(autorange="reversed"), height=360, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_viajeras, use_container_width=True)

# ----------------- TAB 3: COMPORTAMIENTO POR DÍA -----------------
with tab3:
    st.markdown("##### Tendencia Diaria: Volumen de Actividades Realizadas")
    
    if 'Fecha' in df_filtered.columns and df_filtered['Fecha'].nunique() > 1:
        diario = df_filtered.groupby(['Fecha', 'Estado_Actividad']).size().reset_index(name='Cantidad')
        fig_diario = px.line(
            diario,
            x='Fecha',
            y='Cantidad',
            color='Estado_Actividad',
            markers=True,
            color_discrete_map={
                'Finalizada': '#10b981',
                'Cancelada': '#ef4444',
                'Suspendida': '#f59e0b',
                'No realizado': '#64748b'
            }
        )
        fig_diario.update_layout(height=360, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_diario, use_container_width=True)
    else:
        st.info("ℹ️ Los datos filtrados corresponden a una sola fecha. Al alimentar más días en el Excel de Drive, aquí verás la curva histórica de evolución.")
        
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("##### Motivos Más Frecuentes de Cancelación")
        if 'Motivo_Cancelacion' in df_filtered.columns:
            canc_motivos = df_filtered['Motivo_Cancelacion'].dropna().value_counts().head(8).reset_index()
            canc_motivos.columns = ['Motivo', 'Cantidad']
            fig_canc = px.bar(canc_motivos, x='Cantidad', y='Motivo', orientation='h', color_discrete_sequence=['#ef4444'])
            fig_canc.update_layout(yaxis=dict(autorange="reversed"), height=300, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_canc, use_container_width=True)
        else:
            st.caption("No hay columna de motivos de cancelación disponible.")
            
    with col_c2:
        st.markdown("##### Distribución por Sector")
        sect_counts = df_filtered['Sector'].value_counts().reset_index()
        sect_counts.columns = ['Sector', 'Total']
        fig_sec = px.pie(sect_counts, values='Total', names='Sector', hole=0.5, color_discrete_sequence=['#1e293b', '#3b82f6'])
        fig_sec.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_sec, use_container_width=True)

# ----------------- TAB 4: AUDITORÍA Y REGISTROS -----------------
with tab4:
    st.markdown("##### Registros Consolidados")
    cols_show = [c for c in [
        'Sector', 'Recurso', 'Fecha', 'ID_Actividad', 'Estado_Actividad', 
        'Zona_Trabajo', 'Minutos_Viaje', 'Minutos_Duracion', 'Descripcion_Orden',
        'Motivo_Cancelacion', 'Comentarios_Suspension'
    ] if c in df_filtered.columns]
    
    st.dataframe(df_filtered[cols_show], use_container_width=True, hide_index=True)
    
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar Base Filtrada en CSV",
        data=csv_bytes,
        file_name=f"reporte_operativo_bol_{sel_sector}.csv",
        mime="text/csv"
    )
