# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Batch Upgrade RFA Files Inside Current pyRevit .tab
#
# Example:
# r23_Door_content.rfa  ->  r25_Door_content.rfa
#
# What it does:
# 1. Automatically finds the parent .tab folder of this button.
# 2. Recursively scans all subfolders inside that .tab.
# 3. Finds .rfa files whose filename starts with SOURCE_PREFIX.
# 4. Opens each RFA in the current Revit version.
# 5. Saves it as a new RFA with TARGET_PREFIX.
# 6. Overwrites existing target files if enabled.
#
# Important:
# - To upgrade to Revit 2025, run this in Revit 2025.
# - Revit can upgrade older families, but cannot downgrade newer families.
# - Backup your toolbar folder before running this.
# ----------------------------------------------------------------------

import os
import traceback

from pyrevit import revit, DB, forms, script, EXEC_PARAMS


# ----------------------------------------------------------------------
# USER SETTINGS
# ----------------------------------------------------------------------

SOURCE_PREFIX = "r23_"
TARGET_PREFIX = "r25_"

# For R23 -> R25, run this tool in Revit 2025.
REQUIRED_REVIT_VERSION = "2025"

# If True, existing r25 files will be overwritten.
OVERWRITE_EXISTING_TARGET = True

# If True, original r23 files will be deleted after successful upgrade.
# Strongly recommend keeping this False.
DELETE_SOURCE_AFTER_SUCCESS = True

# If True, the script only reports what it would do.
# It will not open or save any family files.
DRY_RUN = False


# ----------------------------------------------------------------------
# BASIC SETUP
# ----------------------------------------------------------------------

app = revit.doc.Application
output = script.get_output()
current_revit_version = app.VersionNumber


# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------

def normalize_path(path):
    """Return normalized absolute path."""
    return os.path.abspath(os.path.normpath(path))


def is_rfa_file(file_name):
    """Check if file is an RFA file."""
    return file_name.lower().endswith(".rfa")


def starts_with_source_prefix(file_name):
    """
    Only process files whose filename starts with SOURCE_PREFIX.

    Example:
    r23_Door_content.rfa -> yes
    Door_r23_content.rfa -> no
    """
    return file_name.lower().startswith(SOURCE_PREFIX.lower())


def get_target_file_name(source_file_name):
    """
    Replace SOURCE_PREFIX at the beginning of filename only.

    Example:
    r23_Door_content.rfa -> r25_Door_content.rfa
    """

    if not starts_with_source_prefix(source_file_name):
        return source_file_name

    remaining_name = source_file_name[len(SOURCE_PREFIX):]
    return TARGET_PREFIX + remaining_name


def get_target_path(source_path):
    """Get target file path in the same folder."""
    folder = os.path.dirname(source_path)
    source_file_name = os.path.basename(source_path)
    target_file_name = get_target_file_name(source_file_name)
    return os.path.join(folder, target_file_name)


def find_parent_tab_folder(start_path):
    """
    Starting from this script/button folder, walk upward until finding a .tab folder.
    """

    current = normalize_path(start_path)

    if os.path.isfile(current):
        current = os.path.dirname(current)

    while True:
        if current.lower().endswith(".tab"):
            return current

        parent = os.path.dirname(current)

        if parent == current:
            return None

        current = parent


def get_current_command_folder():
    """
    Get current pyRevit button folder.

    In most pyRevit environments, EXEC_PARAMS.command_path points to the command bundle folder.
    If not, this fallback uses script.get_bundle_file("").
    """

    try:
        command_path = EXEC_PARAMS.command_path

        if command_path:
            return normalize_path(command_path)
    except:
        pass

    try:
        bundle_path = script.get_bundle_file("")

        if bundle_path:
            return normalize_path(bundle_path)
    except:
        pass

    return None


