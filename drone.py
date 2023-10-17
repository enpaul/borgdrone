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
    repo_init_encryption: Optional[str] = None
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
        prefix = "BORGDRONE_"

        try:
            return cls(
                repo_path=pathlib.Path(os.environ[f"{prefix}REPO_PATH"]),
                archive_path=[
                    pathlib.Path(item.strip())
                    for item in os.environ[f"{prefix}ARCHIVE_PATH"].split(",")
                    if item
                ],
                compact=os.environ.get(f"{prefix}COMPACT", str(cls.compact)).lower()
                == "true",
                check=os.environ.get(f"{prefix}CHECK", str(cls.check)).lower()
                == "true",
                repo_init=os.environ.get(
                    f"{prefix}REPO_INIT", str(cls.repo_init)
                ).lower()
                == "true",
                repo_init_append_only=os.environ.get(
                    f"{prefix}REPO_INIT_APPEND_ONLY", str(cls.repo_init_append_only)
                ).lower()
                == "true",
                repo_init_quota=os.environ[f"{prefix}REPO_INIT_QUOTA"]
                if f"{prefix}REPO_INIT_QUOTA" in os.environ
                else cls.repo_init_quota,
                repo_init_encryption=os.environ[f"{prefix}REPO_INIT_ENCRYPTION"]
                if f"{prefix}REPO_INIT_ENCRYPTION" in os.environ
                else cls.repo_init_encryption,
                repo_init_overwrite_key=os.environ.get(
                    f"{prefix}REPO_INIT_OVERWRITE_KEY", str(cls.repo_init_overwrite_key)
                ).lower()
                == "true",
                repo_key_file=pathlib.Path(os.environ[f"{prefix}REPO_KEY_FILE"])
                if f"{prefix}REPO_KEY_FILE" in os.environ
                else cls.repo_key_file,
                repo_passphrase=os.environ[f"{prefix}REPO_PASSPHRASE"]
                if f"{prefix}REPO_PASSPHRASE" in os.environ
                else cls.repo_passphrase,
                repo_passphrase_file=pathlib.Path(
                    os.environ[f"{prefix}REPO_PASSPHRASE_FILE"]
                )
                if f"{prefix}REPO_PASSPHRASE_FILE" in os.environ
                else cls.repo_passphrase_file,
                prune=os.environ.get(f"{prefix}PRUNE", str(cls.prune)).lower()
                == "true",
                prune_interval=datetime.timedelta(
                    seconds=int(os.environ[f"{prefix}PRUNE_INTERVAL"])
                )
                if f"{prefix}PRUNE_INTERVAL" in os.environ
                else cls.prune_interval,
                prune_secondly=int(
                    os.environ.get(f"{prefix}PRUNE_SECONDLY", cls.prune_secondly)
                ),
                prune_minutely=int(
                    os.environ.get(f"{prefix}PRUNE_MINUTELY", cls.prune_minutely)
                ),
                prune_hourly=int(
                    os.environ.get(f"{prefix}PRUNE_HOURLY", cls.prune_hourly)
                ),
                prune_daily=int(
                    os.environ.get(f"{prefix}PRUNE_DAILY", cls.prune_daily)
                ),
                prune_weekly=int(
                    os.environ.get(f"{prefix}PRUNE_WEEKLY", cls.prune_weekly)
                ),
                prune_monthly=int(
                    os.environ.get(f"{prefix}PRUNE_MONTHLY", cls.prune_monthly)
                ),
                prune_yearly=int(
                    os.environ.get(f"{prefix}PRUNE_YEARLY", cls.prune_yearly)
                ),
                archive_name=os.environ[f"{prefix}ARCHIVE_NAME"]
                if f"{prefix}ARCHIVE_NAME" in os.environ
                else cls.archive_name,
                archive_comment=os.environ[f"{prefix}ARCHIVE_COMMENT"]
                if f"{prefix}ARCHIVE_COMMENT" in os.environ
                else cls.archive_comment,
                archive_exclude_pattern=os.environ[f"{prefix}ARCHIVE_EXCLUDE_PATTERN"]
                if f"{prefix}ARCHIVE_EXCLUDE_PATTERN" in os.environ
                else cls.archive_exclude_pattern,
                archive_exclude_caches=os.environ.get(
                    f"{prefix}ARCHIVE_EXCLUDE_CACHES", str(cls.archive_exclude_caches)
                ).lower()
                == "true",
                archive_exclude_if_present=os.environ[
                    f"{prefix}ARCHIVE_EXCLUDE_IF_PRESENT"
                ]
                if f"{prefix}ARCHIVE_EXCLUDE_IF_PRESENT" in os.environ
                else cls.archive_exclude_if_present,
                archive_keep_exclude_tags=os.environ.get(
                    f"{prefix}ARCHIVE_KEEP_EXCLUDE_TAGS",
                    str(cls.archive_keep_exclude_tags),
                ).lower()
                == "true",
            )
        except KeyError as err:
            raise RuntimeError(f"Required configuration parameter {err} not provided")

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
