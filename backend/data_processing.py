import json
import yaml
import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field as dataclass_field
from llama_index.core import Document

logger = logging.getLogger(__name__)

@dataclass
class StandardizedItem:
    data: Dict[str, Any] = dataclass_field(default_factory=dict)
    text_fields: List[Dict[str, Any]] = dataclass_field(default_factory=list) 

@dataclass
class StandardizedResult:
    standardized_data: List[StandardizedItem] = dataclass_field(default_factory=list)
    metadata_attrs: List[str] = dataclass_field(default_factory=list)
    exclude_embedings_attrs: List[str] = dataclass_field(default_factory=list)
    exclude_llm_attrs: List[str] = dataclass_field(default_factory=list)

def load_schema(schema_path: str) -> Dict[str, Any]:
    with open(schema_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as error:
            logger.error(f"Error reading YAML file: {error}")
            raise

def load_feed(feed_path: str) -> List[Dict[str, Any]]:
    with open(feed_path, encoding="utf-8") as f:
        data = json.loads(f.read())
    bbc_datum = data["referenceData"]["news"]["value"]
    return [x for x in bbc_datum if x.get("id")]

def standardized_data(
    raw_datum: List[Dict[str, Any]], 
    schema: Dict[str, Any], 
) -> StandardizedResult:
    metadata_attrs = set()
    exclude_embedings_attrs = set()
    exclude_llm_attrs = set()
    standardized_data_stream = []
    fields = schema.get("fields", [])
    for raw_data_item in raw_datum:
        standardized_data_point = {}
        text_metadata = []
        for field in fields:
            target_field = field.get("field")
            text_field_map = field.get("text", {})
            metadata_exclude = field.get("metadata_exclude", {})
            
            try:
                processed_value = raw_data_item[target_field]
                standardized_data_point[target_field] = processed_value
            except Exception as e:
                logger.error(f"Error processing field `{target_field}`: {e}")
                raise ValueError(f"Error processing field `{target_field}`")
            
            excluded_llm = metadata_exclude.get("llm", False)
            excluded_embed = metadata_exclude.get("embed", False)
            excluded_storage = metadata_exclude.get("storage", False)
                        
            if not excluded_storage:
                metadata_attrs.add(target_field)
            if excluded_embed:
                exclude_embedings_attrs.add(target_field)
            if excluded_llm:
                exclude_llm_attrs.add(target_field)
            if text_field_map:
                text_metadata.append(
                    {
                        "heading": text_field_map.get("heading"),
                        "value": processed_value
                    }
                )
        standardized_data_stream.append(
                StandardizedItem(
                    data=standardized_data_point,
                    text_fields=text_metadata
                )
            )
    return StandardizedResult(
        standardized_data=standardized_data_stream,
        metadata_attrs=list(metadata_attrs),
        exclude_embedings_attrs=list(exclude_embedings_attrs),
        exclude_llm_attrs=list(exclude_llm_attrs)
    )

def _markdown_build(
    field_text_configs: List[Dict[str, Any]]
) -> str:
    lines = []
    for doc_config in field_text_configs:
        heading = doc_config.get("heading", "")
        value = doc_config.get("value", "")
        if heading:
            lines.append(f"**{heading}**")
        if value:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).strip()

def create_document(
    doc_id: str, 
    field_text_configs: List[Dict[str, Any]], 
    metadata: Dict[str, Any] = None, 
    exclude_embedings_attrs: List[str] = None, 
    exclude_llm_attrs: List[str] = None,
) -> Document:
    metadata = metadata or {}
    exclude_embedings_keys = exclude_embedings_attrs or []
    exclude_llm_keys = exclude_llm_attrs or []
    doc = Document(
        doc_id=doc_id, 
        excluded_embed_metadata_keys=exclude_embedings_keys, 
        excluded_llm_metadata_keys=exclude_llm_keys,
        text=_markdown_build(field_text_configs))
    doc.metadata.update(metadata)
    return doc

def generate_documents(
    raw_data: List[Dict[str, Any]], 
    schema: Dict[str, Any], 
    doc_id_key: str
) -> List[Document]:
    standard_data = standardized_data(raw_data, schema)
    documents = []
    for item in standard_data.standardized_data:
        document = create_document(
            str(item.data.get(doc_id_key)),
            field_text_configs=item.text_fields,
            metadata={
                key: value
                for key, value in item.data.items()
                if key in standard_data.metadata_attrs
            },
            exclude_embedings_attrs=standard_data.exclude_embedings_attrs,
            exclude_llm_attrs=standard_data.exclude_llm_attrs,
        )
        documents.append(document)
    return documents
