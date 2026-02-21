from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

try:
    from streamlit_gsheets import GSheetsConnection
except Exception:
    GSheetsConnection = None

try:
    from st_copy_to_clipboard import st_copy_to_clipboard
except Exception:
    st_copy_to_clipboard = None


st.set_page_config(page_title="Formulario Nexus", page_icon="🧩", layout="centered")

WORKSHEET = os.getenv("GSHEETS_WORKSHEET", "responses")

BASE_FIELDS = [
    "sexo",
    "filtro_mixto",
    "edad",
    "horario",
    "lugar_estudio",
    "socializacion",
    "fines_semana",
    "actividades_extra",
    "ocio_interno",
    "ocio_interno_otro",
    "orden_limpieza",
    "ruido_tolerancia",
    "tabaco_vapeo",
    "visitas",
    "compartir_gastos",
    "temperatura",
]

ALL_COLUMNS = (
    ["match_id"]
    + [f"{field}_A" for field in BASE_FIELDS]
    + ["target_nota_A"]
    + [f"{field}_B" for field in BASE_FIELDS]
    + ["target_nota_B", "timestamp"]
)

CATEGORICAL_OPTIONS: dict[str, list[str]] = {
    "sexo": ["Masculino", "Femenino", "Otro"],
    "filtro_mixto": ["Sí", "No", "Me da exactamente igual"],
    "horario": ["Madrugador", "Nocturno"],
    "lugar_estudio": [
        "En mi habitación en silencio total",
        "En la sala de estudio de la residencia",
        "En bibliotecas públicas o facultad",
        "Con música o ruido ambiente",
    ],
    "fines_semana": [
        "Sí, casi siempre",
        "A veces",
        "No, suelo volver a mi casa familiar",
    ],
    "actividades_extra": [
        "Muy importante, no paro en casa",
        "Intermedio",
        "Soy muy casero, disfruto mi tiempo en la habitación",
    ],
    "ocio_interno": [
        "Torneos de E-sports",
        "Cenas temáticas",
        "Maratón de series-películas",
        "Tardes de juegos de mesa",
        "Otro",
    ],
    "tabaco_vapeo": [
        "No, y me molesta que lo hagan en la habitación",
        "No, pero me da igual si el otro lo hace",
        "Sí, fumo o vapeo",
    ],
    "visitas": [
        "Prefiero que sea un lugar privado solo para nosotros",
        "Está bien de vez en cuando, avisando antes",
        "Me encanta que haya gente, mi cuarto está siempre abierto",
    ],
    "compartir_gastos": [
        "Prefiero que cada uno tenga lo suyo estrictamente",
        "Me gusta comprar a medias y compartir",
        "No me importa invitar o que me cojan cosas si hay confianza",
    ],
    "temperatura": [
        "Muy friolero, prefiero ventana cerrada",
        "Neutro",
        "Muy caluroso, necesito ventilar y dormir fresco",
    ],
}


