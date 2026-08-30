from virtual_library.config import COLORS
from virtual_library.data import DOWNLOADS, SIDEBAR_ITEMS


class AppViewsMixin:

    def _draw_sidebar(self, height: float) -> None:
        sidebar_w = 195
        self.canvas.create_rectangle(0, 0, sidebar_w, height, fill=COLORS["sidebar"], outline="")
        self.canvas.create_line(sidebar_w, 0, sidebar_w, height, fill="#0f2438")

        self._round_rect(17, 19, 34, 36, 4, fill=COLORS["blue"], outline="")
        self._text(24.5, 25.5, "▥", "#d9efff", "caption", "center")
        self._text(44, 20, "BookDownloader", COLORS["text"], "brand")

        y = 64
        for icon, label in SIDEBAR_ITEMS:
            if label == "Налаштування":
                self.canvas.create_line(18, y - 12, sidebar_w - 20, y - 12, fill=COLORS["line_soft"])
            active = label == self.active_nav
            row_h = 38
            fill = COLORS["sidebar_active"] if active else COLORS["sidebar"]
            text_fill = COLORS["blue"] if active else COLORS["text_soft"]
            if active:
                self._round_rect(10, y, sidebar_w - 10, y + row_h, 5, fill=fill, outline="")
                self.canvas.create_rectangle(9, y + 4, 12, y + row_h - 4, fill=COLORS["blue"], outline="")
            self._text(26, y + row_h / 2, icon, text_fill, "body", "center")
            self._text(44, y + row_h / 2, self._trim(self._nav_label(label), sidebar_w - 56, "nav"), text_fill, "nav", "w")
            self.buttons.append(
                {"x1": 9, "y1": y, "x2": sidebar_w - 10, "y2": y + row_h, "action": "nav", "payload": label}
            )
            y += 52

        storage_y = height - 64
        self._text(21, storage_y, "Сховище", COLORS["text_soft"], "body_small")
        self._round_rect(21, storage_y + 18, 174, storage_y + 23, 3, fill="#15253a", outline="")
        self._round_rect(21, storage_y + 18, 88, storage_y + 23, 3, fill=COLORS["blue"], outline="")
        self._text(21, storage_y + 32, "18.4 ГБ / 50 ГБ", COLORS["text_soft"], "body_small")

    def _category_container_height(self) -> float:
        return 10 + 27 + 8 + 6 + 10

    def _draw_search_bar(self, x: float, y: float, left_w: float) -> None:
        search_w = min(620, max(420, left_w + 100))
        search_label = self._t("search")
        search_button_w = 36 + self.fonts["button"].measure(search_label) + 14
        search_h = 44
        self._round_rect(x, y, x + search_w + 400, y + search_h, 7, fill=COLORS["input_bg"], outline=COLORS["input_line"])
        self.search_entry.place(x=x + 16, y=y + 11, width=search_w + 275, height=22)
        self._button(
            x + search_w + 300,
            y + 1,
            x + search_w + 400,
            y + search_h - 1,
            self._t("search"),
            "search",
            fill=COLORS["blue"],
            active_fill=COLORS["blue_dark"],
            radius=7,
            font="button",
            icon="⌕",
        )

    def _draw_filter_button(self, right_x: float, right_w: float, category_y: float) -> None:
        filter_label = "Фільтри" if not self.filter_open else "Фільтри: відкрито"
        filter_h = 34
        container_h = self._category_container_height()
        filter_y = category_y + (container_h - filter_h) / 2
        self._button(
            right_x - 150,
            filter_y,
            right_x + min(-20, right_w - 16),
            filter_y + filter_h,
            filter_label,
            "filter",
            fill=COLORS["panel_alt"],
            active_fill=COLORS["panel_soft"],
            radius=7,
            icon="≡",
        )

    def _draw_category_side_masks(self) -> None:
        if not self._category_container_geom:
            return

        geom = self._category_container_geom
        side_w = 29
        app = COLORS["app"]
        panel = COLORS["panel"]
        line = COLORS["line"]
        chip_y = geom["chip_y"]
        chip_y2 = chip_y + geom["chip_h"] + 1

        self.canvas.create_rectangle(
            geom["x"] - side_w,
            chip_y,
            geom["x"],
            chip_y2,
            fill=app,
            outline="",
        )
        self.canvas.create_rectangle(
            geom["x"] + geom["w"] - 150,
            chip_y,
            geom["x"] + geom["w"] + side_w - 50,
            chip_y2,
            fill=panel,
            outline="",
        )
        self.canvas.create_rectangle(
            geom["x"] + geom["w"] - 145 ,
            chip_y - 10,
            geom["x"] + geom["w"] - 144,
            chip_y2 + 24,
            fill=line,
            outline="",
        )

    def _draw_category_container(self, x: float, y: float, w: float) -> float:
        pad_x = 12
        pad_y = 10
        chip_h = 27
        scroll_h = 6
        scroll_gap = 8
        container_h = self._category_container_height()

        self._round_rect(x, y, x + w, y + container_h, 8, fill=COLORS["panel"], outline=COLORS["line_soft"])

        viewport_x = x + pad_x
        viewport_w = w - pad_x * 2
        chip_y = y + pad_y

        chips, total_w = self._category_chips_metrics()
        max_scroll = max(0, int(total_w - viewport_w + 140))
        self.category_scroll = max(0, min(self.category_scroll, max_scroll))
        has_scroll = max_scroll > 0
        self.category_scroll_bounds = (x, y, x + w, y + container_h, max_scroll)
        self._category_container_geom = {
            "x": x,
            "y": y,
            "w": w,
            "h": container_h,
            "viewport_x": viewport_x,
            "viewport_w": viewport_w,
            "chip_y": chip_y,
            "chip_h": chip_h,
        }

        chip_x = viewport_x - self.category_scroll
        for category, chip_w in chips:
            chip_right = chip_x + chip_w
            if chip_right > viewport_x and chip_x < viewport_x + viewport_w - 120:
                active = self.active_category == category
                fill = COLORS["blue"] if active else COLORS["panel_alt"]
                text_fill = COLORS["text"] if active else COLORS["text_soft"]
                self._button(
                    chip_x,
                    chip_y,
                    chip_x + chip_w,
                    chip_y + chip_h,
                    category,
                    "category",
                    category,
                    fill=fill,
                    active_fill=COLORS["blue_dark"] if active else COLORS["panel_soft"],
                    text_fill=text_fill,
                    radius=7,
                    font="body_small",
                )
            chip_x += chip_w + 8

        if has_scroll:
            track_x1 = viewport_x
            track_x2 = viewport_x + viewport_w - 150
            track_y1 = y + container_h - pad_y - scroll_h
            track_y2 = track_y1 + scroll_h
            track_w = max(1, track_x2 - track_x1)
            thumb_w = max(28, track_w * viewport_w / total_w - 100)
            thumb_x = track_x1 + (track_w - thumb_w) * self.category_scroll / max(1, max_scroll)
            self._round_rect(track_x1, track_y1, track_x2, track_y2, 3, fill=COLORS["line_soft"], outline="")
            self._round_rect(thumb_x, track_y1, thumb_x + thumb_w, track_y2, 3, fill=COLORS["blue"], outline="")
            self.category_scrollbar_bounds = (
                track_x1,
                track_y1 - 4,
                track_x2,
                track_y2 + 4,
                max_scroll,
                thumb_x,
                thumb_w,
                track_w,
            )

        return y + container_h

    def _draw_results(self, x: float, y: float, w: float, h: float) -> None:
        self._round_rect(x, y, x + w, y + h, 8, fill=COLORS["panel"], outline=COLORS["line_soft"])
        self._text(x + 14, y + 14, "Результати пошуку", COLORS["text"], "section")

        books = self._visible_books()
        selected_ids = {book["id"] for book in books}
        if books and self.selected_book_id not in selected_ids:
            self.selected_book_id = books[0]["id"]

        row_x = x + 14
        row_y = y + 40
        row_h = 87
        max_rows = max(1, int((h - 50) // row_h))
        max_scroll = max(0, len(books) - max_rows)
        self.results_scroll = max(0, min(self.results_scroll, max_scroll))
        has_scroll = max_scroll > 0
        row_w = w - (42 if has_scroll else 28)
        self.results_scroll_bounds = (x, y, x + w, y + h, max_scroll)
        if not books:
            self._text(
                x + w / 2,
                y + h / 2,
                "Нічого не знайдено",
                COLORS["text_soft"],
                "title",
                "center",
            )
            self._text(
                x + w / 2,
                y + h / 2 + 24,
                "Спробуйте іншу назву, автора або ISBN.",
                COLORS["text_muted"],
                "body_small",
                "center",
            )
            return

        visible_books = books[self.results_scroll : self.results_scroll + max_rows]
        for index, book in enumerate(visible_books):
            top = row_y + index * row_h
            active = book["id"] == self.selected_book_id
            fill = COLORS["panel_alt"] if active else COLORS["panel"]
            if active:
                self._round_rect(row_x, top, row_x + row_w, top + row_h - 9, 6, fill=fill, outline="")
            else:
                self.canvas.create_line(row_x, top + row_h - 8, row_x + row_w, top + row_h - 8, fill=COLORS["line_soft"])
            btn_w = 112
            btn_x = row_x + row_w - btn_w - 22
            self.buttons.append(
                {
                    "x1": row_x,
                    "y1": top,
                    "x2": btn_x - 8,
                    "y2": top + row_h - 9,
                    "action": "select_book",
                    "payload": book["id"],
                }
            )
            self._draw_cover(row_x + 8, top + 9, 52, 70, book, small=True)

            text_x = row_x + 74
            text_max_w = max(80, btn_x - text_x - 8)
            self._text_fit(text_x, top + 11, book["title"], COLORS["text"], "title", "w", text_max_w)
            self._text_fit(text_x, top + 35, book["author"], COLORS["text_soft"], "body_small", "w", text_max_w)
            meta = f"{book['meta']}  •  {book['pages']} стор."
            self._text_fit(text_x, top + 56, meta, COLORS["text_muted"], "body_small", "w", text_max_w)
            self._text_fit(text_x, top + 72, f"ISBN: {book['isbn']}", COLORS["text_muted"], "caption", "w", text_max_w)

            self._button(
                btn_x,
                top + 18,
                btn_x + btn_w,
                top + 52,
                "Завантажити",
                "download",
                book["id"],
                fill=COLORS["panel_soft"],
                active_fill="#1c334d",
                radius=6,
                icon="⇩",
            )
            self._text_fit(
                btn_x + (btn_w / 2),
                top + 66,
                f"{book['format']}  •  {book['size']}",
                COLORS["text_muted"],
                "caption",
                "center",
                btn_w - 8,
            )

        if has_scroll:
            track_x = x + w - 17
            track_y1 = row_y
            track_y2 = y + h - 14
            track_h = max(1, track_y2 - track_y1)
            thumb_h = max(28, track_h * max_rows / len(books))
            thumb_y = track_y1 + (track_h - thumb_h) * self.results_scroll / max(1, max_scroll)
            self._round_rect(track_x, track_y1, track_x + 6, track_y2, 3, fill=COLORS["line_soft"], outline="")
            self._round_rect(track_x, thumb_y, track_x + 6, thumb_y + thumb_h, 3, fill=COLORS["blue"], outline="")
            self.results_scrollbar_bounds = (
                track_x - 8,
                track_y1,
                track_x + 14,
                track_y2,
                max_scroll,
                thumb_y,
                thumb_h,
                track_h,
            )

    def _draw_downloads(self, x: float, y: float, w: float, h: float) -> None:
        self._round_rect(x, y, x + w, y + h, 8, fill=COLORS["panel"], outline=COLORS["line_soft"])
        self._text(x + 14, y + 14, self._t("download_history"), COLORS["text"], "section")
        history_text = self._t("view_all_history")
        history_label = self.fonts["body_small"].measure(history_text)
        history_x2 = x + w - 14
        history_x1 = history_x2 - history_label
        self._text(history_x2, y + 15, history_text, COLORS["blue"], "body_small", "ne")
        self.buttons.append(
            {
                "x1": history_x1 - 4,
                "y1": y + 8,
                "x2": history_x2 + 4,
                "y2": y + 28,
                "action": "show_history",
                "payload": None,
            }
        )

        items = DOWNLOADS if h > 180 else DOWNLOADS[:4]
        self._draw_download_preview_rows(x + 14, y + 38, w - 28, h - 50, items)

    def _download_preview_row_height(self, book: dict, title_col_w: float) -> int:
        title_lines = self._wrap_text(book["title"], title_col_w - 4, "body_small")
        author_lines = self._wrap_text(book["author"], title_col_w - 4, "caption")[:2]
        title_lh = self._line_height("body_small")
        author_lh = self._line_height("caption")
        return max(54, int(6 + len(title_lines) * title_lh + 2 + len(author_lines) * author_lh + 8))

    def _download_data_content_width(self) -> float:
        gap = 8
        return (
            self.download_col_status_w
            + gap
            + self.download_col_date_w
            + gap
            + self.download_col_size_w
            + gap
            + 56
        )

    def _download_data_columns_at(self, data_x: float) -> dict[str, float | int]:
        gap = 8
        actions_w = 56
        status_w = self.download_col_status_w
        date_w = self.download_col_date_w
        size_w = self.download_col_size_w
        status_x1 = data_x
        date_x1 = status_x1 + status_w + gap
        size_x1 = date_x1 + date_w + gap
        actions_x1 = size_x1 + size_w + gap
        return {
            "status_x1": status_x1,
            "status_w": status_w,
            "date_x1": date_x1,
            "date_w": date_w,
            "size_x1": size_x1,
            "size_w": size_w,
            "actions_x1": actions_x1,
            "actions_w": actions_w,
            "content_w": actions_x1 + actions_w - data_x,
        }

    def _download_preview_title_width(self, items: list[dict], panel_w: float) -> float:
        if not items:
            return 120
        longest = max(
            self.fonts["body_small"].measure(self._book_by_id(item["book_id"])["title"]) for item in items
        )
        return max(100, min(longest + 10, int(panel_w * 0.48)))

    def _draw_download_preview_rows(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        items: list[dict],
    ) -> None:
        if not items:
            return

        cover_w = 44
        title_x = x + cover_w
        title_col_w = self._download_preview_title_width(items, w)
        title_block_end = title_x + title_col_w
        title_data_gap = 20
        data_content_w = self._download_data_content_width()
        data_viewport_w = max(100, x + w - title_block_end - title_data_gap)
        data_viewport_x = x + w - data_viewport_w
        if data_viewport_x < title_block_end + title_data_gap:
            data_viewport_x = title_block_end + title_data_gap
            data_viewport_w = max(80, x + w - data_viewport_x)
        max_scroll = max(0, int(data_content_w - data_viewport_w))
        self.download_data_scroll = max(0, min(self.download_data_scroll, max_scroll))
        has_h_scroll = max_scroll > 0
        scroll_bar_h = 8 if has_h_scroll else 0
        self.download_data_scroll_bounds = (
            data_viewport_x,
            y,
            data_viewport_x + data_viewport_w,
            y + h,
            max_scroll,
        )

        row_y = y
        scroll = self.download_data_scroll
        title_lh = self._line_height("body_small")
        for index, item in enumerate(items):
            book = self._book_by_id(item["book_id"])
            is_done = item["progress"] >= 100
            row_h = self._download_preview_row_height(book, title_col_w)
            if row_y + row_h > y + h - scroll_bar_h:
                break
            top = row_y

            if index > 0:
                self.canvas.create_line(x, top - 3, x + w, top - 3, fill=COLORS["line_soft"])

            self._draw_cover(x + 8, top + max(4, (row_h - 38) / 2), 28, 38, book, small=True)
            title_lines = self._wrap_text(book["title"], title_col_w - 4, "body_small")
            for line_i, line in enumerate(title_lines):
                self._text(title_x, top + 6 + line_i * title_lh, line, COLORS["text"], "body_small", "nw")
            author_y = top + 6 + len(title_lines) * title_lh + 2
            author_lines = self._wrap_text(book["author"], title_col_w - 4, "caption")[:2]
            author_lh = self._line_height("caption")
            for line_i, line in enumerate(author_lines):
                self._text(title_x, author_y + line_i * author_lh, line, COLORS["text_muted"], "caption", "nw")
            self._draw_download_data_row(
                item,
                book,
                data_viewport_x,
                data_viewport_w,
                data_content_w,
                scroll,
                top,
                row_h,
                is_done,
                x + w,
            )
            self.canvas.create_rectangle(
                x,
                top,
                data_viewport_x,
                top + row_h,
                fill=COLORS["panel"],
                outline="",
            )
            self._draw_cover(x + 8, top + max(4, (row_h - 38) / 2), 28, 38, book, small=True)
            for line_i, line in enumerate(title_lines):
                self._text(title_x, top + 6 + line_i * title_lh, line, COLORS["text"], "body_small", "nw")
            for line_i, line in enumerate(author_lines):
                self._text(title_x, author_y + line_i * author_lh, line, COLORS["text_muted"], "caption", "nw")
            row_y += row_h

        if row_y > y:
            self.canvas.create_line(
                data_viewport_x,
                y,
                data_viewport_x,
                min(row_y, y + h - scroll_bar_h),
                fill=COLORS["line_soft"],
            )

        if has_h_scroll:
            track_x1 = data_viewport_x
            track_x2 = data_viewport_x + data_viewport_w
            track_y1 = y + h - scroll_bar_h - 2
            track_y2 = track_y1 + scroll_bar_h
            track_w = max(1, track_x2 - track_x1)
            thumb_w = max(28, track_w * data_viewport_w / data_content_w)
            thumb_x = track_x1 + (track_w - thumb_w) * self.download_data_scroll / max(1, max_scroll)
            self._round_rect(track_x1, track_y1, track_x2, track_y2, 3, fill=COLORS["line_soft"], outline="")
            self._round_rect(thumb_x, track_y1, thumb_x + thumb_w, track_y2, 3, fill=COLORS["blue"], outline="")
            self.download_data_scrollbar_bounds = (
                track_x1,
                track_y1 - 4,
                track_x2,
                track_y2 + 4,
                max_scroll,
                thumb_x,
                thumb_w,
                track_w,
            )

    def _draw_download_data_row(
        self,
        item: dict,
        book: dict,
        viewport_x: float,
        viewport_w: float,
        content_w: float,
        scroll: float,
        top: float,
        row_h: float,
        is_done: bool,
        panel_right: float,
    ) -> None:
        data_x = viewport_x - scroll
        cols = self._download_data_columns_at(data_x)
        data_right = data_x + content_w

        if data_right > viewport_x and data_x < viewport_x + viewport_w:
            status_color = COLORS["text_soft"] if is_done else COLORS["blue"]
            status_y = top + (row_h / 2)
            if cols["status_x1"] + cols["status_w"] > viewport_x and cols["status_x1"] < viewport_x + viewport_w:
                self._text(cols["status_x1"], status_y, "●", status_color, "body_small", "w")
                self._text_fit(
                    cols["status_x1"] + 14,
                    status_y,
                    item["status"],
                    status_color,
                    "caption",
                    "w",
                    cols["status_w"] - 18,
                )

            if is_done and item.get("date"):
                if cols["date_x1"] + cols["date_w"] > viewport_x and cols["date_x1"] < viewport_x + viewport_w:
                    self._text_fit(
                        cols["date_x1"],
                        status_y,
                        item["date"],
                        COLORS["text_muted"],
                        "caption",
                        "w",
                        cols["date_w"],
                    )

            size_x = cols["size_x1"] + cols["size_w"]
            if cols["size_x1"] < viewport_x + viewport_w and size_x > viewport_x:
                self._text_fit(
                    size_x,
                    top + 8,
                    item["size"],
                    COLORS["text_muted"],
                    "caption",
                    "e",
                    cols["size_w"],
                )

            if not is_done:
                bar_x1 = cols["status_x1"] + 14
                if bar_x1 + 120 > viewport_x and bar_x1 < viewport_x + viewport_w:
                    self._round_rect(bar_x1, top + row_h - 16, bar_x1 + 92, top + row_h - 12, 3, fill="#132741", outline="")
                    progress_w = 92 * item["progress"] / 100
                    self._round_rect(bar_x1, top + row_h - 16, bar_x1 + progress_w, top + row_h - 12, 3, fill=COLORS["blue"], outline="")
                    self._text(bar_x1 + 98, top + 8, f"{item['progress']}%", COLORS["text_muted"], "caption")

            actions_x1 = cols["actions_x1"]
            if actions_x1 + cols["actions_w"] > viewport_x and actions_x1 < viewport_x + viewport_w:
                btn_x1 = max(viewport_x, actions_x1)
                btn_x2 = min(viewport_x + viewport_w, actions_x1 + cols["actions_w"])
                self._text(actions_x1 + 8, top + row_h / 2, "□", COLORS["text_muted"], "body_small", "center")
                pause_or_close = "Ⅱ" if not is_done else "×"
                self._text(actions_x1 + 40, top + row_h / 2, pause_or_close, COLORS["text_muted"], "body", "center")
                self.buttons.append(
                    {
                        "x1": btn_x1,
                        "y1": top,
                        "x2": btn_x2,
                        "y2": top + row_h - 4,
                        "action": "remove_download",
                        "payload": book["id"],
                    }
                )

        if viewport_x + viewport_w < panel_right:
            self.canvas.create_rectangle(
                viewport_x + viewport_w,
                top,
                panel_right,
                top + row_h,
                fill=COLORS["panel"],
                outline="",
            )

    def _download_columns(self, x: float, w: float) -> dict[str, float | int]:
        actions_w = 56
        gap = 8
        size_w = self.download_col_size_w
        date_w = self.download_col_date_w
        status_w = self.download_col_status_w
        right = x + w
        size_x2 = right - actions_w
        size_x1 = size_x2 - size_w
        date_x2 = size_x1 - gap
        date_x1 = date_x2 - date_w
        status_x2 = date_x1 - gap
        status_x1 = status_x2 - status_w
        text_start = x + 47
        text_max = max(60, status_x1 - text_start - 8)
        return {
            "text_start": text_start,
            "text_max": text_max,
            "status_x1": status_x1,
            "status_w": status_w,
            "date_x1": date_x1,
            "date_w": date_w,
            "size_x1": size_x1,
            "size_w": size_w,
            "actions_x1": size_x2,
        }

    def _draw_download_table_header(self, x: float, y: float, w: float) -> None:
        cols = self._download_columns(x, w)
        self._text(cols["status_x1"], y + 2, "Статус", COLORS["text_muted"], "caption")
        self._text(cols["date_x1"], y + 2, "Дата", COLORS["text_muted"], "caption")
        self._text(cols["size_x1"], y + 2, "Розмір", COLORS["text_muted"], "caption")
        self.canvas.create_line(x, y + 18, x + w, y + 18, fill=COLORS["line_soft"])

        gap = 8
        boundaries = [
            (cols["date_x1"] - gap // 2, "status", "date", 72, 80),
            (cols["size_x1"] - gap // 2, "date", "size", 80, 56),
        ]
        for boundary, col_a, col_b, min_a, min_b in boundaries:
            handle_half = 4
            self.canvas.create_line(boundary, y, boundary, y + 18, fill=COLORS["line"], width=1)
            self.download_col_resize_handles.append(
                {
                    "x1": boundary - handle_half,
                    "y1": y,
                    "x2": boundary + handle_half,
                    "y2": y + 20,
                    "col_a": col_a,
                    "col_b": col_b,
                    "min_a": min_a,
                    "min_b": min_b,
                }
            )

    def _draw_download_rows(
        self,
        x: float,
        y: float,
        w: float,
        _h: float,
        items: list[dict],
        *,
        table_mode: bool = False,
    ) -> None:
        row_y = y
        compact = w < 760 and not table_mode
        row_h = 54 if compact else 44
        cols = self._download_columns(x, w)
        for index, item in enumerate(items):
            book = self._book_by_id(item["book_id"])
            top = row_y + index * row_h
            if index > 0:
                self.canvas.create_line(x, top - 3, x + w, top - 3, fill=COLORS["line_soft"])

            self._draw_cover(x + 8, top + (6 if compact else 0), 28, 38, book, small=True)
            is_done = item["progress"] >= 100

            if compact:
                self._text_fit(
                    cols["text_start"],
                    top + 4,
                    book["title"],
                    COLORS["text"],
                    "body_small",
                    "w",
                    cols["text_max"],
                )
                secondary = book["author"]
                self._text_fit(
                    cols["text_start"],
                    top + 22,
                    secondary,
                    COLORS["text_muted"],
                    "caption",
                    "w",
                    cols["text_max"],
                )
                self._text_fit(
                    cols["size_x1"] + cols["size_w"],
                    top + 4,
                    item["size"],
                    COLORS["text_muted"],
                    "caption",
                    "e",
                    cols["size_w"],
                )
                status_color = COLORS["text_soft"] if is_done else COLORS["blue"]
                self._text(cols["status_x1"], top + 22, "●", status_color, "body_small", "w")
                self._text_fit(
                    cols["status_x1"] + 14,
                    top + 22,
                    item["status"],
                    status_color,
                    "caption",
                    "w",
                    cols["status_w"] - 18,
                )
                if is_done and item.get("date"):
                    self._text_fit(
                        cols["date_x1"],
                        top + 22,
                        item["date"],
                        COLORS["text_muted"],
                        "caption",
                        "w",
                        cols["date_w"],
                    )
            else:
                self._text_fit(
                    cols["text_start"],
                    top + 2,
                    book["title"],
                    COLORS["text"],
                    "body_small",
                    "w",
                    cols["text_max"],
                )
                self._text_fit(
                    cols["text_start"],
                    top + 20,
                    book["author"],
                    COLORS["text_muted"],
                    "caption",
                    "w",
                    cols["text_max"],
                )
                status_color = COLORS["text_soft"] if is_done else COLORS["blue"]
                self._text(cols["status_x1"], top + 16, "●", status_color, "body_small", "w")
                self._text_fit(
                    cols["status_x1"] + 14,
                    top + 8,
                    item["status"],
                    status_color,
                    "caption",
                    "w",
                    cols["status_w"] - 18,
                )
                if is_done and item.get("date"):
                    self._text_fit(
                        cols["date_x1"],
                        top + (10 if table_mode else 12),
                        item["date"],
                        COLORS["text_soft"],
                        "body_small" if table_mode else "caption",
                        "w",
                        cols["date_w"],
                    )
                self._text_fit(
                    cols["size_x1"] + cols["size_w"],
                    top + 12,
                    item["size"],
                    COLORS["text_muted"],
                    "caption",
                    "e",
                    cols["size_w"],
                )

            if not is_done:
                bar_x1 = cols["status_x1"] + 14
                self._round_rect(bar_x1, top + 27, bar_x1 + 92, top + 31, 3, fill="#132741", outline="")
                progress_w = 92 * item["progress"] / 100
                self._round_rect(bar_x1, top + 27, bar_x1 + progress_w, top + 31, 3, fill=COLORS["blue"], outline="")
                self._text(bar_x1 + 98, top + 8, f"{item['progress']}%", COLORS["text_muted"], "caption")

            self._text(x + w - 58, top + 16, "□", COLORS["text_muted"], "body_small", "center")
            pause_or_close = "Ⅱ" if not is_done else "×"
            self._text(x + w - 25, top + 16, pause_or_close, COLORS["text_muted"], "body", "center")
            self.buttons.append(
                {
                    "x1": x + w - 28,
                    "y1": top,
                    "x2": x + w - 4,
                    "y2": top + 36,
                    "action": "remove_download",
                    "payload": book["id"],
                }
            )

    def _draw_details(self, x: float, y: float, w: float, h: float) -> None:
        self._round_rect(x, y, x + w, y + h, 8, fill=COLORS["panel"], outline=COLORS["line_soft"])
        book = self._book_by_id(self.selected_book_id)

        cover_x = x + 20
        cover_y = y + 24
        self._draw_cover(cover_x, cover_y, 120, 180, book, small=False)

        info_x = cover_x + 140
        info_max_w = max(80, x + w - 20 - info_x)
        self._text_fit(info_x, cover_y + 6, book["title"], COLORS["text"], "detail_title", "w", info_max_w)
        detail_lines = [
            book["author"],
            book["meta"],
            f"Мова: {book['language']}",
            f"Формат: {book['format']}",
            f"Розмір: {book['size']}",
            f"Сторінок: {book['pages']}",
            f"ISBN: {book['isbn']}",
        ]
        detail_y = cover_y + 48
        detail_gap = 16
        for i, line in enumerate(detail_lines):
            self._text_fit(info_x, detail_y + i * detail_gap, line, COLORS["text_soft"], "body_small", "w", info_max_w)

        self._text(info_x, cover_y + 150, "★★★★★", COLORS["yellow"], "body")
        self._text_fit(
            info_x,
            cover_y + 186,
            f"{book['rating']} ({book['reviews']} оцінок)",
            COLORS["text_soft"],
            "body_small",
            "w",
            info_max_w,
        )

        action_y = cover_y + 228
        bookmarked = book["id"] in self.bookmarks
        favorited = book["id"] in self.favorites
        self._button(
            x + 20,
            action_y,
            x + w - 148,
            action_y + 38,
            "Завантажити",
            "download",
            book["id"],
            fill=COLORS["blue"],
            active_fill=COLORS["blue_dark"],
            radius=6,
            icon="⇩",
        )
        self._button(
            x + w - 136,
            action_y,
            x + w - 82,
            action_y + 38,
            "▣" if bookmarked else "□",
            "bookmark",
            book["id"],
            fill=COLORS["panel_soft"],
            active_fill="#1c334d",
            radius=6,
        )
        self._button(
            x + w - 70,
            action_y,
            x + w - 16,
            action_y + 38,
            "♥" if favorited else "♡",
            "favorite",
            book["id"],
            fill=COLORS["panel_soft"],
            active_fill="#1c334d",
            radius=6,
            text_fill=COLORS["danger"] if favorited else COLORS["text_soft"],
        )

        desc_y = action_y + 66
        self._text(x + 20, desc_y, "Опис", COLORS["text"], "section")
        description = book["description"]
        if not self.description_expanded:
            self._text_fit(
                x + 20,
                desc_y + 34,
                description,
                COLORS["text_soft"],
                "body_small",
                "w",
                w - 40,
            )
        else:
            self._text_block(x + 20, desc_y + 34, description, COLORS["text_soft"], "body_small", w - 40, max_lines=4)
        more_label = "Показати менше  ⌃" if self.description_expanded else "Показати більше  ⌄"
        self._text(x + 20, desc_y + 100, more_label, COLORS["blue"], "body_small")
        self.buttons.append(
            {
                "x1": x + 20,
                "y1": desc_y + 94,
                "x2": x + 180,
                "y2": desc_y + 118,
                "action": "toggle_description",
                "payload": None,
            }
        )

        line_y = desc_y + 138
        self.canvas.create_line(x + 20, line_y, x + w - 20, line_y, fill=COLORS["line_soft"])

        info_y = line_y + 22
        self._text(x + 20, info_y, "Інформація про файл", COLORS["text"], "section")
        rows = [
            ("Формат", book["format"]),
            ("Розмір файлу", book["size"]),
            ("Дата публікації", book["date"]),
            ("Видавництво", book["publisher"]),
        ]
        download_item = next((item for item in DOWNLOADS if item["book_id"] == book["id"]), None)
        if download_item and download_item.get("file_path"):
            rows.append(("Шлях до файлу", download_item["file_path"]))
        row_gap = 26
        max_rows = max(0, int((y + h - 20 - (info_y + 42)) // row_gap) + 1)
        for i, (label, value) in enumerate(rows[:max_rows]):
            row_y = info_y + 42 + i * row_gap
            label_max_w = max(90, min(w * 0.38, 150))
            value_max_w = max(80, w - 56 - label_max_w)
            self._text_fit(x + 20, row_y, label, COLORS["text_muted"], "body_small", "w", label_max_w)
            self._text_fit(x + w - 20, row_y, value, COLORS["text_soft"], "body_small", "ne", value_max_w)

        if self.filter_open:
            self._draw_filter_popover(x - 170, y + 76)

    def _draw_filter_popover(self, x: float, y: float) -> None:
        self._round_rect(x, y, x + 150, y + 116, 8, fill="#0d1827", outline=COLORS["line"])
        self._text(x + 12, y + 12, "Швидкі фільтри", COLORS["text"], "section")
        options = [
            ("EPUB", "format:EPUB", 42),
            ("Українська мова", "lang:Українська", 65),
            ("4+ зірки", "rating:4", 88),
        ]
        for label, payload, row_y in options:
            active = (
                (payload == "format:EPUB" and self.filter_format == "EPUB")
                or (payload == "lang:Українська" and self.filter_language == "Українська")
                or (payload == "rating:4" and self.filter_rating == "4")
            )
            fill = COLORS["blue"] if active else COLORS["text_soft"]
            self._text_fit(x + 12, y + row_y, label, fill, "body_small", "w", 126)
            self.buttons.append(
                {
                    "x1": x + 8,
                    "y1": y + row_y - 8,
                    "x2": x + 142,
                    "y2": y + row_y + 14,
                    "action": "filter_option",
                    "payload": payload,
                }
            )

    def _draw_home(self, x: float, y: float, left_w: float, right_x: float, right_w: float, h: float) -> None:
        self._round_rect(x, y, x + left_w, y + h, 8, fill=COLORS["panel"], outline=COLORS["line_soft"])
        self._text_fit(x + 20, y + 24, "Ласкаво просимо до BookDownloader", COLORS["text"], "detail_title", "w", left_w - 40)
        self._text_fit(
            x + 20,
            y + 72,
            "Оберіть розділ зліва або перейдіть до пошуку книг.",
            COLORS["text_soft"],
            "body",
            "w",
            left_w - 40,
        )
        stats_y = y + 120
        self._text(x + 20, stats_y, f"Книг у каталозі: {len(BOOKS)}", COLORS["text_soft"], "body_small")
        self._text(x + 20, stats_y + 24, f"Завантажень: {len(DOWNLOADS)}", COLORS["text_soft"], "body_small")
        self._text(x + 20, stats_y + 48, f"У бібліотеці: {len(self._library_books())}", COLORS["text_soft"], "body_small")
        self._text(x + 20, stats_y + 72, f"В обраному: {len(self.favorites)}", COLORS["text_soft"], "body_small")
        self._button(
            x + 20,
            stats_y + 110,
            x + 180,
            stats_y + 146,
            "Перейти до пошуку",
            "nav",
            "Пошук книг",
            fill=COLORS["blue"],
            active_fill=COLORS["blue_dark"],
            radius=6,
        )
        self._draw_details(right_x, y, right_w, h)

    def _draw_full_history(self, x: float, y: float, w: float, h: float) -> None:
        self._round_rect(x, y, x + w, y + h, 8, fill=COLORS["panel"], outline=COLORS["line_soft"])
        self._text(x + 14, y + 14, self._t("full_history"), COLORS["text"], "section")
        table_x = x + 14
        table_w = w - 28
        header_y = y + 40
        rows_y = y + 62
        self._draw_download_table_header(table_x, header_y, table_w)
        self._draw_download_rows(table_x, rows_y, table_w, h - 76, DOWNLOADS, table_mode=True)

    def _draw_settings(self, x: float, y: float, w: float, h: float) -> None:
        self._round_rect(x, y, x + w, y + h, 8, fill=COLORS["panel"], outline=COLORS["line_soft"])
        self._text(x + 20, y + 24, self._t("settings_title"), COLORS["text"], "detail_title")

        self._text(x + 20, y + 84, self._t("interface_language"), COLORS["text_soft"], "section")
        lang_y = y + 118
        uk_active = self.interface_language == "uk"
        en_active = self.interface_language == "en"
        self._button(
            x + 20,
            lang_y,
            x + 150,
            lang_y + 36,
            "Українська",
            "set_language",
            "uk",
            fill=COLORS["blue"] if uk_active else COLORS["panel_soft"],
            active_fill=COLORS["blue_dark"] if uk_active else "#1c334d",
            radius=6,
        )
        self._button(
            x + 162,
            lang_y,
            x + 292,
            lang_y + 36,
            "English",
            "set_language",
            "en",
            fill=COLORS["blue"] if en_active else COLORS["panel_soft"],
            active_fill=COLORS["blue_dark"] if en_active else "#1c334d",
            radius=6,
        )

        self._text(x + 20, y + 188, self._t("theme"), COLORS["text_soft"], "section")
        theme_y = y + 222
        dark_active = self.theme_mode == "dark"
        light_active = self.theme_mode == "light"
        self._button(
            x + 20,
            theme_y,
            x + 150,
            theme_y + 36,
            self._t("dark_theme"),
            "set_theme",
            "dark",
            fill=COLORS["blue"] if dark_active else COLORS["panel_soft"],
            active_fill=COLORS["blue_dark"] if dark_active else "#1c334d",
            radius=6,
        )
        self._button(
            x + 162,
            theme_y,
            x + 292,
            theme_y + 36,
            self._t("light_theme"),
            "set_theme",
            "light",
            fill=COLORS["blue"] if light_active else COLORS["panel_soft"],
            active_fill=COLORS["blue_dark"] if light_active else "#1c334d",
            radius=6,
        )

        self._text(x + 20, y + 288, self._t("font_size"), COLORS["text_soft"], "section")
        font_y = y + 322
        small_active = self.font_size == "small"
        medium_active = self.font_size == "medium"
        large_active = self.font_size == "large"
        self._button(
            x + 20,
            font_y,
            x + 100,
            font_y + 36,
            self._t("small"),
            "set_font_size",
            "small",
            fill=COLORS["blue"] if small_active else COLORS["panel_soft"],
            active_fill=COLORS["blue_dark"] if small_active else "#1c334d",
            radius=6,
        )

        self._button(
            x + 120,
            font_y,
            x + 200,
            font_y + 36,
            self._t("medium"),
            "set_font_size",
            "medium",
            fill=COLORS["blue"] if medium_active else COLORS["panel_soft"],
            active_fill=COLORS["blue_dark"] if medium_active else "#1c334d",
            radius=6,
        )

        self._button(
            x + 224,
            font_y,
            x + 304,
            font_y + 36,
            self._t("large"),
            "set_font_size",
            "large",
            fill=COLORS["blue"] if large_active else COLORS["panel_soft"],
            active_fill=COLORS["blue_dark"] if large_active else "#1c334d",
            radius=6,
        )

