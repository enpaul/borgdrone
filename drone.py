import dataclasses
import datetime
import os
import pathlib
import sys
from typing import List
from typing import Optional

import plumbum.cmd
import plumbum.machines


@dataclasses.dataclass
class Config:
    repo_path: pathlib.Path
    archive_path: List[str]
    check: bool = True
    compact: bool = True
    repo_init: bool = True
    repo_init_append_only: bool = False
    repo_init_quota: Optional[str] = None
    repo_init_encryption: str = ""
    repo_init_overwrite_key: bool = False
    repo_key_file: pathlib.Path = pathlib.Path("/keys")
    repo_passphrase: Optional[str] = None
    repo_passphrase_file: Optional[pathlib.Path] = None
    prune: bool = False
    prune_interval: Optional[datetime.timedelta] = None
    prune_secondly: Optional[int] = None
    prune_minutely: Optional[int] = None
    prune_hourly: Optional[int] = None
    prune_daily: Optional[int] = None
    prune_weekly: Optional[int] = None
    prune_monthly: Optional[int] = None
    prune_yearly: Optional[int] = None
    archive_name: Optional[str] = None
    archive_comment: Optional[str] = None
    archive_exclude_pattern: Optional[str] = None
    archive_exclude_caches: bool = False
    archive_exclude_if_present: Optional[str] = None
    archive_keep_exclude_tags: bool = False

    @classmethod
    def build(cls):
        parameters = {}
        for conf, field in cls.__dataclass_fields__.items():
            env = f"BORGDRONE_{conf.upper()}"
            if env in os.environ:
                if field.type == bool:
                    parameters[conf] = cls._parse_bool(env, os.environ[env])

        return cls(**parameters)

    @staticmethod
    def _parse_bool(env: str, value: str) -> bool:
        if value.lower().strip() == "true":
            return True
        elif value.lower().strip() == "false":
            return False
        else:
            raise RuntimeError(
                f"Environment variable {env} contains an unexpected value '{value}', expected one of: 'true', 'false'"
            )


def check_version(borg: plumbum.machines.LocalCommand):
    version = borg["--version"]().partition(" ")[-1].strip()

    if int(version.partition(".")[0]) < 2:
        raise RuntimeError("BorgDrone requires BorgBackup version 2.0 or higher")

    print(f"Using BorgBackup {version} from {borg.executable}", file=sys.stderr)


def main() -> int:
    borg = plumbum.cmd.borg
    code = 0

    try:
        check_version(borg)

        config = Config.build()
    except RuntimeError as err:
        print(f"FATAL: {err}", file=sys.stderr)
        code = 1

    return code


if __name__ == "__main__":
    sys.exit(main())
