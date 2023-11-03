"""
Curation module
"""

from .stac.dataframe import STACDataFrame  # , read_stac
from .stac.stac import STACGenerator
from .stac.parsers import STACIdParser, StructuredParser, UnestructuredParser
from .stac.dataframe_labeling import UnlabeledStrategy, LabeledStrategy
