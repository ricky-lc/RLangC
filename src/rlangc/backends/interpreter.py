from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from rlangc.ir.ir import IRInstruction, IRModule


class InterpreterError(RuntimeError):
    pass


@dataclass(frozen=True)
class _UserFunction:
    name: str
    parameters: Tuple[str, ...]
    start_ip: int
    end_ip: int


class _ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class _Frame:
    def __init__(self, parent: Optional["_Frame"] = None) -> None:
        self.parent = parent
        self.values: Dict[str, Any] = {}
        self.const_bindings: Set[str] = set()

    def define(self, name: str, value: Any, kind: str) -> None:
        if kind == "const":
            self.const_bindings.add(name)
        self.values[name] = value

    def assign(self, name: str, value: Any) -> None:
        if name in self.values:
            if name in self.const_bindings:
                raise InterpreterError(f"Cannot reassign const '{name}'")
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        self.values[name] = value

    def resolve(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.resolve(name)
        raise InterpreterError(f"Undefined variable '{name}'")


class _VM:
    def __init__(self, module: IRModule) -> None:
        self.instructions = module.instructions
        self.stack: List[Any] = []
        self.labels = self._build_label_table(self.instructions)
        self.functions = self._collect_functions(self.instructions)
        self.globals = _Frame()
        for name, fn in self._builtins().items():
            self.globals.define(name, fn, "const")

    def run(self) -> None:
        self._run_instructions(0, len(self.instructions), self.globals, skip_function_bodies=True)

    def _build_label_table(self, instructions: List[IRInstruction]) -> Dict[str, int]:
        labels: Dict[str, int] = {}
        for index, instruction in enumerate(instructions):
            if instruction.opcode == "LABEL":
                labels[str(instruction.operands[0])] = index + 1
        return labels

    def _collect_functions(self, instructions: List[IRInstruction]) -> Dict[str, _UserFunction]:
        functions: Dict[str, _UserFunction] = {}
        index = 0
        while index < len(instructions):
            instruction = instructions[index]
            if instruction.opcode != "FUNCTION_BEGIN":
                index += 1
                continue
            name = str(instruction.operands[0])
            parameters = tuple(instruction.operands[1])
            depth = 1
            end_index = index + 1
            while end_index < len(instructions) and depth:
                op = instructions[end_index].opcode
                if op == "FUNCTION_BEGIN":
                    depth += 1
                elif op == "FUNCTION_END":
                    depth -= 1
                end_index += 1
            functions[name] = _UserFunction(
                name=name,
                parameters=parameters,
                start_ip=index + 1,
                end_ip=end_index - 1,
            )
            index = end_index
        return functions

    def _builtins(self) -> Dict[str, Callable[..., Any]]:
        return {
            "print": print,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "format": format,
            "range": range,
        }

    def _run_instructions(
        self,
        start_ip: int,
        end_ip: int,
        frame: _Frame,
        *,
        skip_function_bodies: bool = False,
    ) -> Any:
        ip = start_ip
        while ip < end_ip:
            instruction = self.instructions[ip]
            opcode = instruction.opcode
            operands = instruction.operands

            if opcode == "PUSH_CONST":
                self.stack.append(operands[0])
                ip += 1
                continue
            if opcode == "LOAD_NAME":
                self.stack.append(frame.resolve(str(operands[0])))
                ip += 1
                continue
            if opcode == "STORE_NAME":
                name = str(operands[0])
                kind = str(operands[1])
                value = self.stack.pop()
                if kind in {"let", "const"}:
                    frame.define(name, value, kind)
                else:
                    frame.assign(name, value)
                ip += 1
                continue
            if opcode == "BINARY_OP":
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(self._binary_op(str(operands[0]), left, right))
                ip += 1
                continue
            if opcode == "UNARY_OP":
                value = self.stack.pop()
                self.stack.append(self._unary_op(str(operands[0]), value))
                ip += 1
                continue
            if opcode == "POP":
                self.stack.pop()
                ip += 1
                continue
            if opcode == "JUMP_IF_FALSE":
                condition = self.stack.pop()
                ip = self.labels[str(operands[0])] if not condition else ip + 1
                continue
            if opcode == "JUMP":
                ip = self.labels[str(operands[0])]
                continue
            if opcode == "LABEL":
                ip += 1
                continue
            if opcode == "GET_ITER":
                self.stack[-1] = iter(self.stack[-1])
                ip += 1
                continue
            if opcode == "FOR_ITER":
                variable = str(operands[0])
                end_label = str(operands[1])
                iterator = self.stack[-1]
                try:
                    frame.define(variable, next(iterator), "let")
                    ip += 1
                except StopIteration:
                    self.stack.pop()
                    ip = self.labels[end_label]
                continue
            if opcode == "MAKE_LIST":
                count = int(operands[0])
                values = self.stack[-count:] if count else []
                if count:
                    del self.stack[-count:]
                self.stack.append(list(values))
                ip += 1
                continue
            if opcode == "MAKE_DICT":
                count = int(operands[0])
                items = self.stack[-(count * 2) :] if count else []
                if count:
                    del self.stack[-(count * 2) :]
                result = {}
                for item_index in range(0, len(items), 2):
                    result[items[item_index]] = items[item_index + 1]
                self.stack.append(result)
                ip += 1
                continue
            if opcode == "INDEX_GET":
                index_value = self.stack.pop()
                target = self.stack.pop()
                self.stack.append(target[index_value])
                ip += 1
                continue
            if opcode == "LOAD_ATTR":
                attribute = str(operands[0])
                target = self.stack.pop()
                self.stack.append(getattr(target, attribute))
                ip += 1
                continue
            if opcode == "CALL":
                argument_count = int(operands[0])
                self._call(frame, argument_count)
                ip += 1
                continue
            if opcode == "KW_ARG":
                name = str(operands[0])
                value = self.stack.pop()
                self.stack.append(("__kw__", name, value))
                ip += 1
                continue
            if opcode == "FUNCTION_BEGIN":
                if skip_function_bodies:
                    ip = self.functions[str(operands[0])].end_ip + 1
                    continue
                ip += 1
                continue
            if opcode == "FUNCTION_END":
                if skip_function_bodies:
                    ip += 1
                    continue
                return None
            if opcode == "RETURN":
                value = self.stack.pop()
                raise _ReturnSignal(value)
            if opcode in {"IMPORT", "CLASS_BEGIN", "CLASS_END"}:
                ip += 1
                continue
            if opcode == "ASSIGN_TARGET":
                raise InterpreterError("Assignment to complex targets is not implemented")
            raise InterpreterError(f"Unsupported opcode '{opcode}'")
        return None

    def _call(self, frame: _Frame, argument_count: int) -> None:
        raw_arguments = self.stack[-argument_count:] if argument_count else []
        if argument_count:
            del self.stack[-argument_count:]
        callee = self.stack.pop()

        positional: List[Any] = []
        keywords: Dict[str, Any] = {}
        for argument in raw_arguments:
            if isinstance(argument, tuple) and len(argument) == 3 and argument[0] == "__kw__":
                keywords[str(argument[1])] = argument[2]
            else:
                positional.append(argument)

        if isinstance(callee, _UserFunction):
            result = self._invoke_user_function(callee, positional, keywords, frame)
            self.stack.append(result)
            return
        if callable(callee):
            self.stack.append(callee(*positional, **keywords))
            return
        raise InterpreterError(f"Object of type '{type(callee).__name__}' is not callable")

    def _invoke_user_function(
        self,
        function: _UserFunction,
        positional: List[Any],
        keywords: Dict[str, Any],
        parent_frame: _Frame,
    ) -> Any:
        call_frame = _Frame(parent=parent_frame)
        if len(positional) + len(keywords) > len(function.parameters):
            raise InterpreterError(f"Too many arguments for function '{function.name}'")

        for parameter_name, value in zip(function.parameters, positional):
            call_frame.define(parameter_name, value, "let")

        for parameter_name in function.parameters[len(positional) :]:
            if parameter_name in keywords:
                call_frame.define(parameter_name, keywords.pop(parameter_name), "let")
            else:
                raise InterpreterError(
                    f"Missing required argument '{parameter_name}' for function '{function.name}'"
                )

        if keywords:
            unexpected = ", ".join(sorted(keywords))
            raise InterpreterError(f"Unexpected keyword arguments for '{function.name}': {unexpected}")

        for nested_name, nested_function in self.functions.items():
            call_frame.define(nested_name, nested_function, "const")

        try:
            self._run_instructions(function.start_ip, function.end_ip, call_frame, skip_function_bodies=False)
        except _ReturnSignal as signal:
            return signal.value
        return None

    def _binary_op(self, operator: str, left: Any, right: Any) -> Any:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            return left / right
        if operator == "%":
            return left % right
        if operator == "**":
            return left**right
        if operator == "//":
            return left // right
        if operator == "==":
            return left == right
        if operator == "!=":
            return left != right
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "and":
            return bool(left and right)
        if operator == "or":
            return bool(left or right)
        if operator == "&":
            return left & right
        if operator == "|":
            return left | right
        if operator == "^":
            return left ^ right
        if operator == "<<":
            return left << right
        if operator == ">>":
            return left >> right
        raise InterpreterError(f"Unsupported binary operator '{operator}'")

    def _unary_op(self, operator: str, value: Any) -> Any:
        if operator == "+":
            return +value
        if operator == "-":
            return -value
        if operator == "not":
            return not value
        if operator == "~":
            return ~value
        raise InterpreterError(f"Unsupported unary operator '{operator}'")


def execute(module: IRModule) -> None:
    vm = _VM(module)
    for function_name, function in vm.functions.items():
        vm.globals.define(function_name, function, "const")
    vm.run()
