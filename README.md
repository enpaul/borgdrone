# Borg Drone

OCI container for managing [Borg](https://borgbackup.org/) backups

## Parameter Spec

Environment var prefix: `BORGDRONE_`

| Variable | Type | Default | Usage |
|-|-|-|-|
| BORGDRONE_CHECK | `bool` | `True` | Verify repository before creating backup |
| BORGDRONE_COMPACT | `bool` | `True` | Compact the repository after all write operations |
| BORGDRONE_REPO_INIT | `bool` | `True` | Create the repository if it doesn't exist |
| BORGDRONE_REPO_INIT_APPEND_ONLY | `bool` | `False` | See `borg rcreate --append-only` |
| BORGDRONE_REPO_INIT_QUOTA | `str` | `none` | See `borg rcreate --storage-quota` |
| BORGDRONE_REPO_INIT_ENCRYPTION | `multi` | - | See `borg rcreate --encryption` |
| BORGDRONE_REPO_INIT_OVERWRITE_KEY | `bool` | `False` | If initializing a new repo and `BORGDRONE_REPO_KEY_FILE` exists, overwrite the existing key with the new repo key |
| BORGDRONE_REPO_KEY_FILE | `path` | - | Path to the repository key file |
| BORGDRONE_REPO_PATH | `path` | - | Path to the repository |
| BORGDRONE_REPO_PASSPHRASE | `str` | - | Passphrase for the key specified by `BORGDRONE_REPO_KEY_FILE` |
| BORGDRONE_REPO_PASSPHRASE_FILE | `str` | - | Passphrase for the key specified by `BORGDRONE_REPO_KEY_FILE` stored in a plaintext file |
| BORGDRONE_PRUNE | `bool` | `false` | Prune the repository according to policies |
| BORGDRONE_PRUNE_INTERVAL | `int` | - | See `borg prune --keep-within` |
| BORGDRONE_PRUNE_SECONDLY | `int` | - | See `borg prune --keep-secondly` |
| BORGDRONE_PRUNE_MINUTELY | `int` | - | See `borg prune --keep-minutely` |
| BORGDRONE_PRUNE_HOURLY | `int` | - | See `borg prune --keep-hourly` |
| BORGDRONE_PRUNE_DAILY | `int` | - | See `borg prune --keep-daily` |
| BORGDRONE_PRUNE_WEEKLY | `int` | - | See `borg prune --keep-weekly` |
| BORGDRONE_PRUNE_MONTHLY | `int` | - | See `borg prune --keep-monthly` |
| BORGDRONE_PRUNE_YEARLY | `int` | - | See `borg prune --keep-yearly` |
| BORGDRONE_ARCHIVE_COMPRESSION | `multi` | `lz4` | See `borg help compression` |
| BORGDRONE_ARCHIVE_NAME | `str` | - | Name of the archive to create |
| BORGDRONE_ARCHIVE_PATH | `csv,path` | - | Comma separated list of paths to add to the archive |
| BORGDRONE_ARCHIVE_COMMENT | `str` | - | Comment to attach to the archive
| BORGDRONE_ARCHIVE_EXCLUDE_PATTERN | `str` | - | See `borg create --exclude` |
| BORGDRONE_ARCHIVE_EXCLUDE_CACHES | `bool` | `false` | See `borg create --exclude-caches` |
| BORGDRONE_ARCHIVE_EXCLUDE_IF_PRESENT | `str` | - | See `borg create --exclude-if-present` |
| BORGDRONE_ARCHIVE_KEEP_EXCLUDE_TAGS | `bool` | `false` | See `borg create --keep-exclude-tags` |

## Design Spec

* All configuration taken from environment
* Support server and client operations
* Single run: scheduling + start/stop management should be handled by the orchestrator

Operation:

1. Check whether `BORGDRONE_REPO_PATH` exists; if not:
  1. Initialize repository at path
  1. Export key to `BORGDRONE_REPO_KEY_FILE` location
1. Run `borg check` on destination repository
1. Run `borg create` to create new archive
1. Run `borg prune` on destination repository
1. Run `borg compact` on destination repository