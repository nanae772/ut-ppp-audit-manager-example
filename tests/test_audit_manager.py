from audit_manager.audit_manager import AuditManager
from pathlib import Path
from unittest.mock import MagicMock, patch


@patch("audit_manager.audit_manager.Path")
class TestAuditManager:
    max_entries_per_file = 10
    directory_name = "audit_logs"

    visitor_name = "Bob"
    time_of_visit = "2024-12-28T22:00:00Z"

    def test_create_init_file(self, PathMock):
        """ディレクトリが空のとき、audit_1.txtを作成しそこにログを記録"""
        # Arrange
        path_mock = MagicMock(name="path_mock", spec=Path)
        path_mock.iterdir.return_value = []  # 空のディレクトリ
        path_mock.write_text = MagicMock()

        new_file_mock = MagicMock(name="new_file_mock", spec=Path)
        new_file_mock.write_text = MagicMock()

        PathMock.side_effect = (
            lambda x: new_file_mock
            if x == f"./{TestAuditManager.directory_name}/audit_1.txt"
            else path_mock
        )

        sut = AuditManager(
            TestAuditManager.max_entries_per_file, TestAuditManager.directory_name
        )

        # Act
        sut.add_record(TestAuditManager.visitor_name, TestAuditManager.time_of_visit)

        # Assert
        # 新しいファイルにレコードが書き込まれることを確認
        new_file_mock.write_text.assert_called_once_with(
            f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}"
        )

    def test_add_log_to_existing_file(self, PathMock):
        """
        ディレクトリに既にファイルが存在し、最新ファイルが最大行に達していないなら最新ファイルにログを記録
        """
        # Arrange
        path_mock = MagicMock(name="path_mock", spec=Path)

        audit_file_mock = MagicMock(name="audit_file_mock", spec=Path)
        audit_file_mock.name = "audit_1.txt"
        audit_file_mock.is_file.return_value = True
        audit_file_mock.read_text.return_value = "Alice;2024-12-28T21:00:00Z"
        audit_file_mock.write_text = MagicMock()

        path_mock.iterdir.return_value = [audit_file_mock]

        PathMock.return_value = path_mock

        sut = AuditManager(
            TestAuditManager.max_entries_per_file, TestAuditManager.directory_name
        )

        # Act
        sut.add_record(TestAuditManager.visitor_name, TestAuditManager.time_of_visit)

        # Assert
        # 既にあるファイルにレコードが書き込まれることを確認
        audit_file_mock.write_text.assert_called_once_with(
            f"Alice;2024-12-28T21:00:00Z\n{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}"
        )

    def test_create_new_file_when_latest_is_max(self, PathMock):
        """最新ファイルが最大行に達しているなら、新規のファイルを作成しそこにログを記録"""
        # Arrange
        path_mock = MagicMock(name="path_mock", spec=Path)

        audit_file_mock = MagicMock(name="audit_file_mock", spec=Path)
        audit_file_mock.is_file.return_value = True
        audit_file_mock.name = "audit_1.txt"
        audit_file_mock.read_text.return_value = "\n".join(
            ["Alice;2024-12-28T21:00:00Z"] * TestAuditManager.max_entries_per_file
        )

        path_mock.iterdir.return_value = [audit_file_mock]

        new_file_mock = MagicMock(name="new_file_mock", spec=Path)
        new_file_mock.write_text = MagicMock()

        PathMock.side_effect = (
            lambda x: new_file_mock
            if x == f"./{TestAuditManager.directory_name}/audit_2.txt"
            else path_mock
        )

        sut = AuditManager(
            TestAuditManager.max_entries_per_file, TestAuditManager.directory_name
        )

        # Act
        sut.add_record(TestAuditManager.visitor_name, TestAuditManager.time_of_visit)

        # Assert
        # 新しいファイルにレコードが書き込まれることを確認
        new_file_mock.write_text.assert_called_once_with(
            f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}"
        )
