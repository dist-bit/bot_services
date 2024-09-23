from typing import Any


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x

def from_float(x: Any) -> float:
    assert isinstance(x, float)
    return x

class FaceQuality:
    status: bool
    payload: float

    def __init__(self, status: bool, payload: float) -> None:
        self.status = status
        self.payload = payload

    @staticmethod
    def from_dict(obj: Any) -> 'FaceQuality':
        assert isinstance(obj, dict)
        status = from_bool(obj.get("status"))
        payload = from_float(obj.get("payload"))
        return FaceQuality(status, payload)

    def to_dict(self) -> dict:
        result: dict = {}
        result["status"] = from_bool(self.status)
        result["payload"] = from_float(self.payload)
        return result