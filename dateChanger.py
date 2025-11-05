"""Update the Windows creation time for every non-Python file in the folder.

Usage:
	python main.py 2025-11-05 10:30:00

The timestamp accepts any ISO 8601 variant that ``datetime.fromisoformat``
understands. Naive timestamps are treated as local time.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path
import sys


FILE_WRITE_ATTRIBUTES = 0x0100
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Configure signatures once so we get helpful type checking from ctypes.
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [
	wintypes.LPCWSTR,
	wintypes.DWORD,
	wintypes.DWORD,
	wintypes.LPVOID,
	wintypes.DWORD,
	wintypes.DWORD,
	wintypes.HANDLE,
]

kernel32.SetFileTime.restype = wintypes.BOOL
kernel32.SetFileTime.argtypes = [
	wintypes.HANDLE,
	ctypes.POINTER(wintypes.FILETIME),
	ctypes.POINTER(wintypes.FILETIME),
	ctypes.POINTER(wintypes.FILETIME),
]

kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def to_filetime(dt: datetime) -> wintypes.FILETIME:
	"""Convert an aware datetime to a Windows FILETIME structure."""

	if dt.tzinfo is None:
		msg = "datetime must be timezone aware"
		raise ValueError(msg)

	dt_utc = dt.astimezone(timezone.utc)
	filetime_int = int(dt_utc.timestamp() * 10_000_000) + 116_444_736_000_000_000
	return wintypes.FILETIME(filetime_int & 0xFFFFFFFF, filetime_int >> 32)


def set_creation_time(path: Path, target: datetime) -> None:
	"""Use the Windows API to set the creation time of ``path``."""

	# Directories must be opened with FILE_FLAG_BACKUP_SEMANTICS.
	FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
	dwFlagsAndAttributes = FILE_FLAG_BACKUP_SEMANTICS if path.is_dir() else 0

	handle = kernel32.CreateFileW(
		str(path),
		FILE_WRITE_ATTRIBUTES,
		0,
		None,
		OPEN_EXISTING,
		dwFlagsAndAttributes,
		None,
	)

	if handle == INVALID_HANDLE_VALUE:
		raise ctypes.WinError(ctypes.get_last_error())

	try:
		creation_time = to_filetime(target)
		if not kernel32.SetFileTime(handle, ctypes.byref(creation_time), None, None):
			raise ctypes.WinError(ctypes.get_last_error())
	finally:
		kernel32.CloseHandle(handle)


def parse_timestamp(args: list[str]) -> datetime:
	"""Parse the target timestamp from CLI arguments."""

	if not args:
		msg = "Usage: python main.py YYYY-MM-DD [HH:MM[:SS]]"
		raise SystemExit(msg)

	raw = " ".join(args)
	try:
		parsed = datetime.fromisoformat(raw)
	except ValueError as exc:  # Provide clearer context on parsing failures.
		msg = f"Could not parse timestamp '{raw}': {exc}"
		raise SystemExit(msg) from exc

	if parsed.tzinfo is None:
		# Treat naive timestamps as local time so the user can paste explorer values.
		local_tz = datetime.now().astimezone().tzinfo
		parsed = parsed.replace(tzinfo=local_tz)

	return parsed


def main() -> None:
	timestamp = parse_timestamp(sys.argv[1:])
	folder = Path(__file__).resolve().parent
	script_path = Path(__file__).resolve()

	# Walk the tree recursively and update every file and folder.
	for entry in folder.rglob("*"):
		# Never modify the running script itself.
		if entry == script_path:
			continue

		# Skip unreadable entries (broken symlinks, permission issues).
		try:
			_ = entry.exists()
		except OSError:
			print(f"Skipping unreadable: {entry}")
			continue

		# Attempt to set creation time for both files and directories.
		try:
			set_creation_time(entry, timestamp)
			print(f"Updated creation time for {entry.relative_to(folder)}")
		except Exception as exc:
			print(f"Failed to update {entry}: {exc}")


if __name__ == "__main__":
	main()
