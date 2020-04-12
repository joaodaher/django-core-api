import logging
import os
import sys

from envparse import env


def parse_app_name():
    logger = logging.getLogger(__name__)

    explicit_environment = env.str('ENV', default=None)

    app_name = env.str('APP_NAME', default=None)
    if not app_name:
        from django.conf import settings  # pylint: disable=import-outside-toplevel
        app = settings.PROJECT_DIR.split('/')[-1]
        environment = explicit_environment or 'dev'
    else:
        try:
            app, environment = app_name.rsplit('-', 1)
        except ValueError:
            logger.critical(
                f"APP_NAME environment variable {app_name} "
                f"must be in the format app-name-environment"
            )
            sys.exit(-1)

        if explicit_environment and environment != explicit_environment:
            logger.warning(
                f"Detected environment is {environment} but {explicit_environment} provided. "
                f"Using detected environment {environment}."
            )

    app = app.replace('-', '_')
    if environment not in ['dev', 'stg', 'prd', 'test']:
        logger.warning(f"Suspicious environment name {environment} extracted from {app_name}")

    version = env.str('APP_CURRENT_VERSION', default=None)

    return app, environment, version


APP_NAME, ENV, VERSION = parse_app_name()

app_dir = env.str('APPDIR', default=None)
if app_dir:
    sys.path.append(f'{app_dir}/{APP_NAME}')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{APP_NAME}.settings')


__all__ = ['APP_NAME', 'ENV', 'VERSION']
