
import os
import json
import requests

from typing import Any, Union, Optional

from evals.api import CompletionFn, CompletionResult
from evals.prompt.base import (ChatCompletionPrompt,Prompt)
from evals.record import record_sampling

class CloudFlareChatCompletionResult(CompletionResult):
    def __init__(self, raw_data: Any, prompt: Any):
        self.raw_data = raw_data
        self.prompt = prompt

    def get_completions(self) -> list[str]:
        if self.raw_data and "response" in self.raw_data:
            return [self.raw_data["response"]]
        else:
            return []

class CloudFlareChatCompletionFn(CompletionFn):
    def __init__(
        self,
        model: str,
        account_id: Optional[str] = None,
        api_token: Optional[str] = None,
    ):
        self.model = model
        self.account_id = account_id if account_id else os.getenv("CLOUDFLARE_ACCOUNT_ID")
        if not self.account_id:
            raise Exception("No CloudFlare Account ID Specified")
        self.api_token = api_token if api_token else os.getenv("CLOUDFLARE_API_TOKEN")
        if not self.api_token:
            raise Exception("No CloudFlare API Token Specified")

    def __call__(
        self,
        prompt: Union[str, list[dict[str, str]]],
        **kwargs,
    ) -> CloudFlareChatCompletionResult:

        # validate type
        if not isinstance(prompt, Prompt):
            assert (
                isinstance(prompt, str)
                or (isinstance(prompt, list) and all(isinstance(token, int) for token in prompt))
                or (isinstance(prompt, list) and all(isinstance(token, str) for token in prompt))
                or (isinstance(prompt, list) and all(isinstance(msg, dict) for msg in prompt))
            ), f"Got type {type(prompt)}, with val {type(prompt[0])} for prompt, expected str or list[int] or list[str] or list[dict[str, str]]"

        # coerce to list of chat messages w/ role: system, role: user
        chat_prompt = ChatCompletionPrompt(raw_prompt=prompt).to_formatted_prompt()
       
        # execute request
        api_base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/"
        api_url = f"{api_base_url}{self.model}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        input = { "messages": chat_prompt }
        response = requests.post(api_url, headers=headers, json=input).json()

        # extract result
        if response["success"] == False:
            raise Exception(f"Cloudflare Error: {json.dumps(response['errors'])}")
        result = CloudFlareChatCompletionResult(raw_data=response["result"], prompt=chat_prompt)

        # record and return
        record_sampling(prompt=result.prompt, sampled=result.get_completions())
        return result





