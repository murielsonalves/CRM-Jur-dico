from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parents[1]
env = Environment(loader=FileSystemLoader(BASE_DIR / "templates"))


class DocumentService:
    def render_notificacao(self, payload: dict) -> str:
        return env.get_template("notificacao_extrajudicial.j2").render(**payload, data=date.today())

    def render_acordo(self, payload: dict) -> str:
        return env.get_template("acordo.j2").render(**payload, data=date.today())

    def render_peticao_inicial(self, payload: dict) -> str:
        return env.get_template("peticao_inicial.j2").render(**payload, data=date.today())
