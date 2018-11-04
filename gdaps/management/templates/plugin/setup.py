from setuptools import setup

setup(
    version="0.0.1",
    name='{{ app_name }}',
    description='{{ project_title }}',
    entry_points={
        '{{ project_name }}.plugins': [
            '{{ app_name }} = {{ project_name }}.plugins.{{ app_name }}'
        ]
    }

)
