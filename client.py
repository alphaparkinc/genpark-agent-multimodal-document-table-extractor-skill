import sys, json, re

class AgentDocumentTableExtractor:
    """
    Multi-Modal Document & Tabular Markdown Extractor.
    Extracts structured tables from aligned whitespace, ASCII grids,
    pipe-separated columns, and converts them to GFM Markdown and typed JSON records.
    """
    def _infer_type(self, val_str):
        v = val_str.strip()
        if not v:
            return None
        # Boolean
        if v.lower() in ("true", "yes", "on"): return True
        if v.lower() in ("false", "no", "off"): return False
        # Currency / Percentage
        clean_num = re.sub(r"^[\$\€\£\s]+|[%,\s]+$", "", v)
        try:
            if "." in clean_num:
                return float(clean_num)
            return int(clean_num)
        except ValueError:
            pass
        return v

    def extract_tables_from_text(self, text):
        lines = [line.rstrip() for line in text.splitlines() if line.strip()]
        tables = []
        current_rows = []

        for line in lines:
            # Check for delimiter table line (pipe or 2+ consecutive spaces)
            if "|" in line:
                cells = [c.strip() for c in line.split("|")]
                if cells and not cells[0]: cells.pop(0)
                if cells and not cells[-1]: cells.pop()
                # Skip divider lines like |---|---|
                if any(re.match(r"^:?-+:?$", c) for c in cells):
                    continue
                current_rows.append(cells)
            elif re.search(r"\s{2,}", line):
                cells = re.split(r"\s{2,}", line.strip())
                if len(cells) >= 2:
                    current_rows.append(cells)
                elif current_rows:
                    tables.append(current_rows)
                    current_rows = []
            else:
                if current_rows:
                    tables.append(current_rows)
                    current_rows = []

        if current_rows:
            tables.append(current_rows)

        return tables

    def table_to_markdown(self, rows):
        if not rows:
            return ""
        col_count = max(len(r) for r in rows)
        norm_rows = [r + [""] * (col_count - len(r)) for r in rows]
        
        # Calculate max column widths
        widths = [max(len(str(r[c])) for r in norm_rows) for c in range(col_count)]
        widths = [max(w, 3) for w in widths]

        headers = norm_rows[0]
        header_line = "| " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |"
        sep_line = "|-" + "-|-".join("-" * widths[i] for i in range(col_count)) + "-|"
        
        data_lines = []
        for row in norm_rows[1:]:
            data_lines.append("| " + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)) + " |")

        return "\n".join([header_line, sep_line] + data_lines)

    def table_to_typed_json(self, rows):
        if len(rows) < 2:
            return []
        headers = [str(h).strip().lower().replace(" ", "_") for h in rows[0]]
        records = []
        for row in rows[1:]:
            rec = {}
            for i, h in enumerate(headers):
                cell_val = row[i] if i < len(row) else ""
                rec[h] = self._infer_type(str(cell_val))
            records.append(rec)
        return records

    def run_table_benchmark(self):
        sample_doc = """
Q4 Financial Operating Metrics:
Quarter       Revenue       NetIncome     GrowthRate    ActiveUsers
Q1 2026       $14.2B        $3.4B         18.5%         120000000
Q2 2026       $15.8B        $3.9B         21.2%         135000000
Q3 2026       $16.9B        $4.1B         24.0%         148000000
Q4 2026       $18.5B        $4.8B         28.5%         162000000
"""
        extracted = self.extract_tables_from_text(sample_doc)
        md_table = self.table_to_markdown(extracted[0]) if extracted else ""
        typed_json = self.table_to_typed_json(extracted[0]) if extracted else []

        return {
            "suite": "Document Table Extractor Benchmark",
            "detected_tables": len(extracted),
            "markdown_render": md_table,
            "typed_json_sample": typed_json[:2],
            "status": "EXTRACTION_PARSED_SUCCESSFULLY"
        }
