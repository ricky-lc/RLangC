from rlangc.ir.ir import IRModule


def generate_c(module: IRModule) -> str:
    return f"""#include <stdio.h>

int main(void) {{
    printf("RLangC native executable bootstrap\\n");
    printf("token_count={len(module.tokens)}\\n");
    return 0;
}}
"""
