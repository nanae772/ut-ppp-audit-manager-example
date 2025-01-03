from audit_manager.audit_manager import AuditManager, FileContent, FileUpdate


class TestAuditManager:
    max_entries_per_file = 3
    directory_name = "audit_logs"

    visitor_name = "Bob"
    time_of_visit = "2024-12-28T22:00:00Z"

    def test_create_init_file(self):
        """ディレクトリが空のとき、audit_1.txtを作成しそこにログを記録"""
        # Arrange
        files: list[FileContent] = []
        sut = AuditManager(TestAuditManager.max_entries_per_file)

        # Act
        update = sut.add_record(
            files, TestAuditManager.visitor_name, TestAuditManager.time_of_visit
        )

        # Assert
        # 新しいファイルにレコードが書き込まれることを確認
        assert update == FileUpdate(
            "audit_1.txt",
            f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}",
        )

    def test_add_log_to_existing_file(self):
        """
        ディレクトリに既にファイルが存在し、最新ファイルが最大行に達していないなら最新ファイルにログを記録
        """
        # Arrange
        files: list[FileContent] = [
            FileContent("audit_1.txt", ["Alice;2024-12-28T21:00:00Z"]),
        ]
        sut = AuditManager(TestAuditManager.max_entries_per_file)

        # Act
        update = sut.add_record(
            files, TestAuditManager.visitor_name, TestAuditManager.time_of_visit
        )

        # Assert
        # 既にあるファイルにレコードが書き込まれることを確認
        assert update == FileUpdate(
            "audit_1.txt",
            f"Alice;2024-12-28T21:00:00Z\n{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}",
        )

    def test_create_new_file_when_latest_is_max(self):
        """最新ファイルが最大行に達しているなら、新規のファイルを作成しそこにログを記録"""
        # Arrange
        files: list[FileContent] = [
            FileContent("audit_1.txt", ["Alice;2024-12-28T21:00:00Z"]),
            FileContent(
                "audit_2.txt",
                ["Alice;2024-12-28T21:00:00Z"] * TestAuditManager.max_entries_per_file,
            ),
        ]
        sut = AuditManager(TestAuditManager.max_entries_per_file)

        # Act
        update = sut.add_record(
            files, TestAuditManager.visitor_name, TestAuditManager.time_of_visit
        )

        # Assert
        # 新しいファイルにレコードが書き込まれることを確認
        assert update == FileUpdate(
            "audit_3.txt",
            f"{TestAuditManager.visitor_name};{TestAuditManager.time_of_visit}",
        )
