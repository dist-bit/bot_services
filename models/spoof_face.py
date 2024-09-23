from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Payload:
    score: int
    status: bool

    def __init__(self, score: int, status: bool) -> None:
        self.score = score
        self.status = status

    @staticmethod
    def from_dict(obj: Any) -> 'Payload':
        assert isinstance(obj, dict)
        score = from_int(obj.get("score"))
        status = from_bool(obj.get("status"))
        return Payload(score, status)

    def to_dict(self) -> dict:
        result: dict = {}
        result["score"] = from_int(self.score)
        result["status"] = from_bool(self.status)
        return result


class FaceSpoofing:
    status: bool
    payload: Payload

    def __init__(self, status: bool, payload: Payload) -> None:
        self.status = status
        self.payload = payload

    @staticmethod
    def from_dict(obj: Any) -> 'FaceSpoofing':
        assert isinstance(obj, dict)
        status = from_bool(obj.get("status"))
        payload = Payload.from_dict(obj.get("payload"))
        return FaceSpoofing(status, payload)

    def to_dict(self) -> dict:
        result: dict = {}
        result["status"] = from_bool(self.status)
        result["payload"] = to_class(Payload, self.payload)
        return result