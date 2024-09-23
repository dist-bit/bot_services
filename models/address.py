from typing import Any, Optional, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class State:
    complete_name: str
    abbreviation: str
    renapo: str
    two_digits: str
    three_digits_nomenclature: str
    key: int

    def __init__(self, complete_name: str, abbreviation: str, renapo: str, two_digits: str, three_digits_nomenclature: str, key: int) -> None:
        self.complete_name = complete_name
        self.abbreviation = abbreviation
        self.renapo = renapo
        self.two_digits = two_digits
        self.three_digits_nomenclature = three_digits_nomenclature
        self.key = key

    @staticmethod
    def from_dict(obj: Any) -> 'State':
        assert isinstance(obj, dict)
        complete_name = from_str(obj.get("complete_name"))
        abbreviation = from_str(obj.get("abbreviation"))
        renapo = from_str(obj.get("renapo"))
        two_digits = from_str(obj.get("two_digits"))
        three_digits_nomenclature = from_str(obj.get("three_digits_nomenclature"))
        key = int(from_str(obj.get("key")))
        return State(complete_name, abbreviation, renapo, two_digits, three_digits_nomenclature, key)

    def to_dict(self) -> dict:
        result: dict = {}
        result["complete_name"] = from_str(self.complete_name)
        result["abbreviation"] = from_str(self.abbreviation)
        result["renapo"] = from_str(self.renapo)
        result["two_digits"] = from_str(self.two_digits)
        result["three_digits_nomenclature"] = from_str(self.three_digits_nomenclature)
        result["key"] = from_str(str(self.key))
        return result


class Verification:
    description: str
    status: bool
    note: Optional[str]

    def __init__(self, description: str, status: bool, note: Optional[str]) -> None:
        self.description = description
        self.status = status
        self.note = note

    @staticmethod
    def from_dict(obj: Any) -> 'Verification':
        assert isinstance(obj, dict)
        description = from_str(obj.get("description"))
        status = from_bool(obj.get("status"))
        note = from_union([from_str, from_none], obj.get("note"))
        return Verification(description, status, note)

    def to_dict(self) -> dict:
        result: dict = {}
        result["description"] = from_str(self.description)
        result["status"] = from_bool(self.status)
        result["note"] = from_union([from_str, from_none], self.note)
        return result


class Zone:
    zip_code: int
    township: str
    township_type: str
    municipality: str
    state: str
    city: str
    cp_id: int
    state_id: int
    office_id: int
    township_type_id: str
    municipality_id: str
    township_zip_type_id: int
    zone: str
    city_id: str

    def __init__(self, zip_code: int, township: str, township_type: str, municipality: str, state: str, city: str, cp_id: int, state_id: int, office_id: int, township_type_id: str, municipality_id: str, township_zip_type_id: int, zone: str, city_id: str) -> None:
        self.zip_code = zip_code
        self.township = township
        self.township_type = township_type
        self.municipality = municipality
        self.state = state
        self.city = city
        self.cp_id = cp_id
        self.state_id = state_id
        self.office_id = office_id
        self.township_type_id = township_type_id
        self.municipality_id = municipality_id
        self.township_zip_type_id = township_zip_type_id
        self.zone = zone
        self.city_id = city_id

    @staticmethod
    def from_dict(obj: Any) -> 'Zone':
        assert isinstance(obj, dict)
        zip_code = int(from_str(obj.get("zip_code")))
        township = from_str(obj.get("township"))
        township_type = from_str(obj.get("township_type"))
        municipality = from_str(obj.get("municipality"))
        state = from_str(obj.get("state"))
        city = from_str(obj.get("city"))
        cp_id = int(from_str(obj.get("cp_id")))
        state_id = int(from_str(obj.get("state_id")))
        office_id = int(from_str(obj.get("office_id")))
        township_type_id = from_str(obj.get("township_type_id"))
        municipality_id = from_str(obj.get("municipality_id"))
        township_zip_type_id = int(from_str(obj.get("township_zip_type_id")))
        zone = from_str(obj.get("zone"))
        city_id = from_str(obj.get("city_id"))
        return Zone(zip_code, township, township_type, municipality, state, city, cp_id, state_id, office_id, township_type_id, municipality_id, township_zip_type_id, zone, city_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["zip_code"] = from_str(str(self.zip_code))
        result["township"] = from_str(self.township)
        result["township_type"] = from_str(self.township_type)
        result["municipality"] = from_str(self.municipality)
        result["state"] = from_str(self.state)
        result["city"] = from_str(self.city)
        result["cp_id"] = from_str(str(self.cp_id))
        result["state_id"] = from_str(str(self.state_id))
        result["office_id"] = from_str(str(self.office_id))
        result["township_type_id"] = from_str(self.township_type_id)
        result["municipality_id"] = from_str(self.municipality_id)
        result["township_zip_type_id"] = from_str(str(self.township_zip_type_id))
        result["zone"] = from_str(self.zone)
        result["city_id"] = from_str(self.city_id)
        return result


class Payload:
    address: List[str]
    verifications: List[Verification]
    zone: Zone
    state: State
    exact: bool
    valid: bool

    def __init__(self, address: List[str], verifications: List[Verification], zone: Zone, state: State, exact: bool, valid: bool) -> None:
        self.address = address
        self.verifications = verifications
        self.zone = zone
        self.state = state
        self.exact = exact
        self.valid = valid

    @staticmethod
    def from_dict(obj: Any) -> 'Payload':
        assert isinstance(obj, dict)
        address = from_list(from_str, obj.get("address"))
        verifications = from_list(Verification.from_dict, obj.get("verifications"))
        zone = Zone.from_dict(obj.get("zone"))
        state = State.from_dict(obj.get("state"))
        exact = from_bool(obj.get("exact"))
        valid = from_bool(obj.get("valid"))
        return Payload(address, verifications, zone, state, exact, valid)

    def to_dict(self) -> dict:
        result: dict = {}
        result["address"] = from_list(from_str, self.address)
        result["verifications"] = from_list(lambda x: to_class(Verification, x), self.verifications)
        result["zone"] = to_class(Zone, self.zone)
        result["state"] = to_class(State, self.state)
        result["exact"] = from_bool(self.exact)
        result["valid"] = from_bool(self.valid)
        return result


class AddressParser:
    status: bool
    payload: Payload

    def __init__(self, status: bool, payload: Payload) -> None:
        self.status = status
        self.payload = payload

    @staticmethod
    def from_dict(obj: Any) -> 'AddressParser':
        assert isinstance(obj, dict)
        status = from_bool(obj.get("status"))
        payload = Payload.from_dict(obj.get("payload"))
        return AddressParser(status, payload)

    def to_dict(self) -> dict:
        result: dict = {}
        result["status"] = from_bool(self.status)
        result["payload"] = to_class(Payload, self.payload)
        return result
