"""Inbound worker handler translating queued data into a use-case call."""

from app.interface.schemas import ChatRequest


async def generate(ctx: dict, payload: dict) -> dict:
    command = ChatRequest.model_validate(payload).to_command()
    response = await ctx["service"].chat(command)
    return {
        "content": response.content,
        "model": response.model,
        "cached": response.cached,
    }
