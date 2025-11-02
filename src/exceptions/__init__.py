"""Excepciones personalizadas del sistema"""
from .base_exceptions import (
    FitFlowException,
    ValidationException,
    NotFoundException,
    BusinessRuleException,
    ExternalServiceException
)

__all__ = [
    'FitFlowException',
    'ValidationException',
    'NotFoundException',
    'BusinessRuleException',
    'ExternalServiceException'
]

