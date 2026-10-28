import unittest
from core.demo import QuickDemo
from core.report import build_report
from core.simulator import Simulator, StressTest
from models.computer import Computer
from models.activities import get_task


class DemoTests(unittest.TestCase):
    def test_flow_and_same_workload(self):
        demo = QuickDemo()
        normal = demo.snapshot()
        self.assertFalse(normal['anomaly']['anomalo'])
        demo.optimize()
        self.assertEqual(demo.stage, 'normal')
        demo.inject_waste()
        before = demo.snapshot()
        self.assertTrue(before['anomaly']['anomalo'])
        self.assertAlmostEqual(before['power']['total_w'] - normal['power']['total_w'], 90)
        demo.optimize()
        after, result = demo.snapshot(), demo.comparison()
        self.assertFalse(after['anomaly']['anomalo'])
        self.assertEqual(after['cpu_util'], before['cpu_util'])
        self.assertEqual(after['gpu_util'], before['gpu_util'])
        self.assertLess(after['temp'], before['temp'])
        self.assertAlmostEqual(result['saved_kwh'], 90 / 1000 * 8 * 30)
        self.assertAlmostEqual(result['saved_brl'], 19.44)
        self.assertAlmostEqual(result['reduction_pct'], 90 / before['power']['total_w'] * 100)
        self.assertEqual(demo.sim.baseline.waste_w, 90)
        self.assertEqual(demo.sim.real.waste_w, 0)
        self.assertEqual(demo.sim.real.lockups + demo.sim.real.restarts, 0)
        frozen = demo.comparison()
        demo.inject_waste()
        demo.optimize()
        self.assertEqual(demo.comparison(), frozen)

    def test_tariff_reproducibility_and_reset(self):
        results = []
        for tariff in [0.9, 1.8]:
            demo = QuickDemo(tariff)
            demo.inject_waste()
            demo.optimize()
            results.append(demo.comparison())
        self.assertEqual(results[0]['before_w'], results[1]['before_w'])
        self.assertEqual(results[1]['saved_brl'], results[0]['saved_brl'] * 2)
        self.assertIsNone(QuickDemo().comparison())

    def test_legacy_simulator_report_and_stress(self):
        sim = Simulator(Computer('entrada'), 'leve', QuickDemo.TASK,
                        get_task('leve', QuickDemo.TASK))
        sim.advance(10)
        sim.inject_waste(90)
        sim.advance(2)
        self.assertTrue(sim.snapshot()['anomaly']['anomalo'])
        sim.apply_decision('verificar_processos')
        self.assertEqual(sim.real.waste_w, 0)
        self.assertIsNotNone(build_report(sim))
        test = StressTest('entrada', 'premium', (20, 20), (5, 5))
        self.assertIsNotNone(test.snapshot()['a'])
        self.assertIsNotNone(test.snapshot()['b'])
