"""
File: research_pipeline_integration.py

Overview:
Integration layer for the research_pipeline module.

Purpose:
Provides access to research_pipeline functionality for imputation and correlation.

Dependencies:
- research_pipeline: External ML pipeline module
- pandas: Data manipulation

Last Modified: 2025-08-15
Author: Claude
"""

import sys
import os
from pathlib import Path
import logging

# Add research_pipeline to Python path
RESEARCH_PIPELINE_PATH = Path("/Users/johndixon/AI_Hub/research_pipeline")
if RESEARCH_PIPELINE_PATH.exists():
    sys.path.insert(0, str(RESEARCH_PIPELINE_PATH))
else:
    raise ImportError(f"Research pipeline not found at {RESEARCH_PIPELINE_PATH}")

# Import research_pipeline modules
from research_pipeline.feature_imputer import FeatureImputer
from research_pipeline.eda import EDA
from research_pipeline.data_loader import DataLoader
from research_pipeline.feature_selection import FeatureSelection

logger = logging.getLogger(__name__)

__all__ = [
    'FeatureImputer',
    'EDA',
    'DataLoader',
    'FeatureSelection',
    'RESEARCH_PIPELINE_PATH'
]