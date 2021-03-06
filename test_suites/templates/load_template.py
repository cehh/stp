# Uncomment the following line to overwrite where to load test binary in memory
# load_address = 0x80000000

#Uncomment the following line to overwrite where to jump in test binary in memory
# go_address = "0x%X"%(load_address + go_offset)

# START OF TEST LOGIC
platform.sendline('')
platform.expect('U-Boot#')
platform.sendline('dhcp ' + "0x%X"%load_address + ' ' +
                   SITE_INFO['tftp_server'] + ':' + tftp_base_path +
                   '/test/hello_word/hello_world.bin')
platform.expect('U-Boot#') 