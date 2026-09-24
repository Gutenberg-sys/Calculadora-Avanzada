"""
Calculadora Avanzada en Python
==============================
"""

import ast
import operator
import math
import cmath


class ErrorCalculadora(Exception):
    """Excepción personalizada para errores de la calculadora."""
    pass


class CalculadoraAvanzada:

    OPERADORES_BINARIOS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }


    OPERADORES_UNARIOS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }


    FUNCIONES = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "log": math.log,       # log(x) o log(x, base)
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "factorial": lambda x: math.factorial(int(x)),
        "abs": abs,
        "ceil": math.ceil,
        "floor": math.floor,
        "round": round,
        "degrees": math.degrees,
        "radians": math.radians,
        "gcd": math.gcd,
        "raiz_compleja": cmath.sqrt,  # para raíces de números negativos
    }

    # Constantes disponibles
    CONSTANTES = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": math.inf,
    }

    def __init__(self):
        self.variables = {}
        self.historial = []

    def evaluar(self, expresion: str):
        """Evalúa una expresión matemática o una asignación tipo 'x = 3 + 4'."""
        expresion = expresion.strip()
        if not expresion:
            raise ErrorCalculadora("La expresión está vacía.")

        # Detectar asignación: nombre_variable = expresion
        if "=" in expresion and not any(
            expresion.strip().startswith(op) for op in ("==", "<=", ">=", "!=")
        ):
            partes = expresion.split("=", 1)
            if len(partes) == 2 and partes[0].strip().isidentifier():
                nombre_var = partes[0].strip()
                if nombre_var in self.CONSTANTES:
                    raise ErrorCalculadora(f"'{nombre_var}' es una constante reservada.")
                valor = self._evaluar_expresion(partes[1].strip())
                self.variables[nombre_var] = valor
                self._guardar_historial(expresion, valor)
                return valor

        resultado = self._evaluar_expresion(expresion)
        self._guardar_historial(expresion, resultado)
        return resultado

    def _evaluar_expresion(self, expresion: str):
        try:
            arbol = ast.parse(expresion, mode="eval")
        except SyntaxError as e:
            raise ErrorCalculadora(f"Sintaxis inválida: {e}")

        return self._eval_nodo(arbol.body)

    def _eval_nodo(self, nodo):
        # Números literales
        if isinstance(nodo, ast.Constant):
            if isinstance(nodo.value, (int, float)):
                return nodo.value
            raise ErrorCalculadora(f"Constante no soportada: {nodo.value!r}")

        # Operaciones binarias: a + b, a * b, etc.
        if isinstance(nodo, ast.BinOp):
            tipo_op = type(nodo.op)
            if tipo_op not in self.OPERADORES_BINARIOS:
                raise ErrorCalculadora(f"Operador no soportado: {tipo_op.__name__}")
            izquierda = self._eval_nodo(nodo.left)
            derecha = self._eval_nodo(nodo.right)
            try:
                return self.OPERADORES_BINARIOS[tipo_op](izquierda, derecha)
            except ZeroDivisionError:
                raise ErrorCalculadora("División por cero.")


        if isinstance(nodo, ast.UnaryOp):
            tipo_op = type(nodo.op)
            if tipo_op not in self.OPERADORES_UNARIOS:
                raise ErrorCalculadora(f"Operador unario no soportado: {tipo_op.__name__}")
            valor = self._eval_nodo(nodo.operand)
            return self.OPERADORES_UNARIOS[tipo_op](valor)


        if isinstance(nodo, ast.Call):
            if not isinstance(nodo.func, ast.Name):
                raise ErrorCalculadora("Llamada a función inválida.")
            nombre_funcion = nodo.func.id
            if nombre_funcion not in self.FUNCIONES:
                raise ErrorCalculadora(f"Función desconocida: '{nombre_funcion}'")
            argumentos = [self._eval_nodo(arg) for arg in nodo.args]
            try:
                return self.FUNCIONES[nombre_funcion](*argumentos)
            except ValueError as e:

                raise ErrorCalculadora(
                    f"Error de dominio en '{nombre_funcion}': {e}. "
                    f"¿Quizás quieras 'raiz_compleja' para números negativos?"
                )


        if isinstance(nodo, ast.Name):
            if nodo.id in self.variables:
                return self.variables[nodo.id]
            if nodo.id in self.CONSTANTES:
                return self.CONSTANTES[nodo.id]
            raise ErrorCalculadora(f"Variable no definida: '{nodo.id}'")

        raise ErrorCalculadora(f"Expresión no soportada: {ast.dump(nodo)}")

    def _guardar_historial(self, expresion, resultado):
        self.historial.append((expresion, resultado))

    def mostrar_historial(self):
        if not self.historial:
            print("(historial vacío)")
            return
        for i, (expr, res) in enumerate(self.historial, 1):
            print(f"{i:>3}. {expr} = {res}")


def modo_interactivo():
    calc = CalculadoraAvanzada()
    print("=" * 50)
    print("  CALCULADORA AVANZADA")
    print("=" * 50)
    print("Comandos: 'historial', 'variables', 'salir'")
    print("Funciones disponibles:", ", ".join(sorted(calc.FUNCIONES.keys())))
    print("Constantes: pi, e, tau, inf")
    print("Ejemplos: sqrt(16) + 2^3   |   x = 5 * 3   |   sin(pi/2)")
    print("-" * 50)

    while True:
        try:
            entrada = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break

        if not entrada:
            continue
        if entrada.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break
        if entrada.lower() == "historial":
            calc.mostrar_historial()
            continue
        if entrada.lower() == "variables":
            if calc.variables:
                for nombre, valor in calc.variables.items():
                    print(f"  {nombre} = {valor}")
            else:
                print("(no hay variables definidas)")
            continue

        # Nota: '^' se usa comúnmente para potencia, pero en Python es '**'
        entrada_procesada = entrada.replace("^", "**")

        try:
            resultado = calc.evaluar(entrada_procesada)
            print(f"= {resultado}")
        except ErrorCalculadora as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")


if __name__ == "__main__":
    modo_interactivo()