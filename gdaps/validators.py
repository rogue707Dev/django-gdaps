"""
GDAPS - Generic Django Apps Plugin System
Copyright (C) 2018 Christian González

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import re
from django.core.exceptions import ValidationError

plugin_components_directory_name = "components"
plugin_models_directory_name = "models"
plugin_required_directories = [
    plugin_components_directory_name,
    plugin_models_directory_name,
]  # Todo: Check if they are provided


def validate_plugin_directory(file_path):
    file_path += "/" if file_path[-1] is not "/" else ""

    # check if all required directories exist
    for dir in plugin_required_directories:
        if dir != plugin_models_directory_name:  # models are not required
            path = "{}{}".format(file_path, dir)
            if not os.path.isdir(path):
                raise ValidationError(
                    "The required directory '{}' does not exist.".format(dir)
                )

    # check if components directory conains a .js or .jsx file
    component_files = os.listdir(
        "{}{}".format(file_path, plugin_components_directory_name)
    )
    if len([c for c in component_files if c[-3:] == ".js" or c[-4:] == ".jsx"]) == 0:
        raise ValidationError(
            "The component directory must contain at least one .js or .jsx file."
        )
    # Todo: Check if a .js or .jsx file with the name of the plugin exists and contains a default export React.Component


def validate_plugin_archive_fileextension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".zip"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")
