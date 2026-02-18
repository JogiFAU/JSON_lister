import html
import json
from typing import Any

import streamlit as st


st.set_page_config(page_title="JSON Lister IDE", page_icon="🧭", layout="wide")


def _init_state() -> None:
    defaults = {
        "raw_json": None,
        "filename": "",
        "whitelist": set(),
        "blacklist": set(),
        "interaction_mode": "Whitelist",
        "hide_blacklisted": False,
        "all_variable_paths": [],
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


def _extract_variable_paths(data: Any, base: str = "") -> set[str]:
    """Return unique schema-like paths (arrays normalized as [])."""
    paths: set[str] = set()
    if isinstance(data, dict):
        for key, value in data.items():
            current = f"{base}.{key}" if base else key
            paths.add(current)
            paths.update(_extract_variable_paths(value, current))
    elif isinstance(data, list):
        list_base = f"{base}[]" if base else "[]"
        for item in data:
            paths.update(_extract_variable_paths(item, list_base))
    return paths


def _format_scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _apply_mode(path: str) -> None:
    mode = st.session_state.interaction_mode
    if mode == "Whitelist":
        st.session_state.whitelist.add(path)
        st.session_state.blacklist.discard(path)
    elif mode == "Blacklist":
        st.session_state.blacklist.add(path)
        st.session_state.whitelist.discard(path)
    else:  # Zuordnung aufheben
        st.session_state.blacklist.discard(path)
        st.session_state.whitelist.discard(path)


def _path_color(path: str) -> str:
    if path in st.session_state.whitelist:
        return "#22c55e"  # green
    if path in st.session_state.blacklist:
        return "#ef4444"  # red
    return "#93c5fd"  # blue


def _should_hide(path: str) -> bool:
    if not st.session_state.hide_blacklisted:
        return False
    for blacklisted in st.session_state.blacklist:
        if path == blacklisted or path.startswith(blacklisted + ".") or path.startswith(blacklisted + "[]"):
            return True
    return False


def _editor_line(indent: int, text: str, color: str = "#d4d4d4") -> None:
    st.markdown(
        (
            f"<div style='padding-left:{indent * 18}px; color:{color}; "
            "font-family: Consolas, Menlo, monospace; white-space: pre;'>"
            f"{html.escape(text)}</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_interactive_json(
    data: Any,
    base_schema: str = "",
    base_concrete: str = "",
    indent: int = 0,
) -> None:
    """
    Render full JSON. Click assigns schema-like path (with []) so one field selection
    applies to all matching array elements.
    """
    if isinstance(data, dict):
        _editor_line(indent, "{")
        visible_items = []
        for key, value in data.items():
            schema_path = f"{base_schema}.{key}" if base_schema else key
            concrete_path = f"{base_concrete}.{key}" if base_concrete else key
            if _should_hide(schema_path):
                continue
            visible_items.append((key, value, schema_path, concrete_path))

        for idx, (key, value, schema_path, concrete_path) in enumerate(visible_items):
            comma = "," if idx < len(visible_items) - 1 else ""

            row = st.columns([0.44, 0.56])
            with row[0]:
                if st.button(schema_path, key=f"var_{concrete_path}", use_container_width=True):
                    _apply_mode(schema_path)

                st.markdown(
                    (
                        f"<div style='padding-left:{indent * 18}px; font-family: Consolas, Menlo, monospace; "
                        f"color:{_path_color(schema_path)};'>"
                        f"\"{html.escape(key)}\""
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

            with row[1]:
                if isinstance(value, (dict, list)):
                    _editor_line(indent, f": {comma}")
                    _render_interactive_json(
                        value,
                        base_schema=schema_path,
                        base_concrete=concrete_path,
                        indent=indent + 1,
                    )
                else:
                    _editor_line(indent, f": {_format_scalar(value)}{comma}")

        _editor_line(indent, "}")

    elif isinstance(data, list):
        _editor_line(indent, "[")
        for idx, item in enumerate(data):
            list_schema = f"{base_schema}[]" if base_schema else "[]"
            list_concrete = f"{base_concrete}[{idx}]" if base_concrete else f"[{idx}]"

            if isinstance(item, (dict, list)):
                _render_interactive_json(
                    item,
                    base_schema=list_schema,
                    base_concrete=list_concrete,
                    indent=indent + 1,
                )
            else:
                comma = "," if idx < len(data) - 1 else ""
                _editor_line(indent + 1, f"{_format_scalar(item)}{comma}")
        _editor_line(indent, "]")
    else:
        _editor_line(indent, _format_scalar(data))


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

    st.title("🧭 JSON Lister – Editoransicht mit Variablen-Flags")
    st.caption("Links Optionen, rechts gesamter JSON-Inhalt wie in einer IDE inklusive Flag-Farben.")

    left, right = st.columns([1, 2.2])

    with left:
        st.subheader("Optionen")
        _load_json()

        st.session_state.interaction_mode = st.radio(
            "Klickmodus",
            ["Whitelist", "Blacklist", "Zuordnung aufheben"],
            help=(
                "Whitelist: Feld wird grün markiert. "
                "Blacklist: Feld wird rot markiert. "
                "Zuordnung aufheben: Markierung wird entfernt."
            ),
        )

        st.session_state.hide_blacklisted = st.checkbox(
            "Blacklist-Einträge ausblenden",
            value=st.session_state.hide_blacklisted,
            help="Blendet blacklisted Felder aus, um das Endresultat zu simulieren.",
        )

        if st.button("Whitelist/Blacklist zurücksetzen", use_container_width=True):
            _clear_lists()

        if st.session_state.raw_json is not None:
            all_paths = sorted(_extract_variable_paths(st.session_state.raw_json))
            st.session_state.all_variable_paths = all_paths
            st.info(
                f"Datei: {st.session_state.filename}\n"
                f"Einzigartige Felder gesamt: {len(all_paths)}\n"
                f"Whitelist: {len(st.session_state.whitelist)} | Blacklist: {len(st.session_state.blacklist)}"
            )

            st.markdown("#### Whitelist (grün)")
            st.dataframe({"Variable": sorted(st.session_state.whitelist)}, use_container_width=True, height=160)
            _download_list("Whitelist", st.session_state.whitelist)

            st.markdown("#### Blacklist (rot)")
            st.dataframe({"Variable": sorted(st.session_state.blacklist)}, use_container_width=True, height=160)
            _download_list("Blacklist", st.session_state.blacklist)

            search = st.text_input("Suche Variablenpfad", "")
            matches = [p for p in all_paths if search.lower() in p.lower()]
            st.dataframe({"Pfad": matches[:300]}, use_container_width=True, height=160)
        else:
            st.info("Bitte zuerst eine JSON-Datei laden.")

    with right:
        st.subheader("JSON-Editoransicht")
        if st.session_state.raw_json is None:
            st.markdown(
                "### Anleitung\n"
                "1. JSON-Datei links laden.\n"
                "2. Klickmodus wählen (Whitelist/Blacklist/Zuordnung aufheben).\n"
                "3. Variablennamen im Editor anklicken.\n"
                "4. In Arrays gilt ein Klick für alle Elemente mit diesem Feld (z. B. `Questions[].Text`)."
            )
        else:
            st.markdown(
                """
                <div style='background:#1e1e1e; border-radius:8px; padding:12px; border:1px solid #2d2d2d;'></div>
                """,
                unsafe_allow_html=True,
            )
            _render_interactive_json(st.session_state.raw_json)


if __name__ == "__main__":
    main()
