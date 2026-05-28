import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# =========================================
# CONFIGURACIÓN DE PÁGINA
# =========================================

st.set_page_config(
    page_title="SensorHub MQTT",
    page_icon="📡",
    layout="centered"
)

# =========================================
# ESTILOS VISUALES
# =========================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #dbeafe, #bfdbfe, #93c5fd);
    background-attachment: fixed;
}

h1, h2, h3 {
    color: #0f172a;
    text-align: center;
}

p, label, div {
    color: #1e293b;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(12px);
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 14px;
    border: none;
    padding: 0.7rem 1rem;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #3b82f6;
    color: white;
}

.stTextInput input {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# SESSION STATE
# =========================================

if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

# =========================================
# FUNCIÓN MQTT
# =========================================

def get_mqtt_message(
    broker,
    port,
    topic,
    client_id
):

    message_received = {
        "received": False,
        "payload": None
    }

    def on_message(
        client,
        userdata,
        message
    ):

        try:

            payload = json.loads(
                message.payload.decode()
            )

            message_received["payload"] = payload

            message_received["received"] = True

        except:

            message_received["payload"] = (
                message.payload.decode()
            )

            message_received["received"] = True

    try:

        client = mqtt.Client(
            client_id=client_id
        )

        client.on_message = on_message

        client.connect(
            broker,
            port,
            60
        )

        client.subscribe(topic)

        client.loop_start()

        timeout = time.time() + 5

        while (
            not message_received["received"]
            and time.time() < timeout
        ):

            time.sleep(0.1)

        client.loop_stop()

        client.disconnect()

        return message_received["payload"]

    except Exception as e:

        return {
            "error": str(e)
        }

# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.title("⚙️ Configuración MQTT")

    broker = st.text_input(
        '🌐 Broker MQTT',
        value='broker.mqttdashboard.com'
    )

    port = st.number_input(
        '🔌 Puerto',
        value=1883,
        min_value=1,
        max_value=65535
    )

    topic = st.text_input(
        '📡 Tópico',
        value='Sensor/THP2'
    )

    client_id = st.text_input(
        '🆔 ID del Cliente',
        value='streamlit_client'
    )

    st.markdown("---")

    st.info("""
📌 Configura el broker MQTT y recibe datos de sensores IoT en tiempo real.
""")

# =========================================
# HEADER
# =========================================

st.title("📡 SensorHub MQTT")

st.markdown("""
### Monitor inteligente para recepción de datos IoT en tiempo real
""")

st.markdown("---")

# =========================================
# INFORMACIÓN
# =========================================

with st.expander(
    'ℹ️ Información de uso',
    expanded=False
):

    st.markdown("""
### Cómo usar esta aplicación

1. Configura el broker MQTT en el sidebar
2. Selecciona el tópico MQTT
3. Presiona el botón de conexión
4. Observa los datos recibidos en tiempo real

### Brokers públicos recomendados

- broker.mqttdashboard.com
- test.mosquitto.org
- broker.hivemq.com
""")

# =========================================
# BOTÓN MQTT
# =========================================

if st.button(
    '📥 Obtener Datos del Sensor',
    use_container_width=True
):

    with st.spinner(
        '📡 Conectando al broker MQTT...'
    ):

        sensor_data = get_mqtt_message(
            broker,
            int(port),
            topic,
            client_id
        )

        st.session_state.sensor_data = sensor_data

# =========================================
# RESULTADOS
# =========================================

if st.session_state.sensor_data:

    st.markdown("---")

    st.subheader("📊 Datos Recibidos")

    data = st.session_state.sensor_data

    # ERROR
    if isinstance(data, dict) and 'error' in data:

        st.error(
            f"❌ Error de conexión: {data['error']}"
        )

    else:

        st.success(
            '✅ Datos recibidos correctamente'
        )

        # SI ES JSON
        if isinstance(data, dict):

            cols = st.columns(len(data))

            for i, (key, value) in enumerate(data.items()):

                with cols[i]:

                    st.metric(
                        label=key,
                        value=value
                    )

            with st.expander(
                '🧾 Ver JSON completo'
            ):

                st.json(data)

        # SI ES TEXTO
        else:

            st.code(data)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.markdown(
    """
    <center>
    🧠 Desarrollado con MQTT + Streamlit + IoT
    </center>
    """,
    unsafe_allow_html=True
)
