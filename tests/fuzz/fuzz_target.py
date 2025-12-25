from __future__ import annotations

import sys
import atheris

# Define the target function before importing modules that might need instrumentation
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    
    # Generate fuzzed inputs for bargaining_from_state
    try:
        pressure = fdp.ConsumeFloat()
        effgap = fdp.ConsumeFloat()
        k = fdp.ConsumeFloat()
        
        from nhra_game_theory.equilibrium import bargaining_from_state
        
        # We don't care about the result, just that it doesn't crash 
        # or violate its icontract postconditions (which would raise ViolationError)
        bargaining_from_state(pressure, effgap, k)
        
    except (ValueError, OverflowError, ZeroDivisionError):
        # Expected errors for extreme floats
        pass
    except Exception as e:
        # Unexpected errors are failures
        if "ViolationError" in str(type(e)):
            # This is an icontract violation found by fuzzing!
            raise e
        raise e

if __name__ == "__main__":
    # Atheris requires instrumentation. For simplicity in this SOTA upgrade, 
    # we'll use the basic setup.
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
