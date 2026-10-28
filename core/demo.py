"""Demonstração curta, determinística, sobre o simulador original."""
from copy import deepcopy

from models.computer import Computer
from models.activities import get_task
from core.simulator import Simulator
from core.energy import cost_projection, expected_power_range
from core.recommendations import detect_anomaly


class QuickDemo:
    TASK = "Navegador + documentos"
    WASTE_W = 90.0
    SETTLE_S = 180

    def __init__(self, tariff=0.90):
        self.tariff = tariff
        self.task_ranges = get_task("leve", self.TASK)
        # Carga útil fixa: isola o efeito da intervenção, sem variar a tarefa.
        controlled = {key: (sum(value) / 2,) * 2
                      for key, value in self.task_ranges.items()}
        self.sim = Simulator(Computer("intermediario"), "leve", self.TASK,
                             controlled, tarifa_kwh=tariff)
        self.sim.advance(self.SETTLE_S, passo=2)
        self.stage = "normal"
        self.before = None
        self.after = None

    def snapshot(self):
        snap = deepcopy(self.sim.snapshot())
        expected = expected_power_range(self.sim.computer,
                                        self.task_ranges["cpu"], self.task_ranges["gpu"])
        snap["anomaly"] = detect_anomaly(snap["power"]["total_w"], expected)
        return snap

    def inject_waste(self):
        if self.stage != "normal":
            return
        self.sim.inject_waste(self.WASTE_W)
        # A trilha sem intervenção mantém o MESMO desperdício no comparativo.
        self.sim.baseline.waste_w = self.WASTE_W
        self.sim.advance(self.SETTLE_S, passo=2)
        self.before = self.snapshot()
        self.stage = "waste"

    def optimize(self):
        if self.stage != "waste":
            return
        # Decisão já implementada: remove apenas a parcela de processos extras.
        self.sim.apply_decision("verificar_processos")  # avança 20 s
        self.sim.advance(self.SETTLE_S - 20, passo=2)
        self.after = self.snapshot()
        self.stage = "optimized"

    def comparison(self):
        if self.after is None:
            return None
        before_w = self.before["power"]["total_w"]
        after_w = self.after["power"]["total_w"]
        before = cost_projection(before_w, self.tariff)["30d"]
        after = cost_projection(after_w, self.tariff)["30d"]
        return {
            "before_w": before_w, "after_w": after_w,
            "before_temp": self.before["temp"], "after_temp": self.after["temp"],
            "reduction_pct": (before_w - after_w) / before_w * 100,
            "before_month": before, "after_month": after,
            "saved_kwh": before["kwh"] - after["kwh"],
            "saved_brl": round(before["custo"] - after["custo"], 2),
        }
