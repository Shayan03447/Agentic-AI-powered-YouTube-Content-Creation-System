import os
import json
import logging
from typing import Any
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

