# -*- coding: utf-8 -*-

import os

from pyrevit import revit, script, forms

from Autodesk.Revit.Exceptions import InvalidOperationException

# Exact file name inside this same .pushbutton folder

RVT_FILE_NAME = "MY_System Family Container_R25.rvt"


def get_target_file():
    """Return full path to the RVT stored inside this button folder."""

    return script.get_bundle_file(RVT_FILE_NAME)


def find_already_open_doc(app, target_path):
    """Return already-open doc if the same file is open, else None."""

    target_norm = os.path.normcase(os.path.normpath(target_path))

    for doc in app.Documents:

        try:

            if doc.PathName:

                open_norm = os.path.normcase(os.path.normpath(doc.PathName))

                if open_norm == target_norm:
                    return doc

        except Exception:

            pass

    return None


uiapp = revit.uidoc.Application

app = uiapp.Application

target_file = get_target_file()

if not os.path.exists(target_file):
    forms.alert(

        "File not found:\n{}".format(target_file),

        title="Open Local Revit File",

        warn_icon=True

    )

    script.exit()

# Safety check: OpenAndActivateDocument is not allowed with an open transaction.

if revit.doc.IsModifiable:
    forms.alert(

        "Please finish or cancel the current transaction/edit mode first, then run the button again.",

        title="Open Local Revit File",

        warn_icon=True

    )

    script.exit()

# If the file is already open, activate it.

already_open = find_already_open_doc(app, target_file)

try:

    if already_open:

        uiapp.OpenAndActivateDocument(target_file)

    else:

        uiapp.OpenAndActivateDocument(target_file)

except InvalidOperationException as ex:

    forms.alert(

        "Revit could not open the file.\n\n{}".format(str(ex)),

        title="Open Local Revit File",

        warn_icon=True

    )

except Exception as ex:

    forms.alert(

        "Unexpected error:\n\n{}".format(str(ex)),

        title="Open Local Revit File",

        warn_icon=True

    )
