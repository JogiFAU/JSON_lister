import argparse
import json
from pathlib import Path
from typing import Any


def split_path(path: str) -> list[str]:
    parts: list[str] = []
    for token in path.split('.'):
        if token.endswith('[]') and token != '[]':
            parts.append(token[:-2])
            parts.append('[]')
        else:
            parts.append(token)
    return parts


def delete_path(node: Any, tokens: list[str], idx: int = 0) -> None:
    if idx >= len(tokens):
        return

    token = tokens[idx]

    if token == '[]':
        if isinstance(node, list):
            for item in node:
                delete_path(item, tokens, idx + 1)
        return

    if isinstance(node, list):
        for item in node:
            delete_path(item, tokens, idx)
        return

    if not isinstance(node, dict) or token not in node:
        return

    is_last = idx == len(tokens) - 1
    if is_last:
        del node[token]
        return

    child = node[token]

    if idx + 1 < len(tokens) and tokens[idx + 1] == '[]':
        if isinstance(child, list):
            if idx + 1 == len(tokens) - 1:
                del node[token]
                return
            for item in child:
                delete_path(item, tokens, idx + 2)
        return

    delete_path(child, tokens, idx + 1)


def clean_data(data: Any, blacklist_paths: list[str]) -> Any:
    for path in blacklist_paths:
        tokens = split_path(path)
        delete_path(data, tokens)
    return data


def load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as file:
        return json.load(file)


def save_json(path: Path, payload: Any) -> None:
    with path.open('w', encoding='utf-8') as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_clean.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Bereinigt eine JSON-Datei anhand einer Blacklist von Feldpfaden.'
    )
    parser.add_argument('input_json', type=Path, help='Pfad zur zu bereinigenden JSON-Datei.')
    parser.add_argument('blacklist_json', type=Path, help='Pfad zur Blacklist JSON-Datei (Liste von Feldpfaden).')
    parser.add_argument(
        '-o',
        '--output',
        type=Path,
        default=None,
        help='Optionaler Ausgabepfad. Standard: [input]_clean.json',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data = load_json(args.input_json)
    blacklist = load_json(args.blacklist_json)

    if not isinstance(blacklist, list) or not all(isinstance(entry, str) for entry in blacklist):
        raise ValueError('Die Blacklist muss ein JSON-Array mit Feldpfaden (Strings) sein.')

    cleaned = clean_data(data, blacklist)

    output_path = args.output or default_output_path(args.input_json)
    save_json(output_path, cleaned)

    print(f"Bereinigung abgeschlossen. Datei gespeichert unter: {output_path}")


if __name__ == '__main__':
    main()
