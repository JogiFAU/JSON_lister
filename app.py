import json
from dataclasses import dataclass
from typing import Any

import streamlit as st


st.set_page_config(page_title="JSON Field Blacklist Builder", page_icon="🧭", layout="wide")


@dataclass
class FieldInfo:
    path: str
    depth: int
    is_leaf: bool
    first_value: str


def _init_state() -> None:
    defaults = {
        "raw_json": None,
        "filename": "",
        "records": [],
        "blacklist": set(),
        "field_infos": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _load_json() -> None:
    uploaded = st.file_uploader("JSON-Datei laden", type=["json"])
    if not uploaded:
        return

    try:
        raw = json.load(uploaded)
    except Exception as err:
        st.error(f"Datei konnte nicht gelesen werden: {err}")
        return

    st.session_state.raw_json = raw
    st.session_state.records = raw if isinstance(raw, list) else [raw]
    st.session_state.filename = uploaded.name


def _extract_paths(node: Any, base: str = "") -> set[str]:
    paths: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            current = f"{base}.{key}" if base else key
            paths.add(current)
            paths.update(_extract_paths(value, current))
    elif isinstance(node, list):
        list_base = f"{base}[]" if base else "[]"
        for item in node:
            paths.update(_extract_paths(item, list_base))
    return paths


def _path_depth(path: str) -> int:
    return path.count(".") + path.count("[]")


def _split_path(path: str) -> list[str]:
    parts: list[str] = []
    for token in path.split("."):
        if token.endswith("[]") and token != "[]":
            parts.append(token[:-2])
            parts.append("[]")
        else:
            parts.append(token)
    return parts


def _values_for_path(node: Any, path: str) -> list[Any]:
    tokens = _split_path(path)

    def walk(current: Any, idx: int) -> list[Any]:
        if idx >= len(tokens):
            return [current]

        token = tokens[idx]
        if token == "[]":
            if not isinstance(current, list):
                return []
            results: list[Any] = []
            for item in current:
                results.extend(walk(item, idx + 1))
            return results

        if not isinstance(current, dict) or token not in current:
            return []
        return walk(current[token], idx + 1)

    return walk(node, 0)


def _compact_json(value: Any, max_len: int = 100) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def _is_leaf(path: str, all_paths: set[str]) -> bool:
    prefix_dot = path + "."
    prefix_arr = path + "[]"
    for other in all_paths:
        if other != path and (other.startswith(prefix_dot) or other.startswith(prefix_arr)):
            return False
    return True


def _build_field_infos(records: list[Any]) -> list[FieldInfo]:
    all_paths: set[str] = set()
    for record in records:
        all_paths.update(_extract_paths(record))

    infos: list[FieldInfo] = []
    for path in sorted(all_paths):
        leaf = _is_leaf(path, all_paths)
        first_value = "-"
        if leaf:
            for record in records:
                values = _values_for_path(record, path)
                if values:
                    first_value = _compact_json(values[0])
                    break

        infos.append(
            FieldInfo(
                path=path,
                depth=_path_depth(path),
                is_leaf=leaf,
                first_value=first_value,
            )
        )

    return infos


def _display_path(path: str, depth: int) -> str:
    return f"{'  ' * depth}{path}"


def _descendant_leaves(path: str, infos: list[FieldInfo]) -> set[str]:
    descendants: set[str] = set()
    for info in infos:
        if info.is_leaf and (info.path == path or info.path.startswith(path + ".") or info.path.startswith(path + "[]")):
            descendants.add(info.path)
    return descendants


def _resolve_blacklist_from_editor(edited_rows: list[dict[str, Any]], infos: list[FieldInfo]) -> set[str]:
    info_map = {info.path: info for info in infos}
    resolved: set[str] = set()

    for row in edited_rows:
        path = row["Path"]
        is_marked = bool(row.get("Blacklist"))
        info = info_map[path]

        if not is_marked:
            continue

        if info.is_leaf:
            resolved.add(path)
        else:
            resolved.update(_descendant_leaves(path, infos))

    return resolved


def _export_blacklist() -> None:
    payload = json.dumps(sorted(st.session_state.blacklist), ensure_ascii=False, indent=2)
    st.download_button(
        "Blacklist exportieren",
        data=payload,
        file_name="blacklist.json",
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    _init_state()

    st.title("🧭 JSON Blacklist Builder")
    st.caption("Felder hierarchisch prüfen und finale Felder für die Bereinigung blacklisten.")

    left, right = st.columns([1, 2.2])

    with left:
        st.subheader("Optionen")
        _load_json()

        if st.button("Feldanalyse aktualisieren", use_container_width=True):
            if st.session_state.records:
                st.session_state.field_infos = _build_field_infos(st.session_state.records)

        if st.button("Blacklist zurücksetzen", use_container_width=True):
            st.session_state.blacklist = set()

        if st.session_state.records:
            if not st.session_state.field_infos:
                st.session_state.field_infos = _build_field_infos(st.session_state.records)

            leaf_count = sum(1 for f in st.session_state.field_infos if f.is_leaf)
            st.info(
                f"Datei: {st.session_state.filename}\n"
                f"Einträge: {len(st.session_state.records)}\n"
                f"Felder gesamt: {len(st.session_state.field_infos)}\n"
                f"Finale Felder: {leaf_count}\n"
                f"Blacklist-Einträge: {len(st.session_state.blacklist)}"
            )

            st.markdown("#### Blacklist (nur finale Felder)")
            st.dataframe({"Field": sorted(st.session_state.blacklist)}, use_container_width=True, height=220)
            _export_blacklist()
        else:
            st.info("Bitte zuerst eine JSON-Datei laden.")

    with right:
        st.subheader("Feldübersicht (Hierarchie)")

        if not st.session_state.records:
            st.markdown(
                "### Anleitung\n"
                "1. JSON-Datei laden.\n"
                "2. Haken setzen, um Felder zu blacklisten.\n"
                "3. Nicht-finale Felder markieren automatisch alle untergeordneten finalen Felder.\n"
                "4. Export der Blacklist als JSON."
            )
            return

        infos: list[FieldInfo] = st.session_state.field_infos

        rows: list[dict[str, Any]] = []
        for info in infos:
            if info.is_leaf:
                checked = info.path in st.session_state.blacklist
            else:
                descendants = _descendant_leaves(info.path, infos)
                checked = bool(descendants) and descendants.issubset(st.session_state.blacklist)

            rows.append(
                {
                    "Blacklist": checked,
                    "Field": _display_path(info.path, info.depth),
                    "Path": info.path,
                    "Final": "Ja" if info.is_leaf else "Nein",
                    "Erster Wert": info.first_value if info.is_leaf else "-",
                }
            )

        edited = st.data_editor(
            rows,
            use_container_width=True,
            hide_index=True,
            key="field_editor",
            column_config={
                "Blacklist": st.column_config.CheckboxColumn(
                    "Blacklist",
                    help="Bei übergeordneten Feldern werden alle untergeordneten finalen Felder markiert.",
                    default=False,
                ),
                "Field": st.column_config.TextColumn("Field (Hierarchie)", disabled=True),
                "Path": st.column_config.TextColumn("Pfad", disabled=True),
                "Final": st.column_config.TextColumn("Finales Feld", disabled=True),
                "Erster Wert": st.column_config.TextColumn("Erster gefundener Wert", disabled=True),
            },
            disabled=["Field", "Path", "Final", "Erster Wert"],
        )

        st.session_state.blacklist = _resolve_blacklist_from_editor(edited, infos)


if __name__ == "__main__":
    main()