def inject_mobile_styles() -> None:
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
          h1 {
            font-size: 2rem !important;
            line-height: 1.25 !important;
          }
          h2 {
            font-size: 1.5rem !important;
          }
          h3 {
            font-size: 1.25rem !important;
          }
          p, li, label, div[data-testid="stMarkdownContainer"] p {
            font-size: 1.08rem !important;
            line-height: 1.55 !important;
          }
          div[role="radiogroup"] label p,
          div[data-testid="stSelectbox"] label p,
          div[data-testid="stSlider"] label p,
          div[data-testid="stTextInput"] label p {
            font-size: 1.08rem !important;
          }
          div[data-testid="stRadio"] label p,
          div[data-testid="stCheckbox"] label p {
            font-size: 1.05rem !important;
          }
          button p {
            font-size: 1.05rem !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_query_value(value: str | list[str] | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return str(value[0]).strip() if value else None
    text = str(value).strip()
    return text or None


def get_match_id_from_url() -> str | None:
    return normalize_query_value(st.query_params.get("match_id"))


def get_base_url() -> str:
    configured = str(st.secrets.get("app_base_url", os.getenv("APP_BASE_URL", ""))).strip()
    if configured:
        return configured.rstrip("/")

    # Streamlit Cloud/runtime URL fallback when app_base_url is not configured.
    try:
        runtime_url = str(getattr(st.context, "url", "")).strip()
    except Exception:
        runtime_url = ""
    return runtime_url.rstrip("/")


def build_share_link(match_id: str) -> str:
    base_url = get_base_url()
    if base_url:
        return f"{base_url}/?match_id={match_id}"
    return f"?match_id={match_id}"


def build_root_link() -> str:
    base_url = get_base_url()
    if base_url:
        return f"{base_url}/"
    return "/"


def get_connection():
    if GSheetsConnection is not None:
        return st.connection("gsheets", type=GSheetsConnection)
    return st.connection("gsheets")


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in ALL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[ALL_COLUMNS]


def read_sheet(conn) -> pd.DataFrame:
    try:
        df = conn.read(worksheet=WORKSHEET, ttl=0)
    except TypeError:
        df = conn.read(ttl=0)
    if df is None or df.empty:
        return pd.DataFrame(columns=ALL_COLUMNS)
    return ensure_columns(df.copy())


def write_sheet(conn, df: pd.DataFrame) -> None:
    clean_df = ensure_columns(df.copy())
    try:
        conn.update(worksheet=WORKSHEET, data=clean_df)
    except TypeError:
        conn.update(data=clean_df)


def format_gsheets_error(exc: Exception) -> str:
    raw = f"{type(exc).__name__}: {exc}"
    upper = raw.upper()

    if "SERVICE_DISABLED" in upper or "HAS NOT BEEN USED IN PROJECT" in upper:
        return (
            "Google Sheets API está deshabilitada en tu proyecto de Google Cloud. "
            "Actívala en https://console.cloud.google.com/apis/library/sheets.googleapis.com "
            "y espera 1-5 minutos."
        )
    if "PERMISSION_DENIED" in upper or "403" in upper:
        return (
            "Permiso denegado al abrir el spreadsheet. Verifica que la service account "
            "tiene acceso de Editor al Google Sheet."
        )
    if "WORKSHEETNOTFOUND" in upper:
        return (
            "No existe la pestaña configurada en `worksheet` dentro del Google Sheet. "
            "Crea la pestaña o corrige el nombre."
        )
    return raw


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_short_uuid() -> str:
    return uuid.uuid4().hex[:8]


def has_non_empty_value(value: object) -> bool:
    if value is None:
        return False
    if pd.isna(value):
        return False
    return str(value).strip() != ""


def is_match_completed(df: pd.DataFrame, match_id: str) -> bool:
    if df.empty:
        return False
    rows = df[df["match_id"].astype(str) == str(match_id)]
    if rows.empty:
        return False
    for _, row in rows.iterrows():
        if has_non_empty_value(row.get("target_nota_A")) and has_non_empty_value(row.get("target_nota_B")):
            return True
    return False


def encode_choice(field: str, selected_label: str) -> int:
    options = CATEGORICAL_OPTIONS[field]
    return options.index(selected_label) + 1


def collect_form_values() -> tuple[dict[str, object], int]:
    with st.form("nexus_form"):
        sexo_label = st.selectbox(
            "1) Sexo",
            CATEGORICAL_OPTIONS["sexo"],
            key="sexo",
        )
        filtro_mixto_label = st.radio(
            "2) ¿Estarías dispuesto/a a compartir habitación con alguien de distinto sexo?",
            CATEGORICAL_OPTIONS["filtro_mixto"],
            key="filtro_mixto",
        )
        edad = st.slider("3) Edad", min_value=17, max_value=35, value=22, key="edad")

        horario_label = st.radio(
            "4) Horario: Eres más...",
            CATEGORICAL_OPTIONS["horario"],
            key="horario",
        )
        lugar_estudio_label = st.selectbox(
            "5) ¿Dónde prefieres estudiar habitualmente?",
            CATEGORICAL_OPTIONS["lugar_estudio"],
            key="lugar_estudio",
        )
        socializacion = st.slider(
            "6) ¿Cómo de social te consideras?",
            min_value=1,
            max_value=10,
            value=5,
            key="socializacion",
        )
        fines_semana_label = st.radio(
            "7) ¿Sueles quedarte los fines de semana?",
            CATEGORICAL_OPTIONS["fines_semana"],
            key="fines_semana",
        )
        actividades_extra_label = st.radio(
            "8) ¿Cómo de importante es para ti hacer planes fuera de la residencia?",
            CATEGORICAL_OPTIONS["actividades_extra"],
            key="actividades_extra",
        )
        ocio_interno_label = st.selectbox(
            "9) ¿Qué tipo de actividades te gustaría hacer en la residencia?",
            CATEGORICAL_OPTIONS["ocio_interno"],
            key="ocio_interno",
        )
        ocio_interno_otro = ""
        if ocio_interno_label == "Otro":
            ocio_interno_otro = st.text_input(
                "9.b) Especifica otra actividad",
                max_chars=120,
                key="ocio_interno_otro",
            ).strip()

        orden_limpieza = st.slider(
            "10) ¿Qué tan importante es para ti el orden y la limpieza?",
            min_value=1,
            max_value=10,
            value=5,
            key="orden_limpieza",
        )
        ruido_tolerancia = st.slider(
            "11) ¿Cuál es tu nivel de tolerancia al ruido cuando intentas descansar?",
            min_value=1,
            max_value=10,
            value=5,
            key="ruido_tolerancia",
        )
        tabaco_vapeo_label = st.radio(
            "12) ¿Fumas o vapeas?",
            CATEGORICAL_OPTIONS["tabaco_vapeo"],
            key="tabaco_vapeo",
        )
        visitas_label = st.radio(
            "13) ¿Cómo te sientes respecto a traer amigos o a tu pareja a la habitación?",
            CATEGORICAL_OPTIONS["visitas"],
            key="visitas",
        )
        compartir_gastos_label = st.radio(
            "14) A la hora de comprar cosas básicas (papel higiénico, jabón...)...",
            CATEGORICAL_OPTIONS["compartir_gastos"],
            key="compartir_gastos",
        )
        temperatura_label = st.radio(
            "15) ¿Eres más bien friolero o caluroso?",
            CATEGORICAL_OPTIONS["temperatura"],
            key="temperatura",
        )
        target_nota = st.slider(
            '16) Del 0 al 10, ¿cómo evaluarías la convivencia general con tu compañero/a?',
            min_value=0,
            max_value=10,
            value=7,
            key="target_nota",
        )

        submitted = st.form_submit_button("Enviar")

    values = {
        "sexo": encode_choice("sexo", sexo_label),
        "filtro_mixto": encode_choice("filtro_mixto", filtro_mixto_label),
        "edad": int(edad),
        "horario": encode_choice("horario", horario_label),
        "lugar_estudio": encode_choice("lugar_estudio", lugar_estudio_label),
        "socializacion": int(socializacion),
        "fines_semana": encode_choice("fines_semana", fines_semana_label),
        "actividades_extra": encode_choice("actividades_extra", actividades_extra_label),
        "ocio_interno": encode_choice("ocio_interno", ocio_interno_label),
        "ocio_interno_otro": ocio_interno_otro,
        "orden_limpieza": int(orden_limpieza),
        "ruido_tolerancia": int(ruido_tolerancia),
        "tabaco_vapeo": encode_choice("tabaco_vapeo", tabaco_vapeo_label),
        "visitas": encode_choice("visitas", visitas_label),
        "compartir_gastos": encode_choice("compartir_gastos", compartir_gastos_label),
        "temperatura": encode_choice("temperatura", temperatura_label),
    }
    return values if submitted else {}, int(target_nota)


def append_person_a_row(df: pd.DataFrame, match_id: str, values: dict[str, object], target: int) -> pd.DataFrame:
    row = {col: None for col in ALL_COLUMNS}
    row["match_id"] = match_id
    for field in BASE_FIELDS:
        row[f"{field}_A"] = values.get(field)
    row["target_nota_A"] = int(target)
    row["timestamp"] = now_iso()
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)


def update_or_append_person_b_row(df: pd.DataFrame, match_id: str, values: dict[str, object], target: int) -> pd.DataFrame:
    selected_idx = None
    same_id = df.index[df["match_id"].astype(str) == str(match_id)].tolist()
    for idx in same_id:
        if pd.isna(df.loc[idx, "target_nota_B"]) or str(df.loc[idx, "target_nota_B"]).strip() == "":
            selected_idx = idx
            break
    if selected_idx is None and same_id:
        selected_idx = same_id[-1]

    if selected_idx is not None:
        for field in BASE_FIELDS:
            df.loc[selected_idx, f"{field}_B"] = values.get(field)
        df.loc[selected_idx, "target_nota_B"] = int(target)
        df.loc[selected_idx, "timestamp"] = now_iso()
        return df

    row = {col: None for col in ALL_COLUMNS}
    row["match_id"] = match_id
    for field in BASE_FIELDS:
        row[f"{field}_B"] = values.get(field)
    row["target_nota_B"] = int(target)
    row["timestamp"] = now_iso()
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)


