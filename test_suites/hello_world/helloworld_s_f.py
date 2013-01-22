#@desc Just hello world
requires = []

import pexpect

"""
expect(pattern, timeout=-1, searchwindowsize=None)
index = p.expect (['good', 'bad', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            do_something()
        elif index == 1:
            do_something_else()
        elif index == 2:
            do_some_other_thing()
        elif index == 3:
            do_something_completely_different()
 """

platform.sendline('')
idx = platform.expect(['U-Boot#', pexpect.TIMEOUT])
if idx == 0:
  print 'U-Boot received'
elif idx == 1:
  print 'Timed-out waiting for U-Boot'


