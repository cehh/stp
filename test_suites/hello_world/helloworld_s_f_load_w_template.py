#@desc Just hello world with binary loaded to target

# What's required to run this test
requires = []

runstp_import('test_suites/templates/load_template.py')

platform.sendline('go ' + go_address + ' hello world!')
platform.expect('U-Boot#')

# Return test Result. Valid RC: 'p' => passed, 'f' => failed, 'e' => error
# Perf is an optional hash with performance data {'name': "testname", 'values': [], 'units': "values unit"}
testresult = {'RC': 'P', 'Comments': "YOOOOOOOHOOOOOOOOOOOOO!!!!!!!!!!!!!", 'Perf': None}