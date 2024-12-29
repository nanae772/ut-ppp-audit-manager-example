from audit_manager.audit_manager import AuditManager
from pathlib import Path
import pytest


@pytest.fixture
def create_test_directory():
    log_dir = Path(f"./{TestAuditManager.directory_name}/")
    if not log_dir.is_dir():
        log_dir.mkdir()

    yield

    # Teardown
    for file in log_dir.iterdir():
        if file.is_file():
            file.unlink()


@pytest.fixture
def create_existing_audit_file(create_test_directory):
    audit_file = Path(f"./{TestAuditManager.directory_name}/audit_1.txt")
    if not audit_file.is_file():
        audit_file.touch()

    audit_file.write_text("Alice;2024-12-28T21:00:00Z")
    yield audit_file

    # Teardown
    audit_file.unlink()


@pytest.fixture
def create_max_entries_audit_file(create_test_directory):
    audit_file = Path(f"./{TestAuditManager.directory_name}/audit_1.txt")
    if not audit_file.is_file():
        audit_file.touch()

    lines = ["Alice;2024-12-28T21:00:00Z"] * (TestAuditManager.max_entries_per_file)
    content = "\n".join(lines)
    audit_file.write_text(content)

    yield audit_file

    # Teardown
    audit_file.unlink()


class TestAuditManager:
    max_entries_per_file = 10
    directory_name = "audit_logs"

    visitor_name = "Bob"
    time_of_visit = "2024-12-28T22:00:00Z"

    def test_create_init_file(self, create_test_directory):
        """ディレクトリが空のとき、audit_1.txtを作成しそこにログを記録"""
        # Arrange
        audit_manager = AuditManager(
            TestAuditManager.max_entries_per_file, TestAuditManager.directory_name
        )

        # Act
        audit_manager.add_record(
            TestAuditManager.visitor_name, TestAuditManager.time_of_visit
        )

        # Assert
        test_path = Path(f"./{TestAuditManager.directory_name}/audit_1.txt")
        record = test_path.read_text()
        assert (
            record
            == f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}"
        )

    def test_add_log_to_existing_file(self, create_existing_audit_file: Path):
        """
        ディレクトリに既にファイルが存在し、最新ファイルが最大行に達していないなら最新ファイルにログを記録
        """
        # Arrange
        # Act前のファイルの行数を記録しておく
        existing_file_path = create_existing_audit_file
        lines_before_act = existing_file_path.read_text().splitlines()
        lines_count_before_act = len(lines_before_act)

        audit_manager = AuditManager(
            TestAuditManager.max_entries_per_file, TestAuditManager.directory_name
        )

        # Act
        audit_manager.add_record(
            TestAuditManager.visitor_name, TestAuditManager.time_of_visit
        )

        # Assert
        lines_after_act = existing_file_path.read_text().splitlines()
        lines_count_after_act = len(lines_after_act)
        # Act前後で行数が1増えたことを確認
        assert lines_count_after_act == lines_count_before_act + 1
        # ファイルの最後の行が書き込んだレコードに一致することを確認
        assert (
            lines_after_act[-1]
            == f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}"
        )

    def test_create_new_file_when_latest_is_max(
        self, create_max_entries_audit_file: Path
    ):
        """最新ファイルが最大行に達しているなら、新規のファイルを作成しそこにログを記録"""

        def get_file_index(file_name: str) -> int:
            """ファイル名から番号を取得(e.g. audit_1.txt -> 1, audit_2.txt -> 2)"""
            import re

            pattern = r"audit_(\d+)\.txt"
            match = re.match(pattern, file_name)
            return int(match.group(1))

        # Arrange
        existing_file = create_max_entries_audit_file
        audit_manager = AuditManager(
            TestAuditManager.max_entries_per_file, TestAuditManager.directory_name
        )

        # Act
        audit_manager.add_record(
            TestAuditManager.visitor_name, TestAuditManager.time_of_visit
        )

        # Assert
        # 既存ファイルより１大きい番号で新規ファイルが作成されること
        new_file_index = get_file_index(existing_file.name) + 1
        new_file = Path(
            f"./{TestAuditManager.directory_name}/audit_{new_file_index}.txt"
        )
        assert new_file.is_file()

        # その新規ファイルにレコードが書き込まれていること
        assert (
            new_file.read_text()
            == f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}"
        )
