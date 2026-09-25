"""Marco legal, documental y comercial de la herramienta."""

LEGAL = {
    "title": "Legislaciones, documentación, autorizaciones y validez comercial",
    "eyebrow": "MARCO DE USO · SNOCOMM ENERGY CONTROL",
    "lead": (
        "Snocomm nace como trabajo de titulación de Electricidad en el CFT Paillaco. "
        "Esta página describe, con la seriedad que corresponde, de dónde sale el software, "
        "qué documentos lo acompañan y bajo qué condiciones puede ofrecerse más adelante "
        "fuera del aula."
    ),
    "short_notice": (
        "Herramienta de prediseño e ingeniería informada. El marco legal y comercial "
        "completo está en la pestaña Legislación."
    ),
    "sections": [
        {
            "heading": "Origen académico",
            "body": [
                "Autor: Andres Barbudo Rodriguez. Institución formadora: CFT Paillaco, carrera de Electricidad, Trabajo Práctico Aplicado (TNS).",
                "El repositorio snocomm-edge-controller articula tres piezas de laboratorio: Monitor AHF, prediseño TAN alineado a IEC 61439-1 e IEC 61439-2, y banco HIL 24 V con instrumentos de pañol (wanptek KPS305D y Gratten GA1102CAL).",
                "Mientras el título y las autorizaciones profesionales están en curso, el software se presenta como expediente de titulación y como prototipo de producto. Eso no le quita rigor: le pone fecha y firma.",
            ],
        },
        {
            "heading": "Qué es esta herramienta — y qué documentos la rodean",
            "body": [
                "La calculadora compara campañas CSV de osciloscopio con valores de prediseño y con 24 plantillas habituales en tableros de telecomunicaciones. El módulo TAN propone envolvente, forma de separación, verificaciones de diseño y BOM tipificado.",
                "IEC 61439-1 (reglas generales) e IEC 61439-2 (conjuntos de potencia) son el material técnico de referencia: corriente asignada, IP, calentamiento, resistencia a cortocircuito, integración de aparatos y expediente del conjunto. Usarlas es una ventaja concreta: el tablero se describe como sistema, no como suma de catálogos.",
                "Los informes que emite Snocomm son documentos de ingeniería de prediseño. Conviven, cuando el proyecto lo exige, con la memoria de cálculo, el unifilar, la declaración del ensamblador, los ensayos de tipo del sistema de envolvente y las verificaciones de rutina. Cada uno tiene su lugar; ninguno se disfraza de otro.",
            ],
        },
        {
            "heading": "Autorizaciones y ejercicio profesional en Chile",
            "body": [
                "El ejercicio remunerado de la electricidad en instalaciones de uso público o particular se enmarca en la Superintendencia de Electricidad y Combustibles (SEC), el reglamento de instalaciones y las categorías de instalador que correspondan al tipo de trabajo.",
                "El autor cursa el TNS de Electricidad y, al egresar, gestionará diploma, cédula y las autorizaciones SEC que habiliten el ofrecimiento comercial del servicio y, cuando proceda, del software como herramienta de apoyo a ese servicio.",
                "Hasta completar esos trámites, Snocomm se ofrece en el marco formativo del CFT (defensa, laboratorio, demostración a guía y comisión). El código queda listo para el salto: la autorización es un acto administrativo, no un parche de última hora en el repositorio.",
            ],
        },
        {
            "heading": "Validez comercial prevista",
            "body": [
                "La hoja de ruta comercial es deliberada: titularse, reunir la documentación profesional, y entonces ofrecer Snocomm como plataforma de prediseño y de comparación de campañas para tableros TAN / telecomunicaciones.",
                "Un cliente futuro compra un criterio de ingeniería reproducible —CSV, plantilla, informe PDF con gráficos, prediseño TAN— no un sello de conjunto. Los sellos, cuando existan, los emite quien corresponda (fabricante del sistema de envolvente, organismo de ensayo, instalador autorizado).",
                "Licencia del repositorio: MIT (archivo LICENSE). Eso facilita la transición de prototipo académico a producto, con marca Snocomm Energy Control, sin reescribir el núcleo el día que el diploma esté en la pared.",
            ],
        },
        {
            "heading": "Alcance técnico que el usuario debe tener presente",
            "body": [
                "Las mediciones de esta calculadora provienen de CSV de osciloscopio (típicamente Gratten GA1102CAL, 2 canales). Un dump de 24 VDC documenta el bus del rack; no sustituye un analizador de red ni un ensayo de tipo.",
                "El THDi del Monitor AHF es un indicador académico (H3+H5+H7 sobre I1). El prediseño TAN usa 400 V como tensión de cálculo del tablero y 24 V como banco de laboratorio. Ambos números pueden convivir en el mismo expediente si se etiquetan con honestidad.",
                "Quien firme un tablero, una memoria RIC o una declaración ante la SEC lo hace con su autorización y su criterio. Snocomm está hecho para que esa firma tenga mejores números encima de la mesa.",
            ],
        },
        {
            "heading": "Contacto del expediente",
            "body": [
                "Proyecto: Snocomm Energy Control — AHF Edge Controller + TAN-Telecom.",
                "Autor: Andres Barbudo Rodriguez · CFT Paillaco · Electricidad.",
                "Año del TPA: 2026. Rama de esta función: calculadora comparativa de campañas y 24 plantillas de prediseño.",
            ],
        },
    ],
}
