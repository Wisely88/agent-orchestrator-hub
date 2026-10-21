#!/usr/bin/env python3
"""
Codex 交付物：化学公式计算器自动化单测套件与沙盒回归门禁
"""

import unittest
import sys
import os

# 将父目录加入搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chemistry_engine as ce

class TestChemistryEngine(unittest.TestCase):
    def test_formula_parsing(self):
        # 简单单质与二元化合物
        self.assertEqual(ce.parse_formula("H2"), {"H": 2})
        self.assertEqual(ce.parse_formula("H2O"), {"H": 2, "O": 1})
        self.assertEqual(ce.parse_formula("CO2"), {"C": 1, "O": 2})
        # 复杂盐类与带系数
        self.assertEqual(ce.parse_formula("CuSO4"), {"Cu": 1, "S": 1, "O": 4})
        self.assertEqual(ce.parse_formula("2NaOH"), {"Na": 2, "O": 2, "H": 2})
        # 带括号基团
        self.assertEqual(ce.parse_formula("Ca(OH)2"), {"Ca": 1, "O": 2, "H": 2})

    def test_molar_mass_calculation(self):
        # H2O = 2*1.008 + 15.999 = 18.015
        self.assertAlmostEqual(ce.calculate_molar_mass("H2O"), 18.015, places=2)
        # CO2 = 12.011 + 2*15.999 = 44.009
        self.assertAlmostEqual(ce.calculate_molar_mass("CO2"), 44.009, places=2)
        # 硫酸铜 CuSO4
        self.assertAlmostEqual(ce.calculate_molar_mass("CuSO4"), 159.609, places=2)

    def test_equation_balance_verification(self):
        # 置换反应
        self.assertTrue(ce.verify_equation_balance("Fe + CuSO4 = FeSO4 + Cu"))
        # 复分解反应 (沉淀生成)
        self.assertTrue(ce.verify_equation_balance("2NaOH + CuSO4 = Cu(OH)2↓ + Na2SO4"))
        # 燃烧化合反应
        self.assertTrue(ce.verify_equation_balance("2H2 + O2 = 2H2O"))
        # 碳酸钙分解产气反应
        self.assertTrue(ce.verify_equation_balance("CaCO3 + 2HCl = CaCl2 + H2O + CO2↑"))
        # 错误方程式校验
        self.assertFalse(ce.verify_equation_balance("H2 + O2 = H2O"))

if __name__ == "__main__":
    unittest.main()