def check_basic_file_info(path):
    """
    Try to read BasicFileInfo before fully opening the family.
    This helps skip files saved in a later Revit version.
    """

    try:
        info = DB.BasicFileInfo.Extract(path)

        if info.IsSavedInLaterVersion:
            return False, "File is saved in a later Revit version."

        return True, "OK"

    except Exception as ex:
        # Do not fail here. Some files may fail BasicFileInfo but still open.
        return True, "Could not read BasicFileInfo, will try to open anyway: {}".format(str(ex))


def safe_close_family_doc(family_doc):
    """Close family document safely without saving additional changes."""
    if family_doc:
        try:
            family_doc.Close(False)
        except:
            pass


def print_path_pair(source_path, target_path):
    """Print source and target path in pyRevit output window."""
    output.print_md("- `{}`  \n  → `{}`".format(source_path, target_path))


# ----------------------------------------------------------------------
# CHECK REVIT VERSION
# ----------------------------------------------------------------------

if current_revit_version != REQUIRED_REVIT_VERSION:
    forms.alert(
        "This tool is set up for Revit {}.\n\n"
        "Current Revit version: {}\n\n"
        "For example, to upgrade R23 families to R25, please run this tool in Revit 2025.".format(
            REQUIRED_REVIT_VERSION,
            current_revit_version
        ),
        title="Wrong Revit Version",
        exitscript=True
    )


# ----------------------------------------------------------------------
# FIND CURRENT .TAB FOLDER AUTOMATICALLY
# ----------------------------------------------------------------------

current_command_folder = get_current_command_folder()

if not current_command_folder:
    forms.alert(
        "Could not find current pyRevit command folder.",
        title="Cannot Find Command Folder",
        exitscript=True
    )

tab_folder = find_parent_tab_folder(current_command_folder)

if not tab_folder:
    forms.alert(
        "Could not automatically find parent .tab folder.\n\n"
        "Current command folder:\n{}\n\n"
        "Please make sure this tool is located somewhere inside a .tab folder.".format(
            current_command_folder
        ),
        title="Cannot Find .tab Folder",
        exitscript=True
    )

tab_folder = normalize_path(tab_folder)


# ----------------------------------------------------------------------
# FIND RFA FILES
# ----------------------------------------------------------------------

rfa_files = []

for root, dirs, files in os.walk(tab_folder):
    for file_name in files:

        if not is_rfa_file(file_name):
            continue

        if not starts_with_source_prefix(file_name):
            continue

        full_path = normalize_path(os.path.join(root, file_name))
        rfa_files.append(full_path)

rfa_files = sorted(rfa_files)

if not rfa_files:
    forms.alert(
        "No .rfa files starting with '{}' were found inside:\n\n{}".format(
            SOURCE_PREFIX,
            tab_folder
        ),
        title="No Files Found",
        exitscript=True
    )


# ----------------------------------------------------------------------
# PREVIEW
# ----------------------------------------------------------------------

output.print_md("# Batch RFA Upgrade Preview")
output.print_md("**Current .tab folder:** `{}`".format(tab_folder))
output.print_md("**Source prefix:** `{}`".format(SOURCE_PREFIX))
output.print_md("**Target prefix:** `{}`".format(TARGET_PREFIX))
output.print_md("**Current Revit version:** `{}`".format(current_revit_version))
output.print_md("**Files found:** `{}`".format(len(rfa_files)))

output.print_md("## Files to Process")

for source_path in rfa_files:
    target_path = get_target_path(source_path)
    print_path_pair(source_path, target_path)

if DRY_RUN:
    output.print_md("## Dry Run")
    output.print_md("DRY_RUN is set to True. No files were opened or saved.")
    script.exit()


# ----------------------------------------------------------------------
# CONFIRM BEFORE PROCESSING
# ----------------------------------------------------------------------

