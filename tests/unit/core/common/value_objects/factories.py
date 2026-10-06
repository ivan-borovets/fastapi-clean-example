from tests.unit.core.common.value_objects.types_ import SingleFieldVO


def create_single_field_vo(value: int = 1) -> SingleFieldVO:
    return SingleFieldVO(value)
