import argparse
import sys
from pathlib import Path

import pandas as pd


def infer_type(val):
    s = str(val).lower()
    if s in ["true", "false"]:
        return "bool"
    if s in ["none", "nan", ""] or pd.isna(val):
        return "Any"
    try:
        # Check if it's an integer or a float that is effectively an integer
        f_val = float(val)
        if f_val.is_integer():
            return "int"
        return "float"
    except ValueError:
        return "str"


def generate_params_code(csv_path, output_path):
    df = pd.read_csv(csv_path)

    # Filter out rows that are not scalar parameters
    scalar_df = df[~df["value"].astype(str).str.startswith("(")]

    content = "# AUTO-GENERATED FILE. DO NOT EDIT.\n"
    content += "from __future__ import annotations\n"
    content += "from typing import Any\n"
    content += "from flax import struct\n"
    content += "import jax.numpy as jnp\n\n"
    content += "@struct.dataclass\n"
    content += "class ParamsGenerated:\n"
    content += '    """Auto-generated parameter container from registry CSV."""\n'

    for _, row in scalar_df.iterrows():
        param = row["parameter"]
        val = row["value"]
        desc = row["description"]
        units = row["units"]

        py_type = infer_type(val)

        if py_type == "str":
            val_code = f'"{val}"'
            field_def = f"struct.field(default={val_code}, pytree_node=False)"
        elif py_type == "bool":
            val_code = str(val).capitalize()
            field_def = val_code
        elif py_type == "Any":
            val_code = "None"
            field_def = f"struct.field(default={val_code}, pytree_node=False)"
        elif py_type == "int":
            val_code = str(int(float(val)))
            field_def = val_code
        else:
            val_code = str(val)
            field_def = val_code

        content += f"    {param}: {py_type} = {field_def}  # {desc} ({units})\n"

    return content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    project_root = Path(__file__).parent.parent.parent
    csv_path = project_root / "context/04_parameter_registry.csv"
    output_path = project_root / "src/nhra_gt/domain/params_generated.py"
    generated = generate_params_code(csv_path, output_path)
    if args.check:
        if output_path.exists():
            with open(output_path) as f:
                current = f.read()
            if current == generated:
                print("Check passed")
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            sys.exit(1)
    else:
        with open(output_path, "w") as f:
            f.write(generated)
        print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
