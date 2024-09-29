from typing import Any, List, TypeVar, Type, cast, Callable


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


class DocumentNumberClass:
    value: int
    hash: int
    valid: bool

    def __init__(self, value: int, hash: int, valid: bool) -> None:
        self.value = value
        self.hash = hash
        self.valid = valid

    @staticmethod
    def from_dict(obj: Any) -> 'DocumentNumberClass':
        assert isinstance(obj, dict)
        value = int(from_str(obj.get("value")))
        hash = int(from_str(obj.get("hash")))
        valid = from_bool(obj.get("valid"))
        return DocumentNumberClass(value, hash, valid)

    def to_dict(self) -> dict:
        result: dict = {}
        result["value"] = from_str(str(self.value))
        result["hash"] = from_str(str(self.hash))
        result["valid"] = from_bool(self.valid)
        return result


class CheckDigit:
    document_number: DocumentNumberClass
    dob: DocumentNumberClass
    expiry: DocumentNumberClass
    final_check: DocumentNumberClass
    valid: bool

    def __init__(self, document_number: DocumentNumberClass, dob: DocumentNumberClass, expiry: DocumentNumberClass, final_check: DocumentNumberClass, valid: bool) -> None:
        self.document_number = document_number
        self.dob = dob
        self.expiry = expiry
        self.final_check = final_check
        self.valid = valid

    @staticmethod
    def from_dict(obj: Any) -> 'CheckDigit':
        assert isinstance(obj, dict)
        document_number = DocumentNumberClass.from_dict(obj.get("document_number"))
        dob = DocumentNumberClass.from_dict(obj.get("dob"))
        expiry = DocumentNumberClass.from_dict(obj.get("expiry"))
        final_check = DocumentNumberClass.from_dict(obj.get("final_check"))
        valid = from_bool(obj.get("valid"))
        return CheckDigit(document_number, dob, expiry, final_check, valid)

    def to_dict(self) -> dict:
        result: dict = {}
        result["document_number"] = to_class(DocumentNumberClass, self.document_number)
        result["dob"] = to_class(DocumentNumberClass, self.dob)
        result["expiry"] = to_class(DocumentNumberClass, self.expiry)
        result["final_check"] = to_class(DocumentNumberClass, self.final_check)
        result["valid"] = from_bool(self.valid)
        return result


class Country:
    abbr: str
    full: str

    def __init__(self, abbr: str, full: str) -> None:
        self.abbr = abbr
        self.full = full

    @staticmethod
    def from_dict(obj: Any) -> 'Country':
        assert isinstance(obj, dict)
        abbr = from_str(obj.get("abbr"))
        full = from_str(obj.get("full"))
        return Country(abbr, full)

    def to_dict(self) -> dict:
        result: dict = {}
        result["abbr"] = from_str(self.abbr)
        result["full"] = from_str(self.full)
        return result


class PayloadDob:
    year: int
    month: str
    day: int
    original: int

    def __init__(self, year: int, month: str, day: int, original: int) -> None:
        self.year = year
        self.month = month
        self.day = day
        self.original = original

    @staticmethod
    def from_dict(obj: Any) -> 'PayloadDob':
        assert isinstance(obj, dict)
        year = from_int(obj.get("year"))
        month = from_str(obj.get("month"))
        day = from_int(obj.get("day"))
        original = int(from_str(obj.get("original")))
        return PayloadDob(year, month, day, original)

    def to_dict(self) -> dict:
        result: dict = {}
        result["year"] = from_int(self.year)
        result["month"] = from_str(self.month)
        result["day"] = from_int(self.day)
        result["original"] = from_str(str(self.original))
        return result


class Extra:
    elector_key: str
    register_month: str
    register_year: int
    section: int

    def __init__(self, elector_key: str, register_month: str, register_year: int, section: int) -> None:
        self.elector_key = elector_key
        self.register_month = register_month
        self.register_year = register_year
        self.section = section

    @staticmethod
    def from_dict(obj: Any) -> 'Extra':
        assert isinstance(obj, dict)
        elector_key = from_str(obj.get("elector_key"))
        register_month = from_str(obj.get("register_month"))
        register_year = int(from_str(obj.get("register_year")))
        section = int(from_str(obj.get("section")))
        return Extra(elector_key, register_month, register_year, section)

    def to_dict(self) -> dict:
        result: dict = {}
        result["elector_key"] = from_str(self.elector_key)
        result["register_month"] = from_str(self.register_month)
        result["register_year"] = from_str(str(self.register_year))
        result["section"] = from_str(str(self.section))
        return result


