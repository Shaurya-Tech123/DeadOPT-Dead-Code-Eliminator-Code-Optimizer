import json

from improved_optimizer import optimize_code
from symbol_table import generate_symbol_table


SAMPLES = {
    "python": """import math
import os

def _unused_helper():
    x = 1
    return x

def main():
    a = 5
    a = a
    if False:
        print("dead")
    return a
    print("unreachable")
""",
    "c": """#include <stdio.h>
#include <math.h>

int helper() { return 1; }

int main() {
  int x = 3;
  x = x;
  if (0) { x = 4; }
  return x;
  x = 8;
}
""",
    "cpp": """#include <iostream>
#include <vector>

int helper() { return 1; }

int main() {
  int y = 2;
  y = y;
  if(false){ y = 8; }
  return y;
  y = 1;
}
""",
    "java": """import java.util.List;
import java.util.ArrayList;

public class Test {
  private static int helper(){ return 1; }
  public static void main(String[] args){
    int z = 9;
    z = z;
    if(false){ z = 0; }
    return;
    // unreachable
  }
}
""",
}


def run():
    results = {}
    for language, code in SAMPLES.items():
        optimized = optimize_code(language, code)
        optimized_code = optimized["optimizedCode"]
        report = optimized["report"]
        symbols = generate_symbol_table(language, optimized_code)
        if not isinstance(symbols, list) or len(symbols) == 0:
            raise RuntimeError(f"{language}: empty symbol table")
        if "summary" not in report:
            raise RuntimeError(f"{language}: missing structured report")

        results[language] = {
            "optimizedLength": len(optimized_code),
            "symbols": len(symbols),
            "linesRemoved": report["summary"]["linesRemoved"],
        }
    print(json.dumps(results))


if __name__ == "__main__":
    run()