confirm_message = (
    "Found {} RFA files starting with '{}'.\n\n"
    "They will be opened in Revit {}, upgraded, and saved with '{}' prefix.\n\n"
    "Current .tab folder:\n{}\n\n"
    "Existing target files will be overwritten: {}\n"
    "Original source files will be deleted after success: {}\n\n"
    "Please make sure you have backed up the whole toolbar folder.\n\n"
    "Continue?"
).format(
    len(rfa_files),
    SOURCE_PREFIX,
    current_revit_version,
    TARGET_PREFIX,
    tab_folder,
    OVERWRITE_EXISTING_TARGET,
    DELETE_SOURCE_AFTER_SUCCESS
)

confirmed = forms.alert(
    confirm_message,
    title="Confirm Batch Upgrade",
    yes=True,
    no=True
)

if not confirmed:
    script.exit()


# ----------------------------------------------------------------------
# PROCESS FILES
# ----------------------------------------------------------------------

success = []
skipped = []
failed = []

for source_path in rfa_files:
    family_doc = None

    try:
        target_path = get_target_path(source_path)

        if source_path == target_path:
            skipped.append((source_path, "Target filename is the same as source filename."))
            continue

        if os.path.exists(target_path) and not OVERWRITE_EXISTING_TARGET:
            skipped.append((source_path, "Target file already exists and overwrite is disabled."))
            continue

        ok_to_open, info_message = check_basic_file_info(source_path)

        if not ok_to_open:
            skipped.append((source_path, info_message))
            continue

        # Open family.
        # If it is an older-version RFA, Revit upgrades it in memory.
        family_doc = app.OpenDocumentFile(source_path)

        if not family_doc.IsFamilyDocument:
            skipped.append((source_path, "Opened file is not a family document."))
            safe_close_family_doc(family_doc)
            family_doc = None
            continue

        # Save as target file.
        save_options = DB.SaveAsOptions()
        save_options.OverwriteExistingFile = OVERWRITE_EXISTING_TARGET

        try:
            save_options.MaximumBackups = 1
        except:
            pass

        family_doc.SaveAs(target_path, save_options)

        # Close without saving again.
        family_doc.Close(False)
        family_doc = None

        # Optional delete source file.
        if DELETE_SOURCE_AFTER_SUCCESS:
            try:
                os.remove(source_path)
            except Exception as delete_ex:
                success.append(
                    (
                        source_path,
                        target_path,
                        "Upgraded, but failed to delete source: {}".format(str(delete_ex))
                    )
                )
                continue

        success.append((source_path, target_path, "Upgraded"))

    except Exception as ex:
        failed.append(
            (
                source_path,
                str(ex),
                traceback.format_exc()
            )
        )

        safe_close_family_doc(family_doc)
        family_doc = None


# ----------------------------------------------------------------------
# REPORT
# ----------------------------------------------------------------------

output.print_md("# Batch RFA Upgrade Report")

output.print_md("**Success:** `{}`".format(len(success)))
output.print_md("**Skipped:** `{}`".format(len(skipped)))
output.print_md("**Failed:** `{}`".format(len(failed)))

if success:
    output.print_md("## Successfully Upgraded")

    for source_path, target_path, note in success:
        output.print_md("- `{}`  \n  → `{}`  \n  {}".format(source_path, target_path, note))

if skipped:
    output.print_md("## Skipped")

    for source_path, reason in skipped:
        output.print_md("- `{}`  \n  {}".format(source_path, reason))

if failed:
    output.print_md("## Failed")

    for source_path, error_message, trace in failed:
        output.print_md("### `{}`".format(source_path))
        output.print_md("**Error:** `{}`".format(error_message))
        output.print_md("```text\n{}\n```".format(trace))

forms.alert(
    "Batch upgrade finished.\n\n"
    "Success: {}\n"
    "Skipped: {}\n"
    "Failed: {}\n\n"
    "See pyRevit output window for details.".format(
        len(success),
        len(skipped),
        len(failed)
    ),
    title="Batch Upgrade Finished"
)