from pathlib import Path
import re


class AuditManager:
    """訪問者記録システム"""

    def __init__(
        self, max_entries_per_file: int, directory_name: str
    ) -> "AuditManager":
        self._max_entries_per_file = max_entries_per_file
        self._directory_name = directory_name

    def add_record(self, visitor_name: str, time_of_visit: str) -> None:
        """訪問者の名前と訪問時刻をファイルに記録する"""
        path = Path(self._directory_name)
        path.mkdir(exist_ok=True)
        file_paths = sorted(
            (file for file in path.iterdir() if file.is_file()),
            key=lambda file: file.name,
        )

        new_record = f"{visitor_name};{time_of_visit}"

        # ディレクトリが空ならaudit_1.txtを新しく作成し、そこに記録
        if len(file_paths) == 0:
            new_file = Path(f"./{self._directory_name}/audit_1.txt")
            new_file.write_text(new_record)
            return

        current_file_path = file_paths[-1]  # 最新のファイルパスを取得
        lines = current_file_path.read_text().splitlines()

        if len(lines) < self._max_entries_per_file:
            lines.append(new_record)
            new_content = "\n".join(lines)
            current_file_path.write_text(new_content)
        else:
            # 最新のファイルが最大行に達していたなら、新規ファイルを作成しそこに記録
            pattern = r"audit_(\d+)\.txt"
            match = re.match(pattern, current_file_path.name)
            current_file_index = int(match.group(1))
            new_index = current_file_index + 1

            new_name = f"audit_{new_index}.txt"
            new_file = Path(f"./{self._directory_name}/{new_name}")
            new_file.write_text(new_record)


if __name__ == "__main__":
    import sys

    audit_manager = AuditManager(10, "hoge")
    visitor_name, time_of_visit = sys.argv[1:]
    audit_manager.add_record(visitor_name, time_of_visit)
