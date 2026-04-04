# ToolCalling/tool_calling.py

from typing import Optional, Union, List, Callable, Any
import datetime
import decimal
import json

from Logger.AppLogger import logger
from MySQL.mysql_client import MySQL
from PostGre.postgre_client import Postgre
from SmartNL.smart_nl_processor import SmartNLProcessor
from ChatAgent.chat_agent import ChatAgent


def serialize_result(data):
    """
    Safely convert Python objects into JSON-serializable structures.
    """
    if isinstance(data, list):
        return [serialize_result(item) for item in data]

    if isinstance(data, dict):
        return {key: serialize_result(value) for key, value in data.items()}

    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()

    if isinstance(data, datetime.timedelta):
        return str(data)

    if isinstance(data, decimal.Decimal):
        return float(data)

    if isinstance(data, set):
        return [serialize_result(item) for item in data]

    if hasattr(data, "__dict__"):
        return serialize_result(data.__dict__)

    try:
        json.dumps(data)
        return data
    except Exception:
        return str(data)


def get_last_inputs(chat_agent, last: int = 3) -> str:
    """
    Extract the last `last` user messages from chat history and join them with newlines.
    """
    try:
        if chat_agent is None or not hasattr(chat_agent, "chat_history"):
            return ""

        user_messages = []
        for entry in chat_agent.chat_history:
            if isinstance(entry, dict) and entry.get("role") == "user":
                content = str(entry.get("content", "")).strip()
                if content:
                    user_messages.append(content)

        return "\n".join(user_messages[-last:])
    except Exception as e:
        logger.error(f"Failed to extract last user inputs: {e}")
        return ""


class ToolCalling:
    def __init__(
        self,
        db: Optional[Union[MySQL, Postgre]] = None,
        smart_nl: Optional[SmartNLProcessor] = None,
        chat_agent: Optional[ChatAgent] = None,
    ):
        self.db = db
        self.smart_nl = smart_nl
        self.chat_agent = chat_agent

    def EXECUTE_SQL(self, sql_code):
        """
        Execute a read-only SQL query and return a structured response.
        """
        if not isinstance(sql_code, str) or not sql_code.strip():
            return {
                "success": False,
                "error": "sql_code must be a non-empty string",
                "systemPrompt": "The SQL execution failed. Use the error message to correct the query and try again without crashing the flow."
            }

        if self.db is None:
            return {
                "success": False,
                "error": "Database object is not set",
                "systemPrompt": "The SQL execution failed. Use the error message to correct the query and try again without crashing the flow."
            }

        try:
            if self.smart_nl is not None and self.chat_agent is not None:
                try:
                    question_context = get_last_inputs(self.chat_agent, last=3)
                    self.smart_nl.smart_nl_pipeline(
                        question=question_context,
                        top_k=7,
                        agent=self.chat_agent
                    )
                except Exception as e:
                    logger.error(f"SmartNL pipeline failed inside EXECUTE_SQL: {e}")

            rows = self.db.execute_query(query=sql_code, read_only=True)

            if isinstance(rows, list):
                total_rows = len(rows)
                shown_rows = min(total_rows, 10)
                limited_rows = rows[:10]

                return {
                    "success": True,
                    "result": serialize_result(limited_rows),
                    "total_rows": total_rows,
                    "shown_rows": shown_rows,
                    "systemPrompt": "You can directly describe the query result to the user."
                }

            return {
                "success": True,
                "result": serialize_result(rows),
                "total_rows": None,
                "shown_rows": None,
                "systemPrompt": "You can directly describe the query result to the user."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "systemPrompt": "The SQL execution failed. Use the error message to correct the query and try again without crashing the flow."
            }

    def get_functions(self) -> List[Callable]:
        return [self.EXECUTE_SQL]

    def register_on_agent(self, function_name: str, chat_agent: Optional[Any] = None) -> None:
        if function_name.upper() == "EXECUTE_SQL":
            target_agent = chat_agent if chat_agent is not None else self.chat_agent

            if target_agent is None:
                raise ValueError("No chat_agent provided to register_on_agent()")

            target_agent.register_function(
                func=self.EXECUTE_SQL,
                description="Execute a read-only SQL query against the connected database",
                parameters={
                    "type": "object",
                    "properties": {
                        "sql_code": {
                            "type": "string",
                            "description": "The read-only SQL query to execute.",
                        }
                    },
                    "required": ["sql_code"],
                },
            )
            return

        raise ValueError("Non related function name provided, please check.")
