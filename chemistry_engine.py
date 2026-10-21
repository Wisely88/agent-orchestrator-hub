"""
Chemistry Calculation Engine (Claude 核心交付物)
负责化学分子式解析、相对分子质量高精度计算与常见方程式守恒验证。
"""

import re

ELEMENT_WEIGHTS = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "C": 12.011, "N": 14.007,
    "O": 15.999, "F": 18.998, "Ne": 20.180, "Na": 22.990, "Mg": 24.305,
    "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.065, "Cl": 35.453,
    "K": 39.098, "Ca": 40.078, "Fe": 55.845, "Cu": 63.546, "Zn": 65.380
}

def parse_formula(formula: str) -> dict:
    """
    使用栈优雅解析含括号的化学分子式，支持嵌套、系数与角标。
    例如: 'Ca(OH)2' -> {'Ca': 1, 'O': 2, 'H': 2}
    '2NaOH' -> {'Na': 2, 'O': 2, 'H': 2}
    """
    formula = formula.strip().replace("↓", "").replace("↑", "")
    coeff_match = re.match(r"^(\d+)", formula)
    coeff = int(coeff_match.group(1)) if coeff_match else 1
    formula = re.sub(r"^\d+", "", formula)

    # 栈算法解析括号
    stack = [{}]
    i = 0
    n = len(formula)

    while i < n:
        char = formula[i]

        if char == "(":
            stack.append({})
            i += 1
        elif char == ")":
            i += 1
            # 获取括号后面的数字倍数
            num_start = i
            while i < n and formula[i].isdigit():
                i += 1
            multiplier = int(formula[num_start:i]) if num_start < i else 1
            
            top = stack.pop()
            for elem, cnt in top.items():
                stack[-1][elem] = stack[-1].get(elem, 0) + cnt * multiplier
        elif char.isupper():
            # 大写字母，提取元素名 (如 Cu, O, Cl)
            elem = char
            i += 1
            if i < n and formula[i].islower():
                elem += formula[i]
                i += 1
            # 提取角标数字
            num_start = i
            while i < n and formula[i].isdigit():
                i += 1
            count = int(formula[num_start:i]) if num_start < i else 1
            stack[-1][elem] = stack[-1].get(elem, 0) + count
        else:
            i += 1

    result = stack[0]
    return {elem: cnt * coeff for elem, cnt in result.items()}

def calculate_molar_mass(formula: str) -> float:
    """计算相对分子质量"""
    counts = parse_formula(formula)
    total = 0.0
    for elem, cnt in counts.items():
        if elem in ELEMENT_WEIGHTS:
            total += ELEMENT_WEIGHTS[elem] * cnt
        else:
            raise ValueError(f"未知元素符号: {elem}")
    return round(total, 3)

def verify_equation_balance(equation: str) -> bool:
    """验证化学反应方程式配平守恒"""
    parts = equation.split("=")
    if len(parts) != 2:
        return False
    left_str, right_str = parts[0].strip(), parts[1].strip()

    left_reactants = [r.strip() for r in left_str.split("+")]
    right_products = [p.strip() for p in right_str.split("+")]

    left_atoms = {}
    for r in left_reactants:
        counts = parse_formula(r)
        for elem, cnt in counts.items():
            left_atoms[elem] = left_atoms.get(elem, 0) + cnt

    right_atoms = {}
    for p in right_products:
        counts = parse_formula(p)
        for elem, cnt in counts.items():
            right_atoms[elem] = right_atoms.get(elem, 0) + cnt

    return left_atoms == right_atoms

if __name__ == "__main__":
    print(parse_formula("Ca(OH)2"))
    print(calculate_molar_mass("Ca(OH)2"))
    print("Balance:", verify_equation_balance("2NaOH + CuSO4 = Cu(OH)2↓ + Na2SO4"))
