"""
Fuentes Proxy - Integraciones con servicios externos.

Las fuentes proxy actúan como intermediarios entre nuestro sistema
y servicios externos, encapsulando la lógica de comunicación.
"""
from .pasarela_pagos_proxy import PasarelaPagosProxy
from .clases_externas_proxy import ClasesExternasProxy

__all__ = [
    'PasarelaPagosProxy',
    'ClasesExternasProxy'
]

