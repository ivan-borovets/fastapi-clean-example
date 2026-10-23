from inspect import cleandoc
from pathlib import Path

import pytest

from scripts.makefile.self_return import Violation, find_violations, main


def test_quoted_own_name_on_a_cls_factory_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Foo":
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Foo")]


def test_base_type_on_a_cls_factory_is_reported() -> None:
    source = cleandoc(
        """
        class Sub(Base):
            @classmethod
            def create(cls, value: int) -> "Base":
                return cls(value)
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Base")]


def test_async_factory_returning_a_local_instance_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            async def create(cls) -> "Foo":
                instance = cls()
                return instance
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Foo")]


def test_factory_with_an_annotated_local_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Foo":
                instance: "Foo" = cls()
                return instance
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Foo")]


def test_unquoted_own_name_is_reported() -> None:
    source = cleandoc(
        """
        from __future__ import annotations

        class Foo:
            @classmethod
            def create(cls) -> Foo:
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=5, column=5, message="use Self instead of Foo")]


def test_ternary_of_cls_calls_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls, flag: bool) -> "Foo":
                return cls(1) if flag else cls(2)
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Foo")]


def test_factory_declared_under_a_conditional_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            if sys.version_info >= (3, 13):
                @classmethod
                def create(cls) -> "Foo":
                    return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=4, column=9, message="use Self instead of Foo")]


def test_classmethod_under_another_decorator_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            @field_validator("value")
            @classmethod
            def create(cls) -> "Foo":
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=4, column=5, message="use Self instead of Foo")]


def test_return_of_a_nested_function_is_not_the_factory_return() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Foo":
                def label() -> str:
                    return "foo"

                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Foo")]


def test_fluent_method_returning_self_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            def with_value(self, value: int) -> "Foo":
                self.value = value
                return self
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=2, column=5, message="use Self instead of Foo")]


def test_method_rebinding_self_is_accepted() -> None:
    source = cleandoc(
        """
        class Foo:
            def replace(self) -> "Foo":
                self = Other()
                return self
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_method_returning_another_object_is_accepted() -> None:
    source = cleandoc(
        """
        class Foo:
            def copy(self) -> "Foo":
                return Foo(self.value)
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


@pytest.mark.parametrize("annotation", ["Self", "typing.Self"])
def test_annotation_mentioning_self_is_accepted(annotation: str) -> None:
    source = cleandoc(
        f"""
        class Foo:
            @classmethod
            def create(cls) -> {annotation}:
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


@pytest.mark.parametrize("annotation", ['"Self"', '"typing.Self"', '"Self | None"', 'Optional["Self"]'])
def test_quoted_self_is_reported(annotation: str) -> None:
    source = cleandoc(
        f"""
        class Foo:
            @classmethod
            def create(cls) -> {annotation}:
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="drop the quotes around Self")]


def test_forward_reference_alongside_self_keeps_its_quotes() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Self | Leaf":
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_suppression_silences_the_quoted_self_violation() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Self":  # self-return: ignore
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_validator_returning_self_is_reported() -> None:
    source = cleandoc(
        """
        class Settings:
            @model_validator(mode="after")
            def check(self) -> "Settings":
                return self
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Settings")]


def test_return_of_a_nested_function_is_not_the_fluent_return() -> None:
    source = cleandoc(
        """
        class Foo:
            def rename(self, value: str) -> "Foo":
                def label() -> str:
                    return value

                return self
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=2, column=5, message="use Self instead of Foo")]


