from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict
from langchain_core.messages import BaseMessage

class PipelineState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    messages: List[BaseMessage] = []
    flats: List[Dict] = []
    enriched_flats: List[Dict] = []

    # Intent fields
    town: Optional[str] = None
    flat_type: Optional[str] = None
    max_price: Optional[int] = None
    mrt_radius: Optional[int] = None
    mrt_station: Optional[str] = None