class Description:
    father_last_name: str
    mother_last_name: str

    def __init__(self, father_last_name: str, mother_last_name: str) -> None:
        self.father_last_name = father_last_name
        self.mother_last_name = mother_last_name

    @staticmethod
    def from_dict(obj: Any) -> 'Description':
        assert isinstance(obj, dict)
        father_last_name = from_str(obj.get("father_last_name"))
        mother_last_name = from_str(obj.get("mother_last_name"))
        return Description(father_last_name, mother_last_name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["father_last_name"] = from_str(self.father_last_name)
        result["mother_last_name"] = from_str(self.mother_last_name)
        return result


class Names:
    last_name: str
    names: List[str]
    description: Description

    def __init__(self, last_name: str, names: List[str], description: Description) -> None:
        self.last_name = last_name
        self.names = names
        self.description = description

    @staticmethod
    def from_dict(obj: Any) -> 'Names':
        assert isinstance(obj, dict)
        last_name = from_str(obj.get("last_name"))
        names = from_list(from_str, obj.get("names"))
        description = Description.from_dict(obj.get("description"))
        return Names(last_name, names, description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["last_name"] = from_str(self.last_name)
        result["names"] = from_list(from_str, self.names)
        result["description"] = to_class(Description, self.description)
        return result


class OptionalElement:
    value: str
    valid: bool

    def __init__(self, value: str, valid: bool) -> None:
        self.value = value
        self.valid = valid

    @staticmethod
    def from_dict(obj: Any) -> 'OptionalElement':
        assert isinstance(obj, dict)
        value = from_str(obj.get("value"))
        valid = from_bool(obj.get("valid"))
        return OptionalElement(value, valid)

    def to_dict(self) -> dict:
        result: dict = {}
        result["value"] = from_str(self.value)
        result["valid"] = from_bool(self.valid)
        return result


class Validations:
    register_month_validation: bool
    section_validation: bool

    def __init__(self, register_month_validation: bool, section_validation: bool) -> None:
        self.register_month_validation = register_month_validation
        self.section_validation = section_validation

    @staticmethod
    def from_dict(obj: Any) -> 'Validations':
        assert isinstance(obj, dict)
        register_month_validation = from_bool(obj.get("register_month_validation"))
        section_validation = from_bool(obj.get("section_validation"))
        return Validations(register_month_validation, section_validation)

    def to_dict(self) -> dict:
        result: dict = {}
        result["register_month_validation"] = from_bool(self.register_month_validation)
        result["section_validation"] = from_bool(self.section_validation)
        return result


class Payload:
    document_code: str
    document_type: str
    document_number: int
    issuer: str
    names: Names
    country: Country
    nationality: Country
    dob: PayloadDob
    sex: Country
    #check_digit: CheckDigit
    expiry: PayloadDob
    personal_number: str
    match_document_sides: bool
    address: List[str]
    optionals: List[OptionalElement]
    extra: Extra
    validations: Validations

    def __init__(self, document_code: str, document_type: str, document_number: int, issuer: str, names: Names, country: Country, nationality: Country, dob: PayloadDob, sex: Country, expiry: PayloadDob, personal_number: str, match_document_sides: bool, address: List[str], optionals: List[OptionalElement], extra: Extra, validations: Validations) -> None:
        self.document_code = document_code
        self.document_type = document_type
        self.document_number = document_number
        self.issuer = issuer
        self.names = names
        self.country = country
        self.nationality = nationality
        self.dob = dob
        self.sex = sex
        #self.check_digit = check_digit
        self.expiry = expiry
        self.personal_number = personal_number
        self.match_document_sides = match_document_sides
        self.address = address
        self.optionals = optionals
        self.extra = extra
        self.validations = validations

    @staticmethod
    def from_dict(obj: Any) -> 'Payload':
        assert isinstance(obj, dict)
        document_code = from_str(obj.get("document_code"))
        document_type = from_str(obj.get("document_type"))
        document_number = int(from_str(obj.get("document_number")))
        issuer = from_str(obj.get("issuer"))
        names = Names.from_dict(obj.get("names"))
        country = Country.from_dict(obj.get("country"))
        nationality = Country.from_dict(obj.get("nationality"))
        dob = PayloadDob.from_dict(obj.get("dob"))
        sex = Country.from_dict(obj.get("sex"))
        #check_digit = CheckDigit.from_dict(obj.get("check_digit"))
        expiry = PayloadDob.from_dict(obj.get("expiry"))
        personal_number = from_str(obj.get("personal_number"))
        match_document_sides = from_bool(obj.get("match_document_sides"))
        address = from_list(from_str, obj.get("address"))
        optionals = from_list(OptionalElement.from_dict, obj.get("optionals"))
        extra = Extra.from_dict(obj.get("extra"))
        validations = Validations.from_dict(obj.get("validations"))
        return Payload(document_code, document_type, document_number, issuer, names, country, nationality, dob, sex, expiry, personal_number, match_document_sides, address, optionals, extra, validations)

    def to_dict(self) -> dict:
        result: dict = {}
        result["document_code"] = from_str(self.document_code)
        result["document_type"] = from_str(self.document_type)
        result["document_number"] = from_str(str(self.document_number))
        result["issuer"] = from_str(self.issuer)
        result["names"] = to_class(Names, self.names)
        result["country"] = to_class(Country, self.country)
        result["nationality"] = to_class(Country, self.nationality)
        result["dob"] = to_class(PayloadDob, self.dob)
        result["sex"] = to_class(Country, self.sex)
        #result["check_digit"] = to_class(CheckDigit, self.check_digit)
        result["expiry"] = to_class(PayloadDob, self.expiry)
        result["personal_number"] = from_str(self.personal_number)
        result["match_document_sides"] = from_bool(self.match_document_sides)
        result["address"] = from_list(from_str, self.address)
        result["optionals"] = from_list(lambda x: to_class(OptionalElement, x), self.optionals)
        result["extra"] = to_class(Extra, self.extra)
        result["validations"] = to_class(Validations, self.validations)
        return result


class IDResult:
    status: bool
    payload: Payload

    def __init__(self, status: bool, payload: Payload) -> None:
        self.status = status
        self.payload = payload

    @staticmethod
    def from_dict(obj: Any) -> 'IDResult':
        assert isinstance(obj, dict)
        status = from_bool(obj.get("status"))
        payload = Payload.from_dict(obj.get("payload"))
        return IDResult(status, payload)

    def to_dict(self) -> dict:
        result: dict = {}
        result["status"] = from_bool(self.status)
        result["payload"] = to_class(Payload, self.payload)
        return result