def test_factory_without_a_return_annotation_is_accepted() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls):
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_factory_rebinding_cls_is_accepted() -> None:
    source = cleandoc(
        """
        class Base:
            @classmethod
            def create(cls, kind: str) -> "Base":
                cls = REGISTRY[kind]
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_literal_annotation_that_is_not_an_expression_is_reported() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> Literal["a b"]:
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == [Violation(line=3, column=5, message="use Self instead of Literal['a b']")]


def test_factory_that_can_return_another_class_is_accepted() -> None:
    source = cleandoc(
        """
        class Base:
            @classmethod
            def create(cls, kind: str) -> "Base":
                if kind == "other":
                    return Other()
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_ternary_mixing_cls_with_another_class_is_accepted() -> None:
    source = cleandoc(
        """
        class Base:
            @classmethod
            def create(cls, flag: bool) -> "Base":
                return cls() if flag else Other()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_local_rebound_to_another_class_is_accepted() -> None:
    source = cleandoc(
        """
        class Base:
            @classmethod
            def create(cls, kind: str) -> "Base":
                result = cls()
                if kind == "other":
                    result = Other()
                return result
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_factory_hardcoding_its_own_class_is_accepted() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Foo":
                return Foo()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_method_building_cls_without_returning_it_is_accepted() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def warm_up(cls) -> None:
                cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_method_without_the_classmethod_decorator_is_accepted() -> None:
    source = cleandoc(
        """
        class Registry:
            def build(self, cls: type["Foo"]) -> "Foo":
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_factory_of_a_foreign_class_is_accepted() -> None:
    source = cleandoc(
        """
        class Factory:
            @classmethod
            def create(cls) -> "Foo":
                return Foo(cls())
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_suppression_comment_silences_the_violation() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Foo":  # self-return: ignore
                return cls()
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_suppression_on_the_last_line_of_a_wrapped_signature_is_recognized() -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(
                cls,
                value: int,
            ) -> "Foo":  # self-return: ignore
                return cls(value)
        """,
    )

    sut = list(find_violations(source))

    assert sut == []


def test_violation_renders_an_editor_navigable_diagnostic() -> None:
    violation = Violation(line=3, column=5, message="use Self instead of Foo")

    sut = violation.render(Path("mod.py"), "self-return")

    assert sut == "mod.py:3:5: self-return: use Self instead of Foo"


def test_nested_file_is_reported_on_stdout_with_the_hint_on_stderr(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Foo":
                return cls()
        """,
    )
    module = tmp_path / "pkg" / "mod.py"
    module.parent.mkdir()
    module.write_text(source, encoding="utf-8")

    sut = main([str(tmp_path)])

    captured = capsys.readouterr()
    assert sut == 1
    assert captured.out == f"{module}:3:5: self-return: use Self instead of Foo\n"
    assert captured.err == 'self-return: silence with "# self-return: ignore"\n'


def test_violations_are_reported_in_source_order(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = cleandoc(
        """
        class Outer:
            class Inner:
                @classmethod
                def create(cls) -> "Inner":
                    return cls()

            @classmethod
            def create(cls) -> "Outer":
                return cls()
        """,
    )
    module = tmp_path / "mod.py"
    module.write_text(source, encoding="utf-8")

    main([str(tmp_path)])

    sut = capsys.readouterr().out.splitlines()
    assert sut == [
        f"{module}:4:9: self-return: use Self instead of Inner",
        f"{module}:8:5: self-return: use Self instead of Outer",
    ]


def test_tree_without_violations_exits_zero(tmp_path: Path) -> None:
    source = cleandoc(
        """
        from typing import Self

        class Foo:
            @classmethod
            def create(cls) -> Self:
                return cls()
        """,
    )
    (tmp_path / "mod.py").write_text(source, encoding="utf-8")

    sut = main([str(tmp_path)])

    assert sut == 0


def test_violation_in_a_byte_order_marked_file_is_reported(tmp_path: Path) -> None:
    source = cleandoc(
        """
        class Foo:
            @classmethod
            def create(cls) -> "Foo":
                return cls()
        """,
    )
    (tmp_path / "mod.py").write_text(source, encoding="utf-8-sig")

    sut = main([str(tmp_path)])

    assert sut == 1


def test_root_that_is_not_a_directory_is_rejected(tmp_path: Path) -> None:
    file_root = tmp_path / "mod.py"
    file_root.write_text("", encoding="utf-8")

    for root in (tmp_path / "absent", file_root):
        with pytest.raises(SystemExit, match="no such directory"):
            main([str(root)])


def test_unparsable_file_is_rejected_with_its_path(tmp_path: Path) -> None:
    (tmp_path / "mod.py").write_text("def broken(:\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="cannot check"):
        main([str(tmp_path)])


def test_file_in_a_foreign_encoding_is_rejected_with_its_path(tmp_path: Path) -> None:
    (tmp_path / "mod.py").write_bytes(b"\xff\x00class Foo:\n")

    with pytest.raises(SystemExit, match="cannot check"):
        main([str(tmp_path)])


def test_call_without_roots_is_rejected() -> None:
    with pytest.raises(SystemExit, match="usage"):
        main([])
