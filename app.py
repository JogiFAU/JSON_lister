import html
import json
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="JSON Lister IDE",
    page_icon="🧭",
    layout="wide",
)


IGNORED_METADATA_KEYS = {"metadata", "meta", "_meta", "header", "headers"}


def _init_state() -> None:
    defaults = {
        "raw_json": None,
        "filename": "",
        "scope_data": None,
        "scope_label": "",
        "all_variable_paths": [],
        "whitelist": set(),
        "blacklist": set(),
        "interaction_mode": "Whitelist",
        "hide_blacklisted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _clear_lists() -> None:
    st.session_state.whitelist = set()
    st.session_state.blacklist = set()


def _load_json() -> None:
    uploaded = st.file_uploader("JSON-Datei laden", type=["json"])
    if not uploaded:
        return

    try:
        st.session_state.raw_json = json.load(uploaded)
        st.session_state.filename = uploaded.name
    except Exception as err:
        st.error(f"Datei konnte nicht gelesen werden: {err}")
        return


def _is_metadata_key(key: str) -> bool:
    return key.lower() in IGNORED_METADATA_KEYS


def _find_candidate_scopes(data: Any) -> dict[str, Any]:
    """Find meaningful main-body scopes and exclude common metadata containers."""
    scopes: dict[str, Any] = {"Gesamtes JSON": data}

    if isinstance(data, dict):
        for key, value in data.items():
            if _is_metadata_key(key):
                continue
            if isinstance(value, (dict, list)):
                scopes[f"Top-Level: {key}"] = value

            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    if _is_metadata_key(nested_key):
                        continue
                    if isinstance(nested_value, (dict, list)):
                        scopes[f"{key}.{nested_key}"] = nested_value

    return scopes


def _extract_variable_paths(data: Any, base: str = "") -> set[str]:
    paths: set[str] = set()
    if isinstance(data, dict):
        for key, value in data.items():
            if _is_metadata_key(key):
                continue
            current = f"{base}.{key}" if base else key
            paths.add(current)
            paths.update(_extract_variable_paths(value, current))
    elif isinstance(data, list):
        for item in data:
            paths.update(_extract_variable_paths(item, base))
    return paths


def _format_scalar(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False)
    if len(text) > 100:
        return text[:97] + "..."
    return text


def _render_editor_line(indent: int, content: str, color: str = "#d4d4d4") -> None:
    st.markdown(
        f"<div style='padding-left:{indent * 18}px; color:{color}; font-family: monospace; white-space: pre;'>{content}</div>",
        unsafe_allow_html=True,
    )


def _add_to_mode(path: str) -> None:
    if st.session_state.interaction_mode == "Whitelist":
        st.session_state.whitelist.add(path)
        st.session_state.blacklist.discard(path)
    else:
        st.session_state.blacklist.add(path)
        st.session_state.whitelist.discard(path)


def _is_hidden(path: str) -> bool:
    if not st.session_state.hide_blacklisted:
        return False
    # hide exact field and its children if blacklisted
    for bl in st.session_state.blacklist:
        if path == bl or path.startswith(bl + "."):
            return True
    return False


def _render_json_interactive(data: Any, base: str = "", indent: int = 0) -> None:
    if isinstance(data, dict):
        _render_editor_line(indent, "{")
        for key, value in data.items():
            if _is_metadata_key(key):
                continue
            path = f"{base}.{key}" if base else key
            if _is_hidden(path):
                continue

            cols = st.columns([0.45, 0.55])
            with cols[0]:
                label = f"{path}"
                color = "#22c55e" if path in st.session_state.whitelist else "#ef4444" if path in st.session_state.blacklist else "#60a5fa"
                if st.button(
                    f"{label}",
                    key=f"btn_{path}",
                    help=f"Klicke zum Hinzufügen zur {st.session_state.interaction_mode}.",
                    use_container_width=True,
                ):
                    _add_to_mode(path)
                st.markdown(
                    f"<div style='padding-left:{indent * 18}px; font-family: monospace; color:{color};'>\"{html.escape(key)}\"</div>",
                    unsafe_allow_html=True,
                )
            with cols[1]:
                if isinstance(value, (dict, list)):
                    _render_editor_line(indent, ":")
                    _render_json_interactive(value, path, indent + 1)
                else:
                    _render_editor_line(indent, f": {_format_scalar(value)}", "#d4d4d4")
        _render_editor_line(indent, "}")
    elif isinstance(data, list):
        _render_editor_line(indent, "[")
        for idx, item in enumerate(data):
            path = f"{base}[{idx}]" if base else f"[{idx}]"
            if isinstance(item, (dict, list)):
                _render_json_interactive(item, base, indent + 1)
            else:
                _render_editor_line(indent + 1, _format_scalar(item), "#d4d4d4")
        _render_editor_line(indent, "]")
    else:
        _render_editor_line(indent, _format_scalar(data), "#d4d4d4")


def _download_list(label: str, values: set[str]) -> None:
    st.download_button(
        label=f"{label} exportieren",
        data=json.dumps(sorted(values), ensure_ascii=False, indent=2),
        file_name=f"{label.lower()}.json",
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    _init_state()

    st.title("🧭 JSON Lister – IDE-artige Variablenauswahl")
    st.caption("Fokus auf Fragen/Hauptkörper des JSON; Metadaten werden ausgeblendet.")

    with st.sidebar:
        st.subheader("Datenquelle")
        _load_json()

        if st.session_state.raw_json is not None:
            scopes = _find_candidate_scopes(st.session_state.raw_json)
            selected_scope = st.selectbox("Zu analysierender Bereich", options=list(scopes.keys()))
            st.session_state.scope_label = selected_scope
            st.session_state.scope_data = scopes[selected_scope]

            st.session_state.interaction_mode = st.radio(
                "Klickmodus",
                ["Whitelist", "Blacklist"],
                horizontal=True,
                help="Klick auf Variablennamen ordnet den Eintrag dieser Liste zu.",
            )
            st.session_state.hide_blacklisted = st.checkbox(
                "Blacklist-Einträge in Darstellung verbergen",
                value=st.session_state.hide_blacklisted,
            )

            if st.button("Whitelist/Blacklist zurücksetzen", use_container_width=True):
                _clear_lists()

            paths = sorted(_extract_variable_paths(st.session_state.scope_data))
            st.session_state.all_variable_paths = paths

            st.info(
                f"Datei: {st.session_state.filename}\n"
                f"Bereich: {st.session_state.scope_label}\n"
                f"Gefundene Variablen: {len(paths)}"
            )
        else:
            st.info("Bitte eine JSON-Datei laden.")

    if st.session_state.scope_data is None:
        st.markdown(
            "### Anleitung\n"
            "1. JSON-Datei hochladen.\n"
            "2. Hauptbereich (ohne Metadaten) wählen.\n"
            "3. Im Editor Variablennamen anklicken und Whitelist/Blacklist erstellen."
        )
        return

    left, right = st.columns([2.2, 1])

    with left:
        st.markdown("#### JSON-Editoransicht (anklickbare Variablennamen)")
        st.markdown(
            "<div style='background:#1e1e1e; padding:12px; border-radius:8px;'>",
            unsafe_allow_html=True,
        )
        _render_json_interactive(st.session_state.scope_data)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("#### Whitelist (grün)")
        st.dataframe({"Variable": sorted(st.session_state.whitelist)}, use_container_width=True, height=180)
        remove_wl = st.multiselect("Whitelist entfernen", sorted(st.session_state.whitelist), key="remove_wl")
        if st.button("Aus Whitelist löschen", use_container_width=True):
            for item in remove_wl:
                st.session_state.whitelist.discard(item)
        _download_list("Whitelist", st.session_state.whitelist)

        st.markdown("---")
        st.markdown("#### Blacklist (rot)")
        st.dataframe({"Variable": sorted(st.session_state.blacklist)}, use_container_width=True, height=180)
        remove_bl = st.multiselect("Blacklist entfernen", sorted(st.session_state.blacklist), key="remove_bl")
        if st.button("Aus Blacklist löschen", use_container_width=True):
            for item in remove_bl:
                st.session_state.blacklist.discard(item)
        _download_list("Blacklist", st.session_state.blacklist)

        st.markdown("---")
        st.markdown("#### Alle gefundenen Variablen")
        search = st.text_input("Suche", "")
        matches = [p for p in st.session_state.all_variable_paths if search.lower() in p.lower()]
        st.dataframe({"Pfad": matches[:300]}, use_container_width=True, height=220)


if __name__ == "__main__":
    main()
