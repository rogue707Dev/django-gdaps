from setuptools import setup

setup(
    version="0.0.1",
    name='{{ app_name }}',
    description='{{ project_title }}',
    entry_points={
        '{{ plugin_path }}': [
            '{{ app_name }} = {{ plugin_path }}.{{ app_name }}'
        ]
    }

)
