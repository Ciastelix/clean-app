import asyncio
from collections import defaultdict
from pathlib import Path
import flet as ft
import xxhash


def hash_file_xxhash(file_path):
    h = xxhash.xxh128()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def remove_duplicates(files):
    duplicates = {h: paths for h, paths in files.items() if len(paths) > 1}
    for file_list in duplicates.values():
        for path_to_remove in file_list[1:]:
            try:
                Path(path_to_remove).unlink()
            except OSError as e:
                print(f"{path_to_remove}: {e}")

def scan_for_files(files_dict):
    start_path = Path.home()
    for i in start_path.rglob("*"):
        try:
            if i.is_file() and i.stat().st_size > 0:
                file_hash = hash_file_xxhash(i)
                files_dict[file_hash].append(str(i))
        except (PermissionError, OSError):
            continue
    return files_dict


def ui(page: ft.Page):
    page.title = "Clean App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0
    files = defaultdict(list)
    loading_spinner = ft.ProgressRing(visible=False)
    start_button = ft.Button("Start Scanning")

    def close_dialog(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Scan Complete"),
        content=ft.Text("Scanning finished."),
        actions=[
            ft.TextButton("Delete Duplicates"),
            ft.TextButton("Close", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg)

    def on_scan_complete():
        duplicates = {h: p for h, p in files.items() if len(p) > 1}
        dup_count = sum(len(v) - 1 for v in duplicates.values())
        start_button.visible = True
        start_button.disabled = False
        start_button.text = "Start Scanning"
        loading_spinner.visible = False

        if dup_count == 0:
            dlg.content = ft.Text("No duplicates found.")
        else:
            rows = []
            for file_hash, paths in duplicates.items():
                rows.append(
                    ft.Text(
                        f"Original: {paths[0]}",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                    )
                )
                for dup_path in paths[1:]:
                    rows.append(ft.Text(f"  Duplicate: {dup_path}", size=12))
                rows.append(ft.Divider())

            dlg.content = ft.Container(
                content=ft.Column(
                    rows,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=4,
                ),
                width=500,
                height=400,
            )

        dlg.title = ft.Text(f"Found {dup_count} duplicate(s)")
        dlg.open = True
        page.update()

    async def do_scan_async():
        nonlocal files
        loop = asyncio.get_event_loop()
        files = await loop.run_in_executor(None, scan_for_files, files)
        on_scan_complete()

    def button_clicked(e):
        start_button.visible = False
        loading_spinner.visible = True
        page.update()
        page.run_task(do_scan_async)

    start_button.on_click = button_clicked

    page.add(
        ft.Column(
            [start_button, loading_spinner],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            expand=True,
        )
    )

def main():
    ft.run(ui)


if __name__ == "__main__":
    main()
