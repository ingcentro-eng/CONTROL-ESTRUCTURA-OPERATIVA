import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import io
import requests

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Control Operativo BOL | Seguimiento y Tiempos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILOS CSS PROFESIONALES Y ELEGANTES
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Estilos globales y paleta ejecutiva */
    .main {
        background-color: #f8fafc;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 18px 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 12px;
    }
    .metric-title {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.85rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-sub {
        color: #3b82f6;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 6px;
        padding: 8px 20px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# FUNCIONES AUXILIARES: TRANSFORMACIÓN Y LECTURA
# ---------------------------------------------------------
def convert_time_to_minutes(time_val):
    """Convierte formato HH:MM o timedelta a minutos flotantes."""
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
    """Convierte un enlace compartido de Google Drive en URL de descarga directa."""
    if not url:
        return ""
    # Si es formato docs.google.com/spreadsheets/d/ID/...
    sheets_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
    if sheets_match:
        sheet_id = sheets_match.group(1)
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # Si es formato drive.google.com/file/d/ID/...
    drive_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if drive_match:
        file_id = drive_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
        
    return url


def clean_dataframe(df: pd.DataFrame, source_name: str = "") -> pd.DataFrame:
    """Estandariza columnas, asigna sector y calcula tiempos numéricos."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Estandarizar nombres de columnas principales
    col_mapping = {
        'Estado de actividad': 'Estado_Actividad',
        'Tiempo de viaje': 'Tiempo_Viaje_Raw',
        'Duración': 'Duracion_Raw',
        'ID de actividad': 'ID_Actividad',
        'Zona de trabajo': 'Zona_Trabajo',
        'Tipo de actividad': 'Tipo_Actividad'
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
        
    # Conversión de tiempos a minutos
    if 'Tiempo_Viaje_Raw' in df.columns:
        df['Minutos_Viaje'] = df['Tiempo_Viaje_Raw'].apply(convert_time_to_minutes)
    else:
        df['Minutos_Viaje'] = 0.0

    if 'Duracion_Raw' in df.columns:
        df['Minutos_Duracion'] = df['Duracion_Raw'].apply(convert_time_to_minutes)
    else:
        df['Minutos_Duracion'] = 0.0
        
    if 'Estado_Actividad' in df.columns:
        df['Estado_Actividad'] = df['Estado_Actividad'].fillna('No Definido').str.strip().str.capitalize()
        
    if 'Recurso' in df.columns:
        df['Recurso'] = df['Recurso'].fillna('Sin Recurso').astype(str).str.strip()

    return df


@st.cache_data(ttl=300, show_spinner=False)
def load_data_from_url(drive_url: str):
    """Descarga y procesa el Excel directamente desde el enlace de Google Drive."""
    try:
        direct_url = parse_google_drive_url(drive_url)
        response = requests.get(direct_url, timeout=25)
        response.raise_for_status()
        excel_bytes = io.BytesIO(response.content)
        
        # Lee todas las hojas si existen o la primera por defecto
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


# ---------------------------------------------------------
# BARRA LATERAL: CONTROL DE DATOS Y FILTROS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3256/3256214.png", width=55)
    st.title("Panel de Control")
    st.markdown("---")
    
    st.subheader("1. Origen de Datos")
    
    # Input de URL de Google Drive
    default_url = st.text_input(
        "Enlace de Google Drive (Excel):",
        value="https://docs.google.com/spreadsheets/d/1e80JLTk3YW7c6yxNwiMXq7_5XtpvGd9s/edit?usp=sharing&ouid=116051950038931432257&rtpof=true&sd=true",
        help="El archivo debe tener permiso: 'Cualquier persona con el enlace puede ver'"
    )
    
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        btn_recargar = st.button("🔄 Recargar", use_container_width=True)
    with col_btn2:
        if st.button("Limpiar Caché", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")
    st.subheader("O bien, Cargue Manual:")
    uploaded_files = st.file_uploader(
        "Subir archivos del día (.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True
    )

# ---------------------------------------------------------
# CARGA Y PREPARACIÓN DE INFORMACIÓN
# ---------------------------------------------------------
df_raw = None

if uploaded_files:
    dfs = []
    for f in uploaded_files:
        temp_df = pd.read_excel(f)
        temp_df = clean_dataframe(temp_df, source_name=f.name)
        dfs.append(temp_df)
    df_raw = pd.concat(dfs, ignore_index=True)
    if 'ID_Actividad' in df_raw.columns:
        df_raw = df_raw.drop_duplicates(subset=['ID_Actividad'], keep='last')
    st.sidebar.success(f"Archivos locales cargados: {len(df_raw)} registros.")
elif default_url:
    with st.spinner("Conectando con Google Drive y leyendo actividades..."):
        df_raw, err = load_data_from_url(default_url)
        if err:
            st.sidebar.error(f"Error al leer URL: Asegúrate de que el enlace sea público.")
            st.info("💡 Por favor verifica que en Google Drive el enlace esté configurado con: **Cualquier persona con el enlace (Lector)**.")
else:
    st.info("👋 **Bienvenido al Tablero Operativo BOL.** Ingrese el enlace de Google Drive en la barra lateral o arrastre los archivos Excel correspondientes.")
    st.stop()

if df_raw is None or df_raw.empty:
    st.warning("No se encontraron registros válidos para mostrar.")
    st.stop()


# ---------------------------------------------------------
# FILTROS DINÁMICOS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.subheader("2. Filtros Operativos")
    
    # Filtro Sector
    sectores_disp = ["Todos"] + sorted(list(df_raw['Sector'].unique()))
    sel_sector = st.selectbox("Sector:", sectores_disp)
    
    # Filtrado intermedio por sector
    df_filtered = df_raw.copy()
    if sel_sector != "Todos":
        df_filtered = df_filtered[df_filtered['Sector'] == sel_sector]
        
    # Filtro Recursos
    recursos_disp = ["Todos"] + sorted(list(df_filtered['Recurso'].unique()))
    sel_recurso = st.selectbox("Cuadrilla / Recurso (BOL):", recursos_disp)
    if sel_recurso != "Todos":
        df_filtered = df_filtered[df_filtered['Recurso'] == sel_recurso]
        
    # Filtro Estados
    estados_disp = ["Todos"] + sorted(list(df_filtered['Estado_Actividad'].unique()))
    sel_estado = st.selectbox("Estado de Actividad:", estados_disp)
    if sel_estado != "Todos":
        df_filtered = df_filtered[df_filtered['Estado_Actividad'] == sel_estado]


# ---------------------------------------------------------
# ENCABEZADO PRINCIPAL Y RESUMEN EJECUTIVO
# ---------------------------------------------------------
st.markdown("### ⚡ Estructura Operativa BOL - Indicadores de Desplazamiento y Gestión")
st.caption(f"Visualización consolidada para la toma de decisiones | Sector: **{sel_sector}** | Recurso: **{sel_recurso}**")

# Métricas Top
total_actividades = len(df_filtered)
finalizadas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'finalizada'])
canceladas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'cancelada'])
suspendidas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'suspendida'])
no_realizadas = len(df_filtered[df_filtered['Estado_Actividad'].str.lower() == 'no realizado'])

tasa_efectividad = (finalizadas / total_actividades * 100) if total_actividades > 0 else 0
prom_viaje = df_filtered['Minutos_Viaje'].mean() if total_actividades > 0 else 0
prom_duracion = df_filtered['Minutos_Duracion'].mean() if total_actividades > 0 else 0

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Actividades</div>
        <div class="metric-value">{total_actividades:,}</div>
        <div class="metric-sub">Órdenes asignadas</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Efectividad</div>
        <div class="metric-value">{tasa_efectividad:.1f}%</div>
        <div class="metric-sub">{finalizadas} Finalizadas</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Prom. Desplazamiento</div>
        <div class="metric-value">{prom_viaje:.0f} <span style="font-size:1rem;color:#64748b;">min</span></div>
        <div class="metric-sub">Tiempo en ruta</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Prom. Atención (Faena)</div>
        <div class="metric-value">{prom_duracion:.0f} <span style="font-size:1rem;color:#64748b;">min</span></div>
        <div class="metric-sub">Duración efectiva</div>
    </div>
    """, unsafe_allow_html=True)
with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Canceladas / Susp.</div>
        <div class="metric-value">{canceladas + suspendidas}</div>
        <div class="metric-sub">{canceladas} Canc. | {suspendidas} Susp.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PESTAÑAS DETALLADAS DE ANÁLISIS
# ---------------------------------------------------------
tab_general, tab_recursos, tab_desplazamiento, tab_data = st.tabs([
    "📊 Visión General de Estados",
    "👷 Rendimiento por Cuadrilla (BOL)",
    "⏱️ Matriz de Desplazamiento y Tiempos",
    "📋 Detalle de Registros"
])

# ----------------- TAB 1: VISIÓN GENERAL -----------------
with tab_general:
    col_g1, col_g2 = st.columns([1, 1])
    
    with col_g1:
        st.markdown("##### Distribución de Estados de Actividad")
        estado_counts = df_filtered['Estado_Actividad'].value_counts().reset_index()
        estado_counts.columns = ['Estado', 'Cantidad']
        
        # Paleta de colores operacionales
        color_map = {
            'Finalizada': '#10b981',
            'Cancelada': '#ef4444',
            'Suspendida': '#f59e0b',
            'No realizado': '#64748b',
            'Pendiente': '#3b82f6'
        }
        
        fig_pie = px.pie(
            estado_counts,
            values='Cantidad',
            names='Estado',
            color='Estado',
            color_discrete_map=color_map,
            hole=0.45
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_g2:
        st.markdown("##### Actividades por Sector")
        sector_group = df_filtered.groupby(['Sector', 'Estado_Actividad']).size().reset_index(name='Cantidad')
        fig_bar = px.bar(
            sector_group,
            x='Sector',
            y='Cantidad',
            color='Estado_Actividad',
            barmode='stack',
            color_discrete_map=color_map
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- TAB 2: RECURSOS BOL -----------------
with tab_recursos:
    st.markdown("##### Productividad y Efectividad por Cuadrilla")
    
    rec_summary = df_filtered.groupby('Recurso').agg(
        Total=('ID_Actividad', 'count'),
        Finalizadas=('Estado_Actividad', lambda x: (x.str.lower() == 'finalizada').sum()),
        Canceladas=('Estado_Actividad', lambda x: (x.str.lower() == 'cancelada').sum()),
        Prom_Viaje_Min=('Minutos_Viaje', 'mean'),
        Prom_Duracion_Min=('Minutos_Duracion', 'mean')
    ).reset_index()
    
    rec_summary['Efectividad_%'] = (rec_summary['Finalizadas'] / rec_summary['Total'] * 100).round(1)
    rec_summary['Prom_Viaje_Min'] = rec_summary['Prom_Viaje_Min'].round(1)
    rec_summary['Prom_Duracion_Min'] = rec_summary['Prom_Duracion_Min'].round(1)
    rec_summary = rec_summary.sort_values(by='Total', ascending=False)
    
    # Gráfica de Cuadrillas con más actividades
    fig_rec = px.bar(
        rec_summary.head(15),
        x='Recurso',
        y=['Finalizadas', 'Canceladas'],
        title="Top 15 Cuadrillas por Volumen de Actividad",
        barmode='stack',
        color_discrete_map={'Finalizadas': '#10b981', 'Canceladas': '#ef4444'}
    )
    fig_rec.update_layout(height=360, margin=dict(t=40, b=20, l=10, r=10))
    st.plotly_chart(fig_rec, use_container_width=True)
    
    st.dataframe(
        rec_summary,
        column_config={
            "Efectividad_%": st.column_config.ProgressColumn(
                "Efectividad (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Prom_Viaje_Min": st.column_config.NumberColumn("Prom. Viaje (min)", format="%.1f min"),
            "Prom_Duracion_Min": st.column_config.NumberColumn("Prom. Atención (min)", format="%.1f min")
        },
        use_container_width=True,
        hide_index=True
    )

# ----------------- TAB 3: TIEMPOS Y VIAJE -----------------
with tab_desplazamiento:
    col_t1, col_t2 = st.columns([1, 1])
    
    with col_t1:
        st.markdown("##### Comparativa: Desplazamiento vs. Tiempo en Faena")
        # Scatter de viaje vs duración
        fig_scatter = px.scatter(
            df_filtered,
            x='Minutos_Viaje',
            y='Minutos_Duracion',
            color='Sector',
            hover_data=['Recurso', 'Estado_Actividad', 'Dirección'] if 'Dirección' in df_filtered.columns else ['Recurso'],
            labels={'Minutos_Viaje': 'Tiempo de Viaje (Minutos)', 'Minutos_Duracion': 'Tiempo de Atención (Minutos)'},
            color_discrete_sequence=['#2563eb', '#10b981']
        )
        fig_scatter.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_t2:
        st.markdown("##### Cuadrillas con Mayor Tiempo Promedio de Viaje")
        top_viaje = rec_summary.sort_values(by='Prom_Viaje_Min', ascending=False).head(10)
        fig_top_v = px.bar(
            top_viaje,
            x='Prom_Viaje_Min',
            y='Recurso',
            orientation='h',
            labels={'Prom_Viaje_Min': 'Minutos Promedio en Ruta'},
            color='Prom_Viaje_Min',
            color_continuous_scale='Blues'
        )
        fig_top_v.update_layout(yaxis=dict(autorange="reversed"), height=340, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_top_v, use_container_width=True)

# ----------------- TAB 4: TABLA DE DATOS -----------------
with tab_data:
    st.markdown("##### Registros Filtrados")
    cols_vista = [c for c in ['Sector', 'Recurso', 'ID_Actividad', 'Estado_Actividad', 'Fecha', 'Zona_Trabajo', 'Minutos_Viaje', 'Minutos_Duracion', 'Descripción de la orden', 'Motivo de Cancelación'] if c in df_filtered.columns]
    st.dataframe(df_filtered[cols_vista], use_container_width=True, hide_index=True)
    
    # Exportar datos filtrados
    csv_data = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar Vista en CSV",
        data=csv_data,
        file_name="seguimiento_actividades_bol.csv",
        mime="text/csv"
    )
