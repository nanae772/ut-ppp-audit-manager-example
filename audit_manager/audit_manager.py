from abc import ABC, abstractmethod
from pathlib import Path
import re


class IFileSystem(ABC):
    @abstractmethod
    def get_files(directory_name: str) -> list[str]:
        pass

    @abstractmethod
    def write_all_text(file_path: str, content: str) -> None:
        pass

    @abstractmethod
    def read_all_lines(file_path: str) -> list[str]:
        pass


class FileSystem(IFileSystem):
    @staticmethod
    def get_files(directory_name: str) -> list[str]:
        directory_path = Path(f"./{directory_name}")
        if not directory_path.is_dir():
            raise Exception(f"{directory_path} doesn't exists or is not directory.")

        return sorted(str(item) for item in directory_path.iterdir() if item.is_file())

    @staticmethod
    def write_all_text(file_path: str, content: str) -> None:
        Path(file_path).write_text(content)

    @staticmethod
    def read_all_lines(file_path: str) -> list[str]:
        return Path(file_path).read_text().splitlines()


class AuditManager:
    """訪問者記録システム"""

    def __init__(
        self, max_entries_per_file: int, directory_name: str, file_system: IFileSystem
    ) -> "AuditManager":
        self._max_entries_per_file = max_entries_per_file
        self._directory_name = directory_name
        self._file_system = file_system

    def add_record(self, visitor_name: str, time_of_visit: str) -> None:
        """訪問者の名前と訪問時刻をファイルに記録する"""
        file_paths = self._file_system.get_files(self._directory_name)

        new_record = f"{visitor_name};{time_of_visit}"

        # ディレクトリが空ならaudit_1.txtを新しく作成し、そこに記録
        if len(file_paths) == 0:
            new_file_path = f"./{self._directory_name}/audit_1.txt"
            self._file_system.write_all_text(new_file_path, new_record)
            return

        current_file_path = file_paths[-1]  # 最新のファイルパスを取得
        lines = self._file_system.read_all_lines(current_file_path)

        if len(lines) < self._max_entries_per_file:
            lines.append(new_record)
            new_content = "\n".join(lines)
            self._file_system.write_all_text(current_file_path, new_content)
        else:
            # 最新のファイルが最大行に達していたなら、新規ファイルを作成しそこに記録
            pattern = r"audit_(\d+)\.txt"
            match = re.search(pattern, current_file_path)
            current_file_index = int(match.group(1))
            new_index = current_file_index + 1

            new_name = f"audit_{new_index}.txt"
            new_file_path = f"./{self._directory_name}/{new_name}"
            self._file_system.write_all_text(new_file_path, new_record)


if __name__ == "__main__":
    import sys

    audit_manager = AuditManager(3, "audit_logs", FileSystem)
    visitor_name, time_of_visit = sys.argv[1:]
    audit_manager.add_record(visitor_name, time_of_visit)
