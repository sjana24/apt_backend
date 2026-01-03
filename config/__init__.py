import pymysql

# 1. Fool Django into thinking we have the modern mysqlclient driver
pymysql.version_info = (2, 2, 7, 'final', 0)
pymysql.install_as_MySQLdb()

# 2. Bypass the "MariaDB 10.6 or later is required" check
from django.db.backends.mysql.base import DatabaseWrapper
def patched_check_supported(self):
    return
DatabaseWrapper.check_database_version_supported = patched_check_supported

# 3. FIX FOR SYNTAX ERROR: Disable the "RETURNING" feature
from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.can_return_columns_from_insert = False
DatabaseFeatures.can_return_rows_from_update = False