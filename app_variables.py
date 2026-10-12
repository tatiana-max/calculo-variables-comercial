import io
from datetime import date
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import streamlit as st

# Configuración de la página con diseño ancho
st.set_page_config(
    page_title="Cálculo de Variables", page_icon="💼", layout="wide"
)

# --- ESTILO VISUAL: ROJO CARMESÍ Y LETRA MÁS GRANDE ---
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    h1, h2, h3 {
        color: #DC143C !important;
    }
    .stButton>button {
        background-color: #DC143C;
        color: white;
        border-radius: 5px;
        border: none;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #A30027;
        color: white;
    }
    div[data-testid="metric-container"] {
        background-color: #FFF0F3;
        border: 1px solid #FFCCD5;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("Cálculo de Variables - Comercial")
st.markdown("---")

# --- LISTA DE TODOS LOS COLABORADORES ---
colaboradores_nombres = [
    "David Cárdenas - Gerente de Ventas",
    "Felipe - Ejecutivo / Operaciones",
    "Tatiana Palacios - Asistente de Ventas",
    "Eduardo Flores - Jefe Comercial",
    "Mario Muñoz - Jefe Comercial",
    "Ronald Muñoz - Jefe Comercial",
    "Davis Posligua - Jefe Comercial",
    "Yilberth Ledesma - Jefe Comercial",
]

# Variables máximas totales por cada jefe comercial administrativo
totales_maximos_jefes = {
    "Eduardo Flores - Jefe Comercial": 240.0,
    "Mario Muñoz - Jefe Comercial": 320.0,
    "Ronald Muñoz - Jefe Comercial": 330.0,
    "Davis Posligua - Jefe Comercial": 150.0,
    "Yilberth Ledesma - Jefe Comercial": 220.0,
}

# --- INICIALIZAR ESTADOS GLOBALES DE GRABADO ---
for colab in colaboradores_nombres:
  key_grabado = f"grabado_{colab}"
  key_data = f"data_{colab}"
  if key_grabado not in st.session_state:
    st.session_state[key_grabado] = False
  if key_data not in st.session_state:
    st.session_state[key_data] = None

# --- 1. SELECCIÓN DE COLABORADOR Y PERÍODO ---
st.subheader("1. Selección de Colaborador y Período")

col1_sel, col2_sel = st.columns(2)

with col1_sel:
  colaborador_seleccionado = st.selectbox(
      "Seleccione el colaborador a evaluar:", options=colaboradores_nombres
  )

with col2_sel:
  periodo_evaluacion = st.date_input(
      "Seleccione el período de evaluación:",
      value=(date(2026, 9, 1), date(2026, 9, 30)),
  )

st.markdown("---")

# ==========================================
# 2. EVALUACIÓN SEGÚN EL COLABORADOR SELECCIONADO
# ==========================================

# --- CASO A: DAVID CÁRDENAS ---
if colaborador_seleccionado == "David Cárdenas - Gerente de Ventas":
  variable_total_maxima = 400.0

  if "df_david" not in st.session_state:
    st.session_state.df_david = pd.DataFrame(
        {
            "Variable": [
                "Ventas",
                "Cartera",
                "Visitas",
                "Efectividad",
                "LPP",
                "Clientes nuevos",
            ],
            "Peso (%)": [30, 30, 10, 10, 10, 10],
            "Objetivo Planificado": [1773119.0, 100.0, 150.0, 80.0, 50.0, 20.0],
            "Valor Real Ejecutado": [1674527.0, 90.0, 150.0, 85.0, 45.0, 18.0],
        }
    )

  st.subheader(f"2. Evaluación de Metas: {colaborador_seleccionado}")
  st.write(
      "Modifica los valores en las columnas **Objetivo Planificado** y **Valor"
      " Real Ejecutado**:"
  )


  def calcular_fila_david(row):
    obj = row["Objetivo Planificado"]
    real = row["Valor Real Ejecutado"]
    peso = row["Peso (%)"]
    cumplimiento_calc = (real / obj) * 100 if obj > 0 else 0
    # TOPE MÁXIMO 100% (Sin sobrecumplimientos)
    cumplimiento = min(cumplimiento_calc, 100.0)

    dolares_asig = (peso / 100.0) * variable_total_maxima
    pago = 0.0 if cumplimiento < 90.0 else dolares_asig * (cumplimiento / 100.0)
    return pd.Series(
        [round(cumplimiento, 1), round(pago, 2)],
        index=["% Cumplimiento", "Valor a Pagar ($)"],
    )


  df_trabajo_d = st.session_state.df_david.copy()
  df_trabajo_d[["% Cumplimiento", "Valor a Pagar ($)"]] = df_trabajo_d.apply(
      calcular_fila_david, axis=1
  )

  df_editado_d = st.data_editor(
      df_trabajo_d[[
          "Variable",
          "Peso (%)",
          "Objetivo Planificado",
          "Valor Real Ejecutado",
          "% Cumplimiento",
          "Valor a Pagar ($)",
      ]],
      column_config={
          "Variable": st.column_config.TextColumn(
              "Variable", disabled=True
          ),
          "Peso (%)": st.column_config.NumberColumn(
              "Peso (%)", disabled=True, format="%.1f%%"
          ),
          "Objetivo Planificado": st.column_config.NumberColumn(
              "Objetivo Planificado (Editable)", format="%.2f"
          ),
          "Valor Real Ejecutado": st.column_config.NumberColumn(
              "Valor Real Ejecutado (Editable)", format="%.2f"
          ),
          "% Cumplimiento": st.column_config.NumberColumn(
              "% Cumplimiento (Tope 100%)", disabled=True, format="%.1f%%"
          ),
          "Valor a Pagar ($)": st.column_config.NumberColumn(
              "Valor a Pagar ($)", disabled=True, format="$%.2f"
          ),
      },
      hide_index=True,
      use_container_width=True,
      key="editor_david",
  )

  st.session_state.df_david["Objetivo Planificado"] = df_editado_d[
      "Objetivo Planificado"
  ]
  st.session_state.df_david["Valor Real Ejecutado"] = df_editado_d[
      "Valor Real Ejecutado"
  ]
  st.session_state.df_david[["% Cumplimiento", "Valor a Pagar ($)"]] = (
      st.session_state.df_david.apply(calcular_fila_david, axis=1)
  )

  total_a_pagar_d = st.session_state.df_david["Valor a Pagar ($)"].sum()

  st.markdown("---")
  col1, col2 = st.columns(2)
  col1.metric("Variable Máxima Establecida", f"${variable_total_maxima:,.2f}")
  col2.metric("Total Variable a Pagar", f"${total_a_pagar_d:,.2f}")

  st.markdown("---")
  if st.button(f"Grabar Datos - {colaborador_seleccionado}"):
    st.session_state[f"grabado_{colaborador_seleccionado}"] = True
    st.session_state[f"data_{colaborador_seleccionado}"] = {
        "tipo": "david",
        "df": st.session_state.df_david.copy(),
        "total": total_a_pagar_d,
        "max": variable_total_maxima,
    }
    st.success(f"¡Datos de {colaborador_seleccionado} grabados y acumulados!")


# --- CASO B: FELIPE ---
elif colaborador_seleccionado == "Felipe - Ejecutivo / Operaciones":
  variable_total_maxima_f = 300.0

  st.subheader(f"2. Evaluación de Metas: {colaborador_seleccionado}")
  st.write("Configura los indicadores y adjunta las evidencias fotográficas:")

  st.markdown("#### 1. Presupuesto e Indicador comerciales (Peso: 33.33% - $100)")
  entrego_tiempo_1 = st.radio(
      "¿Entregó en tiempo?",
      options=["Sí", "No"],
      horizontal=True,
      key="tiempo_felipe_1",
  )
  pago_ind1 = 100.0 if entrego_tiempo_1 == "Sí" else 0.0
  foto_evidencia_1 = st.file_uploader(
      "Evidencia fotográfica (Indicador 1):",
      type=["png", "jpg", "jpeg"],
      key="foto_1",
  )
  if foto_evidencia_1:
    st.image(foto_evidencia_1, caption="Evidencia 1", width=300)

  st.markdown("#### 2. Comisiones de Ventas (Peso: 33.33% - $100)")
  entrego_tiempo_2 = st.radio(
      "¿Cumplió con las comisiones de ventas?",
      options=["Sí", "No"],
      horizontal=True,
      key="tiempo_felipe_2",
  )
  pago_ind2 = 100.0 if entrego_tiempo_2 == "Sí" else 0.0
  foto_evidencia_2 = st.file_uploader(
      "Evidencia fotográfica (Indicador 2):",
      type=["png", "jpg", "jpeg"],
      key="foto_2",
  )
  if foto_evidencia_2:
    st.image(foto_evidencia_2, caption="Evidencia 2", width=300)

  st.markdown(
      "#### 3. Cumplimiento de actividades de Planner (Peso: 33.33% - $100)"
  )
  uploaded_file = st.file_uploader(
      "Sube el reporte mensual de Excel (Hoja: 'Datos consolidados'):",
      type=["xlsx", "xls"],
      key="planner_file_felipe",
  )

  pago_ind3 = 0.0
  df_detalles_planner = pd.DataFrame()

  if uploaded_file is not None:
    try:
      xl = pd.ExcelFile(uploaded_file, engine="openpyxl")
      sheet_to_use = (
          "Datos consolidados"
          if "Datos consolidados" in xl.sheet_names
          else xl.sheet_names[0]
      )
      df_planner = pd.read_excel(
          uploaded_file, sheet_name=sheet_to_use, engine="openpyxl"
      )
      st.success(f"¡Archivo cargado con éxito (Hoja: '{sheet_to_use}')!")

      cols_lower = {str(c).strip().lower(): c for c in df_planner.columns}
      col_asignado = next(
          (v for k, v in cols_lower.items() if "asignado" in k or "assigned" in k),
          None,
      )
      col_tarea = next(
          (
              v
              for k, v in cols_lower.items()
              if "nombre de la tarea" in k or "nombre tarea" in k or k == "tarea"
          ),
          None,
      )
      if not col_tarea:
        col_tarea = next(
            (v for k, v in cols_lower.items() if "tarea" in k or "task" in k),
            None,
        )
      col_vencimiento = next(
          (
              v
              for k, v in cols_lower.items()
              if "vencimiento" in k or "due" in k
          ),
          None,
      )
      col_finalizacion = next(
          (
              v
              for k, v in cols_lower.items()
              if "finalizaci" in k or "completion" in k or "fin" in k
          ),
          None,
      )

      if col_asignado:
        df_filtrado = df_planner[
            df_planner[col_asignado]
            .astype(str)
            .str.contains(
                "Felipe Gavilanes;Dennis Navarrete", case=False, na=False
            )
        ].copy()

        if not df_filtrado.empty:
          lista_resultados = []
          for _, row in df_filtrado.iterrows():
            nombre_t = (
                str(row[col_tarea])
                if col_tarea and pd.notna(row[col_tarea])
                else "Sin nombre"
            )
            f_venc = (
                row[col_vencimiento] if col_vencimiento else "No especificada"
            )
            f_fin = (
                row[col_finalizacion] if col_finalizacion else "No especificada"
            )

            cumplio = "No"
            try:
              if pd.to_datetime(f_fin) <= pd.to_datetime(f_venc):
                cumplio = "Sí"
            except:
              cumplio = "No"

            lista_resultados.append(
                {
                    "Actividad": nombre_t,
                    "Fecha Vencimiento": str(f_venc),
                    "Fecha Finalización": str(f_fin),
                    "¿Cumplió?": cumplio,
                }
            )

          df_detalles_planner = pd.DataFrame(lista_resultados)
          st.dataframe(
              df_detalles_planner, hide_index=True, use_container_width=True
          )
          total_t = len(df_detalles_planner)
          completadas_tiempo = len(
              df_detalles_planner[df_detalles_planner["¿Cumplió?"] == "Sí"]
          )
          pago_ind3 = (
              (completadas_tiempo / total_t) * 100 if total_t > 0 else 0
          )
        else:
          st.warning(
              "No se encontraron tareas asignadas a 'Felipe"
              " Gavilanes;Dennis Navarrete'."
          )
    except Exception as e:
      st.error(f"Error al leer el archivo Excel: {e}")

  total_a_pagar_f = pago_ind1 + pago_ind2 + pago_ind3
  st.markdown("---")
  st.subheader("3. Resumen y Consolidado - Felipe")

  df_resumen_f = pd.DataFrame(
      {
          "Indicadores": [
              "Presupuesto e Indicador comerciales",
              "Comisiones de Ventas",
              "Cumplimiento de actividades de Planner",
          ],
          "Objetivo": ["100%", "100%", "100%"],
          "Peso": ["33.33%", "33.33%", "33.33%"],
          "Valor por Indicador": ["$100.00", "$100.00", "$100.00"],
          "Valor a Pagar ($)": [
              f"${pago_ind1:,.2f}",
              f"${pago_ind2:,.2f}",
              f"${pago_ind3:,.2f}",
          ],
      }
  )
  st.dataframe(df_resumen_f, hide_index=True, use_container_width=True)

  col1, col2 = st.columns(2)
  col1.metric("Variable Máxima Establecida", f"${variable_total_maxima_f:,.2f}")
  col2.metric("Total Variable a Pagar", f"${total_a_pagar_f:,.2f}")

  st.markdown("---")
  if st.button(f"Grabar Datos - {colaborador_seleccionado}"):
    st.session_state[f"grabado_{colaborador_seleccionado}"] = True
    st.session_state[f"data_{colaborador_seleccionado}"] = {
        "tipo": "felipe",
        "p1": pago_ind1,
        "p2": pago_ind2,
        "p3": pago_ind3,
        "total": total_a_pagar_f,
        "max": variable_total_maxima_f,
        "img1": foto_evidencia_1,
        "img2": foto_evidencia_2,
        "df_planner": df_detalles_planner,
    }
    st.success(f"¡Datos de {colaborador_seleccionado} grabados y acumulados!")


# --- CASO C: TATIANA PALACIOS (Asistente de Ventas) ---
elif colaborador_seleccionado == "Tatiana Palacios - Asistente de Ventas":
  variable_total_maxima_t = 100.0

  st.subheader(f"2. Evaluación de Metas: {colaborador_seleccionado}")
  st.write(
      "**Objetivo:** Cumplimiento puntual de la planificación mensual de"
      " entregables y reportes comerciales cargados en el Planner, respetando"
      " las fechas límite establecidas."
  )
  st.markdown(
      "#### Cumplimiento de actividades de Planner (Peso: 100% - $100.00)"
  )
  uploaded_file_t = st.file_uploader(
      "Sube el reporte mensual de Excel (Hoja: 'Datos consolidados'):",
      type=["xlsx", "xls"],
      key="planner_file_tatiana",
  )

  pago_tatiana = 0.0
  df_detalles_tatiana = pd.DataFrame()

  if uploaded_file_t is not None:
    try:
      xl = pd.ExcelFile(uploaded_file_t, engine="openpyxl")
      sheet_to_use = (
          "Datos consolidados"
          if "Datos consolidados" in xl.sheet_names
          else xl.sheet_names[0]
      )
      df_planner_t = pd.read_excel(
          uploaded_file_t, sheet_name=sheet_to_use, engine="openpyxl"
      )
      st.success(f"¡Archivo cargado con éxito (Hoja: '{sheet_to_use}')!")

      cols_lower = {str(c).strip().lower(): c for c in df_planner_t.columns}
      col_asignado = next(
          (v for k, v in cols_lower.items() if "asignado" in k or "assigned" in k),
          None,
      )
      col_tarea = next(
          (
              v
              for k, v in cols_lower.items()
              if "nombre de la tarea" in k or "nombre tarea" in k or k == "tarea"
          ),
          None,
      )
      if not col_tarea:
        col_tarea = next(
            (v for k, v in cols_lower.items() if "tarea" in k or "task" in k),
            None,
        )
      col_vencimiento = next(
          (
              v
              for k, v in cols_lower.items()
              if "vencimiento" in k or "due" in k
          ),
          None,
      )
      col_finalizacion = next(
          (
              v
              for k, v in cols_lower.items()
              if "finalizaci" in k or "completion" in k or "fin" in k
          ),
          None,
      )

      if col_asignado:
        df_filtrado_t = df_planner_t[
            df_planner_t[col_asignado]
            .astype(str)
            .str.contains("Tatiana Palacios", case=False, na=False)
        ].copy()

        if not df_filtrado_t.empty:
          lista_resultados_t = []
          for _, row in df_filtrado_t.iterrows():
            nombre_t = (
                str(row[col_tarea])
                if col_tarea and pd.notna(row[col_tarea])
                else "Sin nombre"
            )
            f_venc = (
                row[col_vencimiento] if col_vencimiento else "No especificada"
            )
            f_fin = (
                row[col_finalizacion] if col_finalizacion else "No especificada"
            )

            cumplio = "No"
            try:
              if pd.to_datetime(f_fin) <= pd.to_datetime(f_venc):
                cumplio = "Sí"
            except:
              cumplio = "No"

            lista_resultados_t.append(
                {
                    "Actividad": nombre_t,
                    "Fecha Vencimiento": str(f_venc),
                    "Fecha Finalización": str(f_fin),
                    "¿Cumplió?": cumplio,
                }
            )

          df_detalles_tatiana = pd.DataFrame(lista_resultados_t)
          st.markdown("##### Detalle de Actividades Filtradas (Tatiana):")
          st.dataframe(
              df_detalles_tatiana, hide_index=True, use_container_width=True
          )

          total_t = len(df_detalles_tatiana)
          completadas_tiempo = len(
              df_detalles_tatiana[df_detalles_tatiana["¿Cumplió?"] == "Sí"]
          )
          porcentaje_tatiana = (
              (completadas_tiempo / total_t) * 100 if total_t > 0 else 0
          )
          pago_tatiana = (porcentaje_tatiana / 100.0) * 100.0
        else:
          st.warning(
              "No se encontraron tareas asignadas a 'Tatiana Palacios' en este"
              " archivo."
          )
    except Exception as e:
      st.error(f"Error al leer el archivo Excel: {e}")

  st.markdown("---")
  st.subheader("3. Resumen y Consolidado - Tatiana Palacios")

  df_resumen_tatiana = pd.DataFrame(
      {
          "Indicadores": ["Cumplimiento de actividades de Planner"],
          "Objetivo": ["100%"],
          "Peso": ["100%"],
          "Valor por Indicador": ["$100.00"],
          "Valor a Pagar ($)": [f"${pago_tatiana:,.2f}"],
      }
  )
  st.dataframe(df_resumen_tatiana, hide_index=True, use_container_width=True)

  col1, col2 = st.columns(2)
  col1.metric("Variable Máxima Establecida", f"${variable_total_maxima_t:,.2f}")
  col2.metric("Total Variable a Pagar", f"${pago_tatiana:,.2f}")

  st.markdown("---")
  if st.button(f"Grabar Datos - {colaborador_seleccionado}"):
    st.session_state[f"grabado_{colaborador_seleccionado}"] = True
    st.session_state[f"data_{colaborador_seleccionado}"] = {
        "tipo": "tatiana",
        "total": pago_tatiana,
        "max": variable_total_maxima_t,
        "df_planner": df_detalles_tatiana,
    }
    st.success(f"¡Datos de {colaborador_seleccionado} grabados y acumulados!")


# --- CASO D: JEFES COMERCIALES (Eduardo, Mario, Ronald, Davis, Yilberth) ---
else:
  variable_total_maxima = totales_maximos_jefes[colaborador_seleccionado]
  session_df_key = f"df_jefe_{colaborador_seleccionado}"

  if session_df_key not in st.session_state:
    st.session_state[session_df_key] = pd.DataFrame(
        {
            "Indicador": [
                "Visitas",
                "Efectividad",
                "Línea por Pedido (LPP)",
                "Clientes nuevos",
                "Control de gastos",
            ],
            "Peso (%)": [15.0, 15.0, 15.0, 15.0, 40.0],
            "Objetivo Planificado": [150.0, 80.0, 50.0, 20.0, 1450.0],
            "Valor Real Ejecutado": [150.0, 85.0, 45.0, 18.0, 1400.0],
        }
    )

  st.subheader(f"2. Evaluación de Metas: {colaborador_seleccionado}")
  st.write(
      f"Variable Máxima Asignada: **${variable_total_maxima:,.2f}**. Modifica"
      " únicamente el **Objetivo Planificado** y el **Valor Real Ejecutado**;"
      " los cálculos y el resumen se actualizan automáticamente en esta misma"
      " tabla (Tope máximo de cumplimiento: 100%):"
  )


  def calcular_fila_jefe(row):
    obj = row["Objetivo Planificado"]
    real = row["Valor Real Ejecutado"]
    peso = row["Peso (%)"]
    ind_name = row["Indicador"]
    dolares_asig = (peso / 100.0) * variable_total_maxima

    if ind_name == "Control de gastos":
      # Control de gastos: Si real > objetivo => 0% y $0, si real <= objetivo => 100% y pago total
      if real > obj:
        cumplimiento = 0.0
        pago = 0.0
      else:
        cumplimiento = 100.0
        pago = dolares_asig
    else:
      cumplimiento_calc = (real / obj) * 100 if obj > 0 else 0
      # TOPE MÁXIMO 100% (Sin sobrecumplimiento)
      cumplimiento = min(cumplimiento_calc, 100.0)
      pago = 0.0 if cumplimiento < 90.0 else dolares_asig * (cumplimiento / 100.0)

    return pd.Series(
        [round(cumplimiento, 1), round(pago, 2)],
        index=["% Cumplimiento", "Valor a Pagar ($)"],
    )


  df_trabajo = st.session_state[session_df_key].copy()
  df_trabajo[["% Cumplimiento", "Valor a Pagar ($)"]] = df_trabajo.apply(
      calcular_fila_jefe, axis=1
  )

  # UNA SOLA TABLA LIMPIA (Edición y Resultados juntos)
  df_editado_jefe = st.data_editor(
      df_trabajo[[
          "Indicador",
          "Peso (%)",
          "Objetivo Planificado",
          "Valor Real Ejecutado",
          "% Cumplimiento",
          "Valor a Pagar ($)",
      ]],
      column_config={
          "Indicador": st.column_config.TextColumn("Indicador", disabled=True),
          "Peso (%)": st.column_config.NumberColumn(
              "Peso (%)", disabled=True, format="%.1f%%"
          ),
          "Objetivo Planificado": st.column_config.NumberColumn(
              "Objetivo Planificado (Editable)", format="%.2f"
          ),
          "Valor Real Ejecutado": st.column_config.NumberColumn(
              "Valor Real Ejecutado (Editable)", format="%.2f"
          ),
          "% Cumplimiento": st.column_config.NumberColumn(
              "% Cumplimiento (Tope 100%)", disabled=True, format="%.1f%%"
          ),
          "Valor a Pagar ($)": st.column_config.NumberColumn(
              "Valor a Pagar ($) (Calculado)", disabled=True, format="$%.2f"
          ),
      },
      hide_index=True,
      use_container_width=True,
      key=f"editor_unica_{colaborador_seleccionado}",
  )

  # Actualizar estado con la edición y recálculo automático
  st.session_state[session_df_key]["Objetivo Planificado"] = df_editado_jefe[
      "Objetivo Planificado"
  ]
  st.session_state[session_df_key]["Valor Real Ejecutado"] = df_editado_jefe[
      "Valor Real Ejecutado"
  ]
  st.session_state[session_df_key][["% Cumplimiento", "Valor a Pagar ($)"]] = (
      st.session_state[session_df_key].apply(calcular_fila_jefe, axis=1)
  )

  total_a_pagar_jefe = st.session_state[session_df_key][
      "Valor a Pagar ($)"
  ].sum()

  st.markdown("---")
  col1, col2 = st.columns(2)
  col1.metric("Variable Máxima Establecida", f"${variable_total_maxima:,.2f}")
  col2.metric("Total Variable a Pagar", f"${total_a_pagar_jefe:,.2f}")

  st.markdown("---")
  if st.button(f"Grabar Datos - {colaborador_seleccionado}"):
    st.session_state[f"grabado_{colaborador_seleccionado}"] = True
    st.session_state[f"data_{colaborador_seleccionado}"] = {
        "tipo": "jefe",
        "df": st.session_state[session_df_key].copy(),
        "total": total_a_pagar_jefe,
        "max": variable_total_maxima,
    }
    st.success(f"¡Datos de {colaborador_seleccionado} grabados y acumulados!")


# ==========================================
# GENERADOR DE PDF CONSOLIDADO GENERAL
# ==========================================
def generar_pdf_consolidado(todos_datos, fechas):
  buffer = io.BytesIO()
  c = canvas.Canvas(buffer, pagesize=letter)
  width, height = letter
  periodo_str = (
      f"Periodo: {fechas[0].strftime('%d/%m/%Y')} al"
      f" {fechas[1].strftime('%d/%m/%Y')}"
      if isinstance(fechas, tuple)
      else f"Periodo: {fechas}"
  )

  c.setFillColorRGB(0.86, 0.08, 0.24)
  c.rect(0, height - 50, width, 50, fill=1, stroke=0)
  c.setFillColorRGB(1, 1, 1)
  c.setFont("Helvetica-Bold", 14)
  c.drawString(40, height - 32, "REPORTE CONSOLIDADO - CALCULO DE VARIABLES")

  c.setFillColorRGB(0.2, 0.2, 0.2)
  c.setFont("Helvetica-Bold", 10)
  c.drawString(40, height - 70, periodo_str)
  y = height - 95

  for colab in colaboradores_nombres:
    if st.session_state[f"grabado_{colab}"] and todos_datos.get(colab):
      data = todos_datos[colab]

      if y < 200:
        c.showPage()
        y = height - 50

      c.setFillColorRGB(0.86, 0.08, 0.24)
      c.setFont("Helvetica-Bold", 11)
      c.drawString(40, y, f"Colaborador: {colab}")
      y -= 18

      if data["tipo"] == "david":
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, "Variable")
        c.drawString(180, y, "Objetivo")
        c.drawString(260, y, "Real")
        c.drawString(340, y, "% Cumplimiento")
        c.drawString(450, y, "Valor a Pagar")
        c.line(40, y - 3, 570, y - 3)
        y -= 18

        c.setFont("Helvetica", 9)
        for _, row in data["df"].iterrows():
          if y < 50:
            c.showPage()
            y = height - 50
          c.drawString(40, y, str(row["Variable"]))
          c.drawString(180, y, f"{row['Objetivo Planificado']:,.2f}")
          c.drawString(260, y, f"{row['Valor Real Ejecutado']:,.2f}")
          c.drawString(340, y, f"{row['% Cumplimiento']:.1f}%")
          c.drawString(450, y, f"${row['Valor a Pagar ($)']:,.2f}")
          y -= 16

        y -= 4
        c.line(40, y, 570, y)
        y -= 16
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, f"Variable Máxima: ${data['max']:,.2f}")
        c.drawString(340, y, f"Total a Pagar: ${data['total']:,.2f}")
        y -= 30

      elif data["tipo"] == "felipe":
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, "Indicadores")
        c.drawString(280, y, "Objetivo")
        c.drawString(360, y, "Peso")
        c.drawString(450, y, "Valor a Pagar")
        c.line(40, y - 3, 570, y - 3)
        y -= 18

        c.setFont("Helvetica", 9)
        inds = [
            ("Presupuesto e Indicador comerciales", data["p1"]),
            ("Comisiones de Ventas", data["p2"]),
            ("Cumplimiento de actividades de Planner", data["p3"]),
        ]
        for ind_name, val_pago in inds:
          if y < 50:
            c.showPage()
            y = height - 50
          c.drawString(40, y, ind_name[:40])
          c.drawString(280, y, "100%")
          c.drawString(360, y, "33.33%")
          c.drawString(450, y, f"${val_pago:,.2f}")
          y -= 16

        y -= 4
        c.line(40, y, 570, y)
        y -= 16
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, f"Variable Máxima: ${data['max']:,.2f}")
        c.drawString(340, y, f"Total a Pagar: ${data['total']:,.2f}")
        y -= 30

      elif data["tipo"] == "tatiana":
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, "Indicadores")
        c.drawString(280, y, "Objetivo")
        c.drawString(360, y, "Peso")
        c.drawString(450, y, "Valor a Pagar")
        c.line(40, y - 3, 570, y - 3)
        y -= 18

        c.setFont("Helvetica", 9)
        if y < 50:
          c.showPage()
          y = height - 50
        c.drawString(40, y, "Cumplimiento de actividades de Planner")
        c.drawString(280, y, "100%")
        c.drawString(360, y, "100%")
        c.drawString(450, y, f"${data['total']:,.2f}")
        y -= 16

        y -= 4
        c.line(40, y, 570, y)
        y -= 16
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, f"Variable Máxima: ${data['max']:,.2f}")
        c.drawString(340, y, f"Total a Pagar: ${data['total']:,.2f}")
        y -= 30

      elif data["tipo"] == "jefe":
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, "Indicador")
        c.drawString(180, y, "Objetivo")
        c.drawString(250, y, "Real")
        c.drawString(320, y, "% Cumplimiento")
        c.drawString(440, y, "Valor a Pagar")
        c.line(40, y - 3, 570, y - 3)
        y -= 18

        c.setFont("Helvetica", 9)
        for _, row in data["df"].iterrows():
          if y < 50:
            c.showPage()
            y = height - 50
          c.drawString(40, y, str(row["Indicador"]))
          c.drawString(180, y, f"{row['Objetivo Planificado']:,.2f}")
          c.drawString(250, y, f"{row['Valor Real Ejecutado']:,.2f}")
          c.drawString(320, y, f"{row['% Cumplimiento']:.1f}%")
          c.drawString(440, y, f"${row['Valor a Pagar ($)']:,.2f}")
          y -= 16

        y -= 4
        c.line(40, y, 570, y)
        y -= 16
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, f"Variable Máxima: ${data['max']:,.2f}")
        c.drawString(320, y, f"Total a Pagar: ${data['total']:,.2f}")
        y -= 30

  c.save()
  buffer.seek(0)
  return buffer


# ==========================================
# PANEL DE DESCARGA CONSOLIDADA
# ==========================================
st.markdown("---")
st.subheader("📥 Panel de Descarga del Reporte Consolidado General")
st.write(
    "Haz clic en el botón para descargar **un solo PDF consolidado** que incluye"
    " a todos los colaboradores y jefes que hayas grabado:"
)

datos_todos = {
    colab: st.session_state[f"data_{colab}"]
    for colab in colaboradores_nombres
    if st.session_state[f"grabado_{colab}"]
}

if datos_todos:
  pdf_cons = generar_pdf_consolidado(datos_todos, periodo_evaluacion)

  st.download_button(
      label=(
          "📄 Descargar Reporte PDF Consolidado General (David, Felipe,"
          " Tatiana y Jefes)"
      ),
      data=pdf_cons,
      file_name="Reporte_Consolidado_General.pdf",
      mime="application/pdf",
      key="btn_dl_general",
  )
else:
  st.info(
      "Aún no has grabado los datos de ningún colaborador. Graba al menos a"
      " uno para habilitar el reporte consolidado."
  )