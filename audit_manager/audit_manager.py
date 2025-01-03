from pathlib import Path
import re


class FileContent:
    def __init__(self, file_name: str, lines: list[str]):
        self.file_name: str = file_name
        self.lines: list[str] = lines


class FileUpdate:
    def __init__(self, file_name: str, new_content: str):
        self.file_name: str = file_name
        self.new_content: str = new_content

    def __eq__(self, other: "FileUpdate") -> bool:
        return (
            self.file_name == other.file_name and self.new_content == other.new_content
        )


class AuditManager:
    """訪問者記録システム"""

    def __init__(self, max_entries_per_file: int) -> "AuditManager":
        self._max_entries_per_file = max_entries_per_file

    def add_record(
        self, files: list[FileContent], visitor_name: str, time_of_visit: str
    ) -> FileUpdate:
        """訪問者の名前と訪問時刻をファイルに記録する"""

        def sort_by_index(files: list[FileContent]) -> list[(int, FileContent)]:
            def get_index(file_name: str) -> int:
                pattern = r"audit_(\d)+\.txt"
                return int(re.search(pattern, file_name).group(1))

            return sorted((get_index(file.file_name), file) for file in files)

        sorted_files: list[(int, FileContent)] = sort_by_index(files)
        new_record: str = f"{visitor_name};{time_of_visit}"

        if len(sorted_files) == 0:
            return FileUpdate("audit_1.txt", new_record)

        current_file_index: int
        current_file: FileContent
        current_file_index, current_file = sorted_files[-1]
        lines: list[str] = current_file.lines

        if len(lines) < self._max_entries_per_file:
            lines.append(new_record)
            new_content: str = "\n".join(lines)
            return FileUpdate(current_file.file_name, new_content)
        else:
            new_index: int = current_file_index + 1
            new_name: str = f"audit_{new_index}.txt"
            return FileUpdate(new_name, new_record)


class Persister:
    """訪問者記録ログの永続化に関する処理を担当するクラス"""

    @staticmethod
    def read_directory(directory_name: str) -> list[FileContent]:
        """指定したdirectoryを読み込んでファイルのリストを返す"""
        return [
            FileContent(file.name, file.read_text().splitlines())
            for file in Path(directory_name).iterdir()
            if file.is_file()
        ]

    @staticmethod
    def apply_update(directory_name: str, update: FileUpdate) -> None:
        """FileUpdateの内容に基づいてファイルの新規作成および更新を行う"""
        Path(directory_name).joinpath(update.file_name).write_text(update.new_content)


class ApplicationService:
    """AuditManagerとPersisterの連携を指揮するクラス"""

    def __init__(self, directory_name: str, max_entries_per_file: int):
        self._directory_name: str = directory_name
        self._audit_manager: AuditManager = AuditManager(max_entries_per_file)
        self._persister: Persister = Persister

    def add_record(self, visitor_name: str, time_of_visit: str) -> None:
        update: FileUpdate = self._audit_manager.add_record(
            self._persister.read_directory(self._directory_name),
            visitor_name,
            time_of_visit,
        )
        self._persister.apply_update(self._directory_name, update)


if __name__ == "__main__":
    import sys

    application_service = ApplicationService("audit_logs", 3)
    visitor_name, time_of_visit = sys.argv[1:]
    application_service.add_record(visitor_name, time_of_visit)
