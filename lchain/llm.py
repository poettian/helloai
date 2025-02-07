# 这是一个使用 json_mode 的例子

from langchain_openai import ChatOpenAI
from typing import Optional
from pydantic import BaseModel,Field
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env",verbose=True)

llm = ChatOpenAI(model="gpt-4o-mini")

# Pydantic
class Joke(BaseModel):
    """Joke to tell user."""

    setup: str = Field(description="The setup of the joke.")
    punchline: str = Field(description="The punchline of the joke.")
    rating: Optional[int] = Field(
        default=None, description="How funny the joke is, from 1 to 10."
    )

structured_llm = llm.with_structured_output(None, method="json_mode")

structured_llm.invoke(
    "Tell me a joke about cats"
)