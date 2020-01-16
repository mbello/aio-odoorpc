from typing import Protocol, Mapping


class ProtoAsyncResponse(Protocol):
    async def json(self) -> Mapping:
        ...


class ProtoResponse(Protocol):
    def json(self) -> Mapping:
        ...


class ProtoAsyncHttpClient(Protocol):
    async def post(self, json: Mapping) -> ProtoResponse or ProtoAsyncResponse:
        ...


class ProtoHttpClient(Protocol):
    def post(self, json: Mapping) -> ProtoResponse:
        ...