def main() -> None:
    inject_mobile_styles()
    st.title("Formulario Nexus")
    with st.container(border=True):
        st.subheader("Consentimiento informado y privacidad")
        st.markdown(
            "- Este formulario es anónimo: no solicitamos nombre, email, teléfono ni otros datos personales identificables.\n"
            "- Las respuestas se almacenan para análisis y entrenamiento del modelo de recomendación de Nexus.\n"
            "- Los resultados se tratarán de forma agregada y no se compartirán respuestas individuales.\n"
            "- El identificador técnico `match_id` se usa únicamente para emparejar respuestas (Persona A / Persona B).\n"
            "- Al continuar, declaras que entiendes este tratamiento de datos y aceptas participar de forma voluntaria."
        )
        accepted_privacy = st.checkbox(
            "He leído y acepto el tratamiento anónimo de mis respuestas para fines de análisis y entrenamiento del modelo.",
            key="consentimiento_legal",
        )

    st.warning(
        "¿Viviste con más de una persona? No pasa nada. Elige solo a UN ex-compañero para hacer este test "
        "(puede ser con el que mejor te llevaste o con el que peor). Responde a las preguntas pensando única "
        "y exclusivamente en tu convivencia con esa persona."
    )
    if not accepted_privacy:
        st.info("Para continuar, debes aceptar el consentimiento informado y privacidad.")
        return

    match_id = get_match_id_from_url()
    is_person_b = match_id is not None

    conn = None
    df = None

    if is_person_b:
        st.info(f"Flujo Invitado (Persona B). match_id detectado: `{match_id}`")
        try:
            conn = get_connection()
            df = read_sheet(conn)
        except Exception as exc:
            st.error(f"No se pudo abrir Google Sheets: {format_gsheets_error(exc)}")
            st.stop()

        if is_match_completed(df, match_id):
            st.success("Este enlace ya fue respondido por ambas personas y el test quedó completado.")
            st.write("Si quieres hacerlo de nuevo, inicia un nuevo test aquí:")
            st.link_button("Ir al inicio (/)", build_root_link())
            st.stop()

    values, target = collect_form_values()
    if not values:
        return

    if conn is None or df is None:
        try:
            conn = get_connection()
            df = read_sheet(conn)
        except Exception as exc:
            st.error(f"No se pudo abrir Google Sheets: {format_gsheets_error(exc)}")
            st.stop()

    try:
        if is_person_b:
            updated = update_or_append_person_b_row(df, match_id, values, target)
            write_sheet(conn, updated)
            st.success("Gracias. Tu formulario (Persona B) fue enviado correctamente.")
        else:
            new_match_id = generate_short_uuid()
            updated = append_person_a_row(df, new_match_id, values, target)
            write_sheet(conn, updated)

            link = build_share_link(new_match_id)
            st.success("Formulario enviado correctamente.")
            st.write("Comparte este enlace con tu ex-compañero/a:")
            st.code(link, language="text")

            if st_copy_to_clipboard is not None:
                st_copy_to_clipboard(link, "Copiar enlace")
            else:
                st.caption(
                    "Instala `st-copy-to-clipboard` para mostrar un botón de copiado integrado."
                )
    except Exception as exc:
        st.error(f"No se pudo guardar la respuesta en Google Sheets: {exc}")


if __name__ == "__main__":
    main()
