from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import LangchainNodeParser
from ingestion.ingestion_schema import TransformationTypeEnum, Transformation
from llama_index.core.node_parser import MarkdownNodeParser

from typing import List

class IngestionUtil:
    TRANSFORMATION_MAP = {
        TransformationTypeEnum.markdown_node_parser: MarkdownNodeParser
    }
    @staticmethod
    def preprocess_transformation_conf(
            transformation_conf: List[Transformation],
    ):
        for t in transformation_conf:
            if (
                    t['transformation_type'] == TransformationTypeEnum.recursive_char_text_splitter
            ):
                if "length_function" in t['args']:
                    if t["args"]["length_function"] == "len":
                        t["args"]["length_function"] = len
    @staticmethod
    def get_transformations(transformation_conf: List[Transformation]):
        IngestionUtil.preprocess_transformation_conf(transformation_conf)
        transformations = [
            (
                IngestionUtil.TRANSFORMATION_MAP[t['transformation_type']](
                    **{k: v for k, v in t['args'].items()}
                )
                if IngestionUtil.TRANSFORMATION_MAP[t['transformation_type']]
                   not in {RecursiveCharacterTextSplitter}
                else LangchainNodeParser(
                    IngestionUtil.TRANSFORMATION_MAP[t['transformation_type']](
                        **{k: v for k, v in t['args'].items()}
                    )
                )
            )
            for t in transformation_conf
            if t['transformation_type'] in IngestionUtil.TRANSFORMATION_MAP
        ]
        return transformations