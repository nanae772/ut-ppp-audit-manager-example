from audit_manager.audit_manager import AuditManager, IFileSystem
from unittest.mock import MagicMock


class TestAuditManager:
    max_entries_per_file = 3
    directory_name = "audit_logs"

    visitor_name = "Bob"
    time_of_visit = "2024-12-28T22:00:00Z"

    def test_create_init_file(self):
        """ディレクトリが空のとき、audit_1.txtを作成しそこにログを記録"""
        # Arrange
        file_system_mock = MagicMock(name="file_system_mock", spec=IFileSystem)
        file_system_mock.get_files.return_value = []  # 空のディレクトリ

        sut = AuditManager(
            TestAuditManager.max_entries_per_file,
            TestAuditManager.directory_name,
            file_system_mock,
        )

        # Act
        sut.add_record(TestAuditManager.visitor_name, TestAuditManager.time_of_visit)

        # Assert
        # 新しいファイルにレコードが書き込まれることを確認
        file_system_mock.write_all_text.assert_called_once_with(
            f"./{TestAuditManager.directory_name}/audit_1.txt",
            f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}",
        )

    def test_add_log_to_existing_file(self):
        """
        ディレクトリに既にファイルが存在し、最新ファイルが最大行に達していないなら最新ファイルにログを記録
        """
        # Arrange
        file_system_mock = MagicMock(name="file_system_mock", spec=IFileSystem)

        existing_file_path = f"./{TestAuditManager.directory_name}/audit_1.txt"
        file_system_mock.get_files.return_value = [existing_file_path]

        existing_file_content = "Alice;2024-12-28T21:00:00Z"
        file_system_mock.read_all_lines.return_value = [existing_file_content]

        sut = AuditManager(
            TestAuditManager.max_entries_per_file,
            TestAuditManager.directory_name,
            file_system_mock,
        )

        # Act
        sut.add_record(TestAuditManager.visitor_name, TestAuditManager.time_of_visit)

        # Assert
        # 既にあるファイルにレコードが書き込まれることを確認
        file_system_mock.write_all_text.assert_called_once_with(
            existing_file_path,
            f"{existing_file_content}\n{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}",
        )

    def test_create_new_file_when_latest_is_max(self):
        """最新ファイルが最大行に達しているなら、新規のファイルを作成しそこにログを記録"""
        # Arrange
        file_system_mock = MagicMock(name="file_system_mock", spec=IFileSystem)

        file_system_mock.get_files.return_value = [
            f"./{TestAuditManager.directory_name}/audit_1.txt"
        ]

        file_system_mock.read_all_lines.return_value = [
            "Alice;2024-12-28T21:00:00Z"
        ] * TestAuditManager.max_entries_per_file

        sut = AuditManager(
            TestAuditManager.max_entries_per_file,
            TestAuditManager.directory_name,
            file_system_mock,
        )

        # Act
        sut.add_record(TestAuditManager.visitor_name, TestAuditManager.time_of_visit)

        # Assert
        # 新しいファイルにレコードが書き込まれることを確認
        file_system_mock.write_all_text.assert_called_once_with(
            f"./{TestAuditManager.directory_name}/audit_2.txt",
            f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}",
        )
