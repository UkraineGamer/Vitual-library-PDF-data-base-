import tkinter as tk
from tkinter import font as tkfont

from virtual_library.config import COLORS, DARK_COLORS, LIGHT_COLORS, TextAnchor, TextJustify, UI_STRINGS
from virtual_library.data import BOOKS, CATEGORIES, DOWNLOADS, SIDEBAR_ITEMS
from virtual_library.services import BookSearch
from virtual_library.ui.components import UiComponentsMixin
from virtual_library.ui.views import AppViewsMixin


class BookDownloaderApp(AppViewsMixin, UiComponentsMixin):
    def __init__(self) -> None:
        self.book_search = BookSearch()
        self.root = tk.Tk()
        self.root.title("BookDownloader")
        self.root.geometry("1280x850")
        self.root.minsize(1060, 700)
        self.root.configure(bg=COLORS["app"])

        self.canvas = tk.Canvas(
            self.root,
            bg=COLORS["app"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.fonts = self._build_fonts()
        self.buttons: list[dict] = []
        self.hover_action: tuple[str, str | None] | None = None
        self.selected_book_id = "1984"
        self.active_nav = "Пошук книг"
        self.active_category = "Усі"
        self.bookmarks: set[str] = {"1984"}
        self.favorites: set[str] = set()
        self.filter_open = False
        self.filter_format = ""
        self.filter_language = ""
        self.filter_rating = ""
        self.description_expanded = False
        self.interface_language = "uk"
        self.theme_mode = "dark"
        self.font_size = "medium"
        self.placeholder_active = True
        self.api_results: list[dict] | None = None
        self.extra_books: dict[str, dict] = {}
        self.results_scroll = 0
        self.results_scroll_bounds: tuple[float, float, float, float, int] | None = None
        self.results_scrollbar_bounds: tuple[float, float, float, float, int, float, float, float] | None = None
        self.category_scroll = 0
        self.category_scroll_bounds: tuple[float, float, float, float, int] | None = None
        self.category_scrollbar_bounds: tuple[float, float, float, float, int, float, float, float] | None = None
        self.scroll_drag: dict | None = None
        self._search_area_bottom = 120
        self._category_container_geom: dict | None = None
        self.download_col_status_w = 110
        self.download_col_date_w = 132
        self.download_col_size_w = 80
        self.download_col_resize_handles: list[dict] = []
        self.download_data_scroll = 0
        self.download_data_scroll_bounds: tuple[float, float, float, float, int] | None = None
        self.download_data_scrollbar_bounds: tuple[float, float, float, float, int, float, float, float] | None = None

        self.search_entry = tk.Entry(
            self.root,
            bd=0,
            relief=tk.FLAT,
            bg=COLORS["input_bg"],
            fg=COLORS["text_muted"],
            insertbackground=COLORS["text"],
            font=self.fonts["body"],
        )
        self.search_entry.insert(0, UI_STRINGS["uk"]["search_placeholder"])
        self.search_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_entry_focus_out)
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", lambda _event: self._run_search())

        self.canvas.bind("<Configure>", lambda _event: self.draw())
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", self._on_leave)

        self._apply_theme()
        self.draw()

    def run(self) -> None:
        self.root.mainloop()

    def _build_fonts(self) -> dict[str, tkfont.Font]:
        return {
            "brand": tkfont.Font(family="Segoe UI", size=10, weight="bold"),
            "nav": tkfont.Font(family="Segoe UI", size=10),
            "body": tkfont.Font(family="Segoe UI", size=13),
            "body_small": tkfont.Font(family="Segoe UI", size=10),
            "body_detail": tkfont.Font(family="Segoe UI", size=11),
            "caption": tkfont.Font(family="Segoe UI", size=8),
            "section": tkfont.Font(family="Segoe UI Semibold", size=11),
            "title": tkfont.Font(family="Segoe UI Semibold", size=13),
            "detail_title": tkfont.Font(family="Segoe UI Semibold", size=22),
            "button": tkfont.Font(family="Segoe UI Semibold", size=10),
            "cover": tkfont.Font(family="Georgia", size=17, weight="bold"),
            "cover_small": tkfont.Font(family="Georgia", size=8, weight="bold"),
        }

    def _apply_font_size(self) -> None:
        base_sizes = {
            "brand": 10,
            "nav": 10,
            "body": 10,
            "body_small": 9,
            "caption": 8,
            "section": 11,
            "title": 13,
            "detail_title": 22,
            "button": 10,
            "cover": 17,
            "cover_small": 8,
        }
        offset = {"small": -1, "medium": 0, "large": 2}[self.font_size]
        for name, base_size in base_sizes.items():
            self.fonts[name].configure(size=base_size + offset)
    def _book_by_id(self, book_id: str) -> dict:
        if self.extra_books.get(book_id):
            return self.extra_books[book_id]
        if self.api_results:
            for book in self.api_results:
                if book["id"] == book_id:
                    return book
        for book in BOOKS:
            if book["id"] == book_id:
                return book
        return BOOKS[0]

    def _catalog_books(self) -> list[dict]:
        if self.api_results is not None:
            return self.api_results
        return BOOKS

    def _library_books(self) -> list[dict]:
        library_ids = {item["book_id"] for item in DOWNLOADS if item.get("file_path")}
        return [self._book_by_id(book_id) for book_id in library_ids]

    def _query(self) -> str:
        if self.placeholder_active:
            return ""
        return self.search_entry.get().strip().casefold()

    def _reset_results_scroll(self) -> None:
        self.results_scroll = 0

    def _category_chips_metrics(self) -> tuple[list[tuple[str, float]], float]:
        chips: list[tuple[str, float]] = []
        for category in CATEGORIES:
            chip_w = max(32, self.fonts["body_small"].measure(category) + 24)
            chips.append((category, chip_w))
        total_w = sum(chip_w for _, chip_w in chips) + max(0, (len(chips) - 1) * 8)
        return chips, total_w

    def _apply_theme(self) -> None:
        palette = LIGHT_COLORS if self.theme_mode == "light" else DARK_COLORS
        COLORS.clear()
        COLORS.update(palette)
        self.root.configure(bg=COLORS["app"])
        self.canvas.configure(bg=COLORS["app"])
        entry_fg = COLORS["text_muted"] if self.placeholder_active else COLORS["text"]
        self.search_entry.configure(
            bg=COLORS["input_bg"],
            fg=entry_fg,
            insertbackground=COLORS["text"],
        )

    def _t(self, key: str) -> str:
        lang = "en" if self.interface_language == "en" else "uk"
        return UI_STRINGS.get(lang, UI_STRINGS["uk"]).get(key, UI_STRINGS["uk"].get(key, key))

    def _nav_label(self, uk_label: str) -> str:
        mapping = {
            "Головна": "nav_home",
            "Пошук книг": "nav_search",
            "Завантаження": "nav_downloads",
            "Історія": "nav_history",
            "Бібліотека": "nav_library",
            "Обране": "nav_favorites",
            "Налаштування": "nav_settings",
        }
        return self._t(mapping.get(uk_label, "nav_search"))

    def _update_search_placeholder(self) -> None:
        if self.placeholder_active:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self._t("search_placeholder"))
            self.search_entry.configure(fg=COLORS["text_muted"])

    def _visible_books(self) -> list[dict]:
        if self.active_nav == "Бібліотека":
            source = self._library_books()
        elif self.active_nav == "Обране":
            source = [self._book_by_id(book_id) for book_id in self.favorites]
        else:
            source = self._catalog_books()

        query = self._query()
        visible = []
        for book in source:
            if self.active_nav not in ("Бібліотека", "Обране"):
                if self.active_category not in ("Усі", "Більше⌄") and self.active_category not in book["categories"]:
                    continue
            if self.filter_format and book["format"] != self.filter_format:
                continue
            if self.filter_language and book["language"] != self.filter_language:
                continue
            if self.filter_rating:
                try:
                    if float(book["rating"]) < float(self.filter_rating):
                        continue
                except ValueError:
                    continue
            haystack = " ".join(
                [
                    book["title"],
                    book["author"],
                    book["meta"],
                    str(book["isbn"]),
                ]
            ).casefold()
            if query and query not in haystack:
                continue
            visible.append(book)
        return visible

    def _run_search(self) -> None:
        query = self._query()
        self._reset_results_scroll()
        if not query:
            self.api_results = None
            self.draw()
            return

        results = self.book_search.search_books(query)
        self.api_results = results
        for book in results:
            self.extra_books[book["id"]] = book
        if results:
            self.selected_book_id = results[0]["id"]
        self.draw()

    def _on_entry_focus_in(self, _event: tk.Event) -> None:
        if self.placeholder_active:
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg=COLORS["text"])
            self.placeholder_active = False

    def _on_entry_focus_out(self, _event: tk.Event) -> None:
        if not self.search_entry.get().strip():
            self.placeholder_active = True
            self.search_entry.configure(fg=COLORS["text_muted"])
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self._t("search_placeholder"))
            self.draw()

    def _on_search_change(self, _event: tk.Event) -> None:
        if not self.placeholder_active:
            self._reset_results_scroll()
            self.draw()

    def _on_click(self, event: tk.Event) -> None:
        if self.category_scrollbar_bounds:
            x1, y1, x2, y2, max_scroll, thumb_x, thumb_w, track_w = self.category_scrollbar_bounds
            if max_scroll > 0 and y1 <= event.y <= y2:
                if thumb_x <= event.x <= thumb_x + thumb_w:
                    self.scroll_drag = {
                        "kind": "category",
                        "start_mouse": event.x,
                        "start_scroll": self.category_scroll,
                        "thumb_size": thumb_w,
                        "track_size": track_w,
                        "max_scroll": max_scroll,
                    }
                    return
                if x1 <= event.x <= x2:
                    ratio = (event.x - x1) / max(1, x2 - x1)
                    self.category_scroll = max(0, min(max_scroll, round(ratio * max_scroll)))
                    self.draw()
                    return

        if self.results_scrollbar_bounds:
            x1, y1, x2, y2, max_scroll, thumb_y, thumb_h, track_h = self.results_scrollbar_bounds
            if max_scroll > 0 and x1 <= event.x <= x2:
                if thumb_y <= event.y <= thumb_y + thumb_h:
                    self.scroll_drag = {
                        "kind": "results",
                        "start_mouse": event.y,
                        "start_scroll": self.results_scroll,
                        "thumb_size": thumb_h,
                        "track_size": track_h,
                        "max_scroll": max_scroll,
                    }
                    return
                if y1 <= event.y <= y2:
                    ratio = (event.y - y1) / max(1, y2 - y1)
                    self.results_scroll = max(0, min(max_scroll, round(ratio * max_scroll)))
                    self.draw()
                    return

        if self.download_data_scrollbar_bounds:
            x1, y1, x2, y2, max_scroll, thumb_x, thumb_w, track_w = self.download_data_scrollbar_bounds
            if max_scroll > 0 and y1 <= event.y <= y2:
                if thumb_x <= event.x <= thumb_x + thumb_w:
                    self.scroll_drag = {
                        "kind": "download_data",
                        "start_mouse": event.x,
                        "start_scroll": self.download_data_scroll,
                        "thumb_size": thumb_w,
                        "track_size": track_w,
                        "max_scroll": max_scroll,
                    }
                    return
                if x1 <= event.x <= x2:
                    ratio = (event.x - x1) / max(1, x2 - x1)
                    self.download_data_scroll = max(0, min(max_scroll, round(ratio * max_scroll)))
                    self.draw()
                    return

        for handle in self.download_col_resize_handles:
            if handle["x1"] <= event.x <= handle["x2"] and handle["y1"] <= event.y <= handle["y2"]:
                self.scroll_drag = {
                    "kind": "col_resize",
                    "start_mouse": event.x,
                    "col_a": handle["col_a"],
                    "col_b": handle["col_b"],
                    "start_a": getattr(self, f"download_col_{handle['col_a']}_w"),
                    "start_b": getattr(self, f"download_col_{handle['col_b']}_w"),
                    "min_a": handle["min_a"],
                    "min_b": handle["min_b"],
                }
                return

        for button in reversed(self.buttons):
            if button["x1"] <= event.x <= button["x2"] and button["y1"] <= event.y <= button["y2"]:
                self._handle_action(button["action"], button["payload"])
                return

    def _on_drag(self, event: tk.Event) -> None:
        if not self.scroll_drag:
            return

        drag = self.scroll_drag
        travel = max(1, drag["track_size"] - drag["thumb_size"])
        if drag["kind"] == "category":
            delta = event.x - drag["start_mouse"]
            next_scroll = drag["start_scroll"] + delta * drag["max_scroll"] / travel
            next_scroll = max(0, min(drag["max_scroll"], round(next_scroll)))
            if next_scroll != self.category_scroll:
                self.category_scroll = next_scroll
                self.draw()
        elif drag["kind"] == "results":
            delta = event.y - drag["start_mouse"]
            next_scroll = drag["start_scroll"] + delta * drag["max_scroll"] / travel
            next_scroll = max(0, min(drag["max_scroll"], round(next_scroll)))
            if next_scroll != self.results_scroll:
                self.results_scroll = next_scroll
                self.draw()
        elif drag["kind"] == "download_data":
            delta = event.x - drag["start_mouse"]
            next_scroll = drag["start_scroll"] + delta * drag["max_scroll"] / travel
            next_scroll = max(0, min(drag["max_scroll"], round(next_scroll)))
            if next_scroll != self.download_data_scroll:
                self.download_data_scroll = next_scroll
                self.draw()
        elif drag["kind"] == "col_resize":
            delta = round(event.x - drag["start_mouse"])
            new_a = drag["start_a"] + delta
            new_b = drag["start_b"] - delta
            if new_a >= drag["min_a"] and new_b >= drag["min_b"]:
                setattr(self, f"download_col_{drag['col_a']}_w", new_a)
                setattr(self, f"download_col_{drag['col_b']}_w", new_b)
                self.draw()

    def _on_release(self, _event: tk.Event) -> None:
        self.scroll_drag = None

    def _on_mousewheel(self, event: tk.Event) -> str | None:
        if getattr(event, "num", None) == 4:
            direction = -1
        elif getattr(event, "num", None) == 5:
            direction = 1
        else:
            direction = -1 if event.delta > 0 else 1

        if self.category_scroll_bounds:
            x1, y1, x2, y2, max_scroll = self.category_scroll_bounds
            if x1 <= event.x <= x2 and y1 <= event.y <= y2 and max_scroll > 0:
                step = 40
                next_scroll = max(0, min(max_scroll, self.category_scroll + direction * step))
                if next_scroll != self.category_scroll:
                    self.category_scroll = next_scroll
                    self.draw()
                return "break"

        if self.download_data_scroll_bounds:
            x1, y1, x2, y2, max_scroll = self.download_data_scroll_bounds
            if x1 <= event.x <= x2 and y1 <= event.y <= y2 and max_scroll > 0:
                step = 40
                next_scroll = max(0, min(max_scroll, self.download_data_scroll + direction * step))
                if next_scroll != self.download_data_scroll:
                    self.download_data_scroll = next_scroll
                    self.draw()
                return "break"

        if not self.results_scroll_bounds:
            return None

        x1, y1, x2, y2, max_scroll = self.results_scroll_bounds
        if not (x1 <= event.x <= x2 and y1 <= event.y <= y2) or max_scroll <= 0:
            return None

        next_scroll = max(0, min(max_scroll, self.results_scroll + direction))
        if next_scroll != self.results_scroll:
            self.results_scroll = next_scroll
            self.draw()
        return "break"

    def _on_motion(self, event: tk.Event) -> None:
        over_resize = any(
            handle["x1"] <= event.x <= handle["x2"] and handle["y1"] <= event.y <= handle["y2"]
            for handle in self.download_col_resize_handles
        )
        if over_resize:
            if self.canvas.cget("cursor") != "sb_h_double_arrow":
                self.canvas.configure(cursor="sb_h_double_arrow")
            return

        next_hover: tuple[str, str | None] | None = None
        for button in reversed(self.buttons):
            if button["x1"] <= event.x <= button["x2"] and button["y1"] <= event.y <= button["y2"]:
                next_hover = (button["action"], button["payload"])
                break
        if next_hover != self.hover_action:
            self.hover_action = next_hover
            self.canvas.configure(cursor="hand2" if next_hover else "")
            self.draw()

    def _on_leave(self, _event: tk.Event) -> None:
        if self.hover_action:
            self.hover_action = None
            self.canvas.configure(cursor="")
            self.draw()

    def _handle_action(self, action: str, payload: str | None) -> None:
        if action == "nav" and payload:
            self._reset_results_scroll()
            self.active_nav = payload
            self.filter_open = False
            self.description_expanded = False
            if payload != "Пошук книг":
                self.api_results = None
        elif action == "category" and payload:
            self._reset_results_scroll()
            self.active_category = payload
            visible = self._visible_books()
            if visible and self.selected_book_id not in {book["id"] for book in visible}:
                self.selected_book_id = visible[0]["id"]
        elif action == "select_book" and payload:
            self.selected_book_id = payload
            self.description_expanded = False
        elif action == "search":
            self._run_search()
            return
        elif action == "filter":
            self.filter_open = not self.filter_open
        elif action == "filter_option" and payload:
            self._reset_results_scroll()
            if payload == "format:EPUB":
                self.filter_format = "" if self.filter_format == "EPUB" else "EPUB"
            elif payload == "lang:Українська":
                self.filter_language = "" if self.filter_language == "Українська" else "Українська"
            elif payload == "rating:4":
                self.filter_rating = "" if self.filter_rating == "4" else "4"
        elif action == "bookmark" and payload:
            if payload in self.bookmarks:
                self.bookmarks.remove(payload)
            else:
                self.bookmarks.add(payload)
        elif action == "favorite" and payload:
            if payload in self.favorites:
                self.favorites.remove(payload)
            else:
                self.favorites.add(payload)
        elif action == "download" and payload:
            self._start_download(payload)
        elif action == "remove_download" and payload:
            DOWNLOADS[:] = [item for item in DOWNLOADS if item["book_id"] != payload]
        elif action == "show_history":
            self.active_nav = "Історія"
        elif action == "toggle_description":
            self.description_expanded = not self.description_expanded
        elif action == "set_language" and payload in ("uk", "en"):
            self.interface_language = payload
            self._update_search_placeholder()
        elif action == "set_theme" and payload in ("dark", "light"):
            self.theme_mode = payload
            self._apply_theme()
        elif action == "set_font_size" and payload in ("small", "medium", "large"):
            self.font_size = payload
            self._apply_font_size()
        self.draw()

    def _start_download(self, book_id: str) -> None:
        file_path = self.book_search.get_file_path(self.root)
        if not file_path:
            return

        book = self._book_by_id(book_id)
        for item in DOWNLOADS:
            if item["book_id"] == book_id:
                item["status"] = "Завершено"
                item["date"] = "Щойно"
                item["size"] = book["size"]
                item["progress"] = 100
                item["file_path"] = file_path
                return
        DOWNLOADS.insert(
            0,
            {
                "book_id": book_id,
                "status": "Завершено",
                "date": "Щойно",
                "size": book["size"],
                "progress": 100,
                "file_path": file_path,
            },
        )

    def draw(self) -> None:
        width = max(self.canvas.winfo_width(), 1060)
        height = max(self.canvas.winfo_height(), 700)
        self.canvas.delete("all")
        self.buttons = []
        self.results_scroll_bounds = None
        self.results_scrollbar_bounds = None
        self.category_scroll_bounds = None
        self.category_scrollbar_bounds = None
        self._category_container_geom = None
        self.download_col_resize_handles = []
        self.download_data_scroll_bounds = None
        self.download_data_scrollbar_bounds = None

        self._round_rect(1, 1, width - 2, height - 2, 10, fill=COLORS["app"], outline="#0f2538")
        self._draw_sidebar(height)

        content_x = 215
        content_y = 22
        content_w = width - content_x - 14
        right_w = 398 if content_w > 890 else 350
        gap = 12
        right_x = width - right_w - 14
        left_w = right_x - content_x - gap
        downloads_h = 226
        bottom_margin = 14

        if self.active_nav == "Налаштування":
            self.search_entry.place_forget()
            self._draw_settings(content_x + 10, content_y, left_w + right_w + gap, height - content_y - bottom_margin)
            return

        if self.active_nav == "Історія":
            self.search_entry.place_forget()
            self._draw_full_history(content_x + 10, content_y, left_w + right_w + gap, height - content_y - bottom_margin)
            return

        if self.active_nav == "Завантаження":
            self.search_entry.place_forget()
            self._draw_downloads(content_x + 10, content_y, left_w + right_w + gap, height - content_y - bottom_margin)
            return

        if self.active_nav == "Головна":
            self.search_entry.place_forget()
            self._draw_home(content_x + 10, content_y, left_w - 10, right_x, right_w, height - content_y - bottom_margin)
            return

        search_x = content_x + 10
        search_y = content_y
        left_content_w = left_w - 10
        category_y = search_y + 44 + 10
        self._draw_category_container(search_x, category_y, left_content_w)

        self._draw_sidebar(height)
        self._draw_search_bar(search_x, search_y, left_content_w)
        panel_top = category_y + self._category_container_height() + 10
        self._search_area_bottom = category_y + self._category_container_height()
        results_h = max(342, height - panel_top - downloads_h - 24)
        self._draw_results(search_x, panel_top, left_content_w, results_h)
        self._draw_downloads(search_x, panel_top + results_h + 10, left_content_w, downloads_h)
        self._draw_details(right_x, panel_top, right_w, height - panel_top - bottom_margin)
        self._draw_category_side_masks()
        self._draw_filter_button(right_x, right_w, category_y)
    def _draw_cover(self, x: float, y: float, w: float, h: float, book: dict, *, small: bool) -> None:
        self._round_rect(x, y, x + w, y + h, 4, fill=book["cover_bg"], outline="#0b111a")
        self.canvas.create_rectangle(x + 4, y + 4, x + w - 4, y + h - 4, fill=book["cover_bg"], outline="#2a3040")

        accent = book["cover_accent"]
        if book["id"] == "1984":
            title_font = "cover_small" if small else "cover"
            self._text(x + w / 2, y + h * 0.23, "1984", accent, title_font, "center")
            self.canvas.create_oval(x + w * 0.24, y + h * 0.46, x + w * 0.76, y + h * 0.68, outline="#d9c47f", width=2)
            self.canvas.create_oval(x + w * 0.44, y + h * 0.53, x + w * 0.56, y + h * 0.62, fill="#101010", outline="")
            self._text(x + w / 2, y + h - 12, "ОРВЕЛЛ", "#d4b15f", "caption", "center")
        elif book["id"] == "hobbit":
            self.canvas.create_rectangle(x + 4, y + h * 0.58, x + w - 4, y + h - 4, fill="#17352c", outline="")
            self.canvas.create_arc(x + w * 0.08, y + h * 0.16, x + w * 0.92, y + h * 0.86, start=20, extent=140, outline=accent, width=2)
            self.canvas.create_polygon(
                x + w * 0.18,
                y + h - 6,
                x + w * 0.5,
                y + h * 0.42,
                x + w * 0.82,
                y + h - 6,
                fill="#2b5b42",
                outline="",
            )
            self._text(x + w / 2, y + 10, "ГОБІТ", "#f2d17b", "caption", "center")
        elif book["id"] == "sapiens":
            self.canvas.create_rectangle(x + 5, y + 5, x + w - 5, y + h - 5, fill="#f3eadc", outline="")
            self._text(x + w / 2, y + h * 0.22, "Sapiens", accent, "caption", "center")
            self.canvas.create_oval(x + w * 0.35, y + h * 0.43, x + w * 0.65, y + h * 0.62, outline="#4f382e", width=2)
            self._text(x + w / 2, y + h - 14, "ХАРАРІ", "#4f382e", "caption", "center")
        elif book["id"] == "think-grow":
            self.canvas.create_rectangle(x + 5, y + 5, x + w - 5, y + h - 5, fill="#17110b", outline="#59451d")
            self._text(x + w / 2, y + h * 0.28, "ДУМАЙ", accent, "caption", "center")
            self._text(x + w / 2, y + h * 0.48, "І БАГАТІЙ", accent, "caption", "center")
            self.canvas.create_line(x + 12, y + h - 16, x + w - 12, y + h - 16, fill=accent)
        else:
            self.canvas.create_rectangle(x + 5, y + 5, x + w - 5, y + h - 5, fill="#191613", outline="#5c4620")
            self._text(x + w / 2, y + h * 0.28, "КОРОТКА", accent, "caption", "center")
            self._text(x + w / 2, y + h * 0.45, "ІСТОРІЯ", accent, "caption", "center")
            self.canvas.create_oval(x + w * 0.28, y + h * 0.58, x + w * 0.72, y + h * 0.82, outline=accent)

        path = book.get("cover_image")
        if path:
            from pathlib import Path
            from PIL import Image, ImageTk
            image_path = Path(__file__).resolve().parent / path
            if image_path.is_file():
                with Image.open(image_path) as source:
                    image = source.convert("RGBA").resize(
                        (max(1, round(w)), max(1, round(h))), Image.Resampling.LANCZOS
                    )
                photo = ImageTk.PhotoImage(image)
                if not hasattr(self, "_cover_refs"):
                    self._cover_refs = []
                self._cover_refs.append(photo)
                self.canvas.create_image(x, y, image=photo, anchor="nw")
            

    def _trim(self, text: str, max_width: float, font: str = "body") -> str:
        text = str(text)
        if not text:
            return text
        font_obj = self.fonts[font]
        if font_obj.measure(text) <= max_width:
            return text
        ellipsis = "..."
        if font_obj.measure(ellipsis) >= max_width:
            return ellipsis
        trimmed = text
        while len(trimmed) > 1 and font_obj.measure(trimmed + ellipsis) > max_width:
            trimmed = trimmed[:-1]
        return trimmed.rstrip() + ellipsis

    def _text_fit(
        self,
        x: float,
        y: float,
        text: str,
        fill: str,
        font: str,
        anchor: TextAnchor,
        max_width: float,
    ) -> int:
        return self._text(x, y, self._trim(text, max_width, font), fill, font, anchor)

    def _line_height(self, font: str) -> int:
        return self.fonts[font].metrics("linespace") + 2

    def _split_long_word(self, word: str, max_width: float, font: str) -> list[str]:
        if self.fonts[font].measure(word) <= max_width:
            return [word]

        chunks: list[str] = []
        chunk = ""
        for char in word:
            candidate = chunk + char
            if chunk and self.fonts[font].measure(candidate) > max_width:
                chunks.append(chunk)
                chunk = char
            else:
                chunk = candidate
        if chunk:
            chunks.append(chunk)
        return chunks

    def _wrap_text(self, text: str, max_width: float, font: str, max_lines: int | None = None) -> list[str]:
        words = str(text).split()
        if not words:
            return [""]

        lines: list[str] = []
        current = ""
        for word in words:
            for piece in self._split_long_word(word, max_width, font):
                candidate = f"{current} {piece}" if current else piece
                if current and self.fonts[font].measure(candidate) > max_width:
                    lines.append(current)
                    current = piece
                else:
                    current = candidate
        if current:
            lines.append(current)

        if max_lines is not None and len(lines) > max_lines:
            lines = lines[:max_lines]
            ellipsis = "..."
            if self.fonts[font].measure(lines[-1] + ellipsis) <= max_width:
                lines[-1] = lines[-1].rstrip() + ellipsis
            else:
                lines[-1] = self._trim(lines[-1], max_width, font)
        return lines

    def _text_block(
        self,
        x: float,
        y: float,
        text: str,
        fill: str,
        font: str,
        max_width: float,
        max_lines: int | None = None,
    ) -> float:
        lines = self._wrap_text(text, max_width, font, max_lines)
        line_height = self._line_height(font)
        self._text(x, y, "\n".join(lines), fill, font, "nw")
        return len(lines) * line_height


if __name__ == "__main__":
    BookDownloaderApp().run()
