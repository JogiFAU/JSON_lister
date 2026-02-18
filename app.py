import json
from dataclasses import dataclass
from typing import Any

import streamlit as st


st.set_page_config(page_title="JSON Field Blacklist Builder", page_icon="🧭", layout="wide")


@dataclass
class FieldInfo:
    path: str
    depth: int
    samples: list[str]


def _init_state() -> None:
    defaults = {
        "raw_json": None,
        "filename": "",
        "records": [],
        "sample_count": 3,
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

    if isinstance(raw, list):
        records = raw
    else:
        records = [raw]

    st.session_state.raw_json = raw
    st.session_state.records = records
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
    depth = path.count(".")
    depth += path.count("[]")
    return depth


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


def _compact_json(value: Any, max_len: int = 90) -> str:
    text = json.dumps(value, ensure_ascii=False)
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _even_indices(count: int, picks: int) -> list[int]:
    if count <= 0:
        return []
    if picks >= count:
        return list(range(count))
    if picks == 1:
        return [0]

    step = (count - 1) / (picks - 1)
    raw = [round(i * step) for i in range(picks)]

    # strictly increasing & bounded
    indices: list[int] = []
    prev = -1
    for idx in raw:
        idx = max(idx, prev + 1)
        idx = min(idx, count - (picks - len(indices)))
        indices.append(idx)
        prev = idx

    indices[0] = 0
    indices[-1] = count - 1
    return indices


def _build_field_infos(records: list[Any], sample_count: int) -> list[FieldInfo]:
    unique_paths: set[str] = set()
    for record in records:
        unique_paths.update(_extract_paths(record))

    infos: list[FieldInfo] = []
    for path in sorted(unique_paths):
        seen: list[tuple[int, Any]] = []
        for ridx, record in enumerate(records):
            values = _values_for_path(record, path)
            if values:
                # per record first matching value for interpretation
                seen.append((ridx, values[0]))

        if seen:
            pick_idx = _even_indices(len(seen), sample_count)
            samples = [f"#{seen[i][0] + 1}: {_compact_json(seen[i][1])}" for i in pick_idx]
        else:
            samples = ["-"]

        infos.append(FieldInfo(path=path, depth=_path_depth(path), samples=samples))

    return infos


def _display_path(path: str, depth: int) -> str:
    return f"{'  ' * depth}{path}"


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
    st.caption("Einzigartige Felder mit Beispielwerten prüfen und Blacklist für spätere Bereinigung erstellen.")

    left, right = st.columns([1, 2.2])

    with left:
        st.subheader("Optionen")
        _load_json()

        st.session_state.sample_count = st.number_input(
            "Anzahl Beispielwerte pro Feld (X)",
            min_value=2,
            max_value=10,
            value=int(st.session_state.sample_count),
            step=1,
            help="Standard: 3. Die Beispiele werden möglichst gleichmäßig über vorhandene Einträge verteilt.",
        )

        if st.button("Feldanalyse aktualisieren", use_container_width=True):
            if st.session_state.records:
                st.session_state.field_infos = _build_field_infos(
                    st.session_state.records,
                    int(st.session_state.sample_count),
                )

        if st.button("Blacklist zurücksetzen", use_container_width=True):
            st.session_state.blacklist = set()

        if st.session_state.records:
            if not st.session_state.field_infos:
                st.session_state.field_infos = _build_field_infos(
                    st.session_state.records,
                    int(st.session_state.sample_count),
                )

            st.info(
                f"Datei: {st.session_state.filename}\n"
                f"Einträge: {len(st.session_state.records)}\n"
                f"Einzigartige Felder: {len(st.session_state.field_infos)}\n"
                f"Blacklist-Einträge: {len(st.session_state.blacklist)}"
            )

            st.markdown("#### Blacklist")
            st.dataframe({"Field": sorted(st.session_state.blacklist)}, use_container_width=True, height=200)
            _export_blacklist()
        else:
            st.info("Bitte zuerst eine JSON-Datei laden.")

    with right:
        st.subheader("Feldübersicht (Hierarchie + Beispielwerte)")

        if not st.session_state.records:
            st.markdown(
                "### Anleitung\n"
                "1. JSON-Datei laden.\n"
                "2. X Beispielwerte einstellen (Standard 3, min 2, max 10).\n"
                "3. Felder in der Tabelle für die Blacklist markieren.\n"
                "4. Blacklist exportieren."
            )
            return

        infos: list[FieldInfo] = st.session_state.field_infos

        rows: list[dict[str, Any]] = []
        max_samples = int(st.session_state.sample_count)
        for info in infos:
            row: dict[str, Any] = {
                "Blacklist": info.path in st.session_state.blacklist,
                "Field": _display_path(info.path, info.depth),
                "Path": info.path,
            }
            for idx in range(max_samples):
                row[f"Beispiel {idx + 1}"] = info.samples[idx] if idx < len(info.samples) else "-"
            rows.append(row)

        edited = st.data_editor(
            rows,
            use_container_width=True,
            hide_index=True,
            key="field_editor",
            column_config={
                "Blacklist": st.column_config.CheckboxColumn(
                    "Blacklist",
                    help="Aktiviere, um das Field in die Blacklist aufzunehmen.",
                    default=False,
                ),
                "Field": st.column_config.TextColumn("Field (Hierarchie)", disabled=True),
                "Path": st.column_config.TextColumn("Pfad", disabled=True),
            },
            disabled=["Field", "Path"] + [f"Beispiel {i + 1}" for i in range(max_samples)],
        )

        new_blacklist = {row["Path"] for row in edited if row.get("Blacklist")}
        st.session_state.blacklist = new_blacklist


if __name__ == "__main__":
    main()
