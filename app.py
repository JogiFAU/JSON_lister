import json
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="JSON Lister IDE",
    page_icon="🧭",
    layout="wide",
)


def _safe_preview(value: Any) -> str:
    """Short single-line preview for tree/list items."""
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 120 else text[:117] + "..."



def _to_record(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return item
    return {"value": item}


def _render_json_like_panel(record: dict[str, Any]) -> None:
    """IDE-like left panel showing field names and values."""
    st.markdown("#### Strukturansicht (IDE-Stil)")

    lines = ["{"]
    for idx, (key, value) in enumerate(record.items()):
        comma = "," if idx < len(record) - 1 else ""
        lines.append(f'  "{key}": {_safe_preview(value)}{comma}')
    lines.append("}")

    st.code("\n".join(lines), language="json")


def _init_state() -> None:
    if "records" not in st.session_state:
        st.session_state.records = []
    if "filename" not in st.session_state:
        st.session_state.filename = ""
    if "example_count" not in st.session_state:
        st.session_state.example_count = 1
    if "selected_index" not in st.session_state:
        st.session_state.selected_index = 0
    if "whitelist" not in st.session_state:
        st.session_state.whitelist = set()
    if "blacklist" not in st.session_state:
        st.session_state.blacklist = set()


def _clear_lists() -> None:
    st.session_state.whitelist = set()
    st.session_state.blacklist = set()


def _handle_file_upload() -> None:
    uploaded = st.file_uploader("JSON-Datei laden", type=["json"])
    if uploaded is None:
        return

    try:
        data = json.load(uploaded)
    except Exception as err:
        st.error(f"Datei konnte nicht gelesen werden: {err}")
        return

    if isinstance(data, list):
        raw_records = data
    else:
        raw_records = [data]

    if not raw_records:
        st.warning("Die JSON-Datei enthält keine Elemente.")
        return

    st.session_state.records = [_to_record(item) for item in raw_records]
    st.session_state.filename = uploaded.name
    st.session_state.example_count = min(st.session_state.example_count, len(st.session_state.records))
    st.session_state.selected_index = 0


def _move_key_to_whitelist(key: str) -> None:
    st.session_state.whitelist.add(key)
    st.session_state.blacklist.discard(key)


def _move_key_to_blacklist(key: str) -> None:
    st.session_state.blacklist.add(key)
    st.session_state.whitelist.discard(key)


def _download_list(label: str, values: set[str]) -> None:
    sorted_values = sorted(values)
    st.download_button(
        label=f"{label} exportieren",
        data=json.dumps(sorted_values, ensure_ascii=False, indent=2),
        file_name=f"{label.lower()}.json",
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    _init_state()

    st.title("🧭 JSON Lister – Whitelist/Blacklist Builder")
    st.caption("JSON-Datensätze inspizieren wie in einer IDE und relevante Variablennamen sammeln.")

    with st.sidebar:
        st.subheader("Datenquelle")
        _handle_file_upload()

        if st.session_state.records:
            max_examples = len(st.session_state.records)
            count = st.number_input(
                "Anzahl Beispiele",
                min_value=1,
                max_value=max_examples,
                value=st.session_state.example_count,
                step=1,
            )
            st.session_state.example_count = int(count)

            if st.button("Listen zurücksetzen", use_container_width=True):
                _clear_lists()

            st.info(
                f"Datei: {st.session_state.filename}\n"
                f"Elemente gesamt: {len(st.session_state.records)}\n"
                f"Betrachtete Beispiele: {st.session_state.example_count}"
            )
        else:
            st.info("Bitte zuerst eine JSON-Datei laden.")

    if not st.session_state.records:
        st.markdown(
            ""
            "### Willkommen\n"
            "1. Lade links eine JSON-Datei hoch.\n"
            "2. Wähle die Anzahl der Beispielelemente.\n"
            "3. Wähle Variablen und verschiebe sie in Whitelist/Blacklist."
        )
        return

    visible_records = st.session_state.records[: st.session_state.example_count]

    top_cols = st.columns([2, 1])
    with top_cols[0]:
        st.subheader("Element-Auswahl")
        options = [f"#{i + 1}" for i in range(len(visible_records))]
        selected_label = st.radio(
            "Beispiel-Element",
            options=options,
            index=min(st.session_state.selected_index, len(visible_records) - 1),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.selected_index = options.index(selected_label)

    record = visible_records[st.session_state.selected_index]

    left, middle, right = st.columns([1.5, 1, 1])

    with left:
        _render_json_like_panel(record)

    with middle:
        st.markdown("#### Variablen")
        keys = list(record.keys())
        selected_keys = st.multiselect(
            "Variablennamen auswählen",
            options=keys,
            help="Wähle Felder aus dem aktuellen Element.",
        )

        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("→ Whitelist", use_container_width=True):
                for key in selected_keys:
                    _move_key_to_whitelist(key)
        with btn_cols[1]:
            if st.button("→ Blacklist", use_container_width=True):
                for key in selected_keys:
                    _move_key_to_blacklist(key)

        st.markdown("#### Felddetails")
        selected_key = st.selectbox("Details für Feld", options=keys)
        st.code(json.dumps(record[selected_key], ensure_ascii=False, indent=2), language="json")

    with right:
        st.markdown("#### Whitelist")
        st.dataframe({"Variablen": sorted(st.session_state.whitelist)}, use_container_width=True, height=180)
        remove_wl = st.multiselect("Aus Whitelist entfernen", options=sorted(st.session_state.whitelist), key="rm_wl")
        if st.button("Whitelist-Einträge entfernen", use_container_width=True):
            for key in remove_wl:
                st.session_state.whitelist.discard(key)

        _download_list("Whitelist", st.session_state.whitelist)

        st.markdown("---")
        st.markdown("#### Blacklist")
        st.dataframe({"Variablen": sorted(st.session_state.blacklist)}, use_container_width=True, height=180)
        remove_bl = st.multiselect("Aus Blacklist entfernen", options=sorted(st.session_state.blacklist), key="rm_bl")
        if st.button("Blacklist-Einträge entfernen", use_container_width=True):
            for key in remove_bl:
                st.session_state.blacklist.discard(key)

        _download_list("Blacklist", st.session_state.blacklist)


if __name__ == "__main__":
    main()
