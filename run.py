import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

module_name = sys.argv[1]
function_name = ' '.join(sys.argv[2:])

exec('import %s' % module_name)
exec('%s.%s' % (module_name, function_name))
