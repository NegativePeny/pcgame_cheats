import re
import capstone

with open(r'D:\Games\Super Meat Boy Race Mode Edition\SuperMeatBoy.exe', 'rb') as f:
    data = f.read()

cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
for m in re.finditer(rb'\x6a\x0e', data[:0x35c200]):
    pos = m.start()
    va = 0x400000 + pos + 0xc00
    chunk = data[pos : pos + 15]
    insns = list(cs.disasm(chunk, va))
    if len(insns) >= 3 and insns[2].mnemonic == 'call':
        print(f'VA 0x{va:X}: {[f"{i.mnemonic} {i.op_str}" for i in insns[:3]]}')
