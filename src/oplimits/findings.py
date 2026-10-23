"""Collected findings from model conversion and calculations (messages in Croatian)."""
import pandas as pd

INFO = "INFO"
WARNING = "UPOZORENJE"


class Findings:
    def __init__(self):
        self.rows = []

    def add(self, level, category, text, element=""):
        self.rows.append(dict(razina=level, kategorija=category, element=str(element), nalaz=text))

    def info(self, category, text, element=""):
        self.add(INFO, category, text, element)

    def warn(self, category, text, element=""):
        self.add(WARNING, category, text, element)

    def warnings(self):
        return [r for r in self.rows if r["razina"] == WARNING]

    def to_frame(self):
        return pd.DataFrame(self.rows, columns=["razina", "kategorija", "element", "nalaz"])

    def __len__(self):
        return len(self.rows)
