__all__=["v8","v9"]
__version__="0.20.0"

try:
    import logfire
    logfire.configure()
    logfire.instrument_pydantic()
except ImportError:
    pass
