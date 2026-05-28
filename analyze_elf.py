import sys
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

path = r"d:\PICOCTF\EASY\PIE TIME\PIETIME"

def analyze_elf(filename):
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)
        section = elffile.get_section_by_name('.symtab')
        
        if not section:
            print("No symbol table found.")
            return

        if isinstance(section, SymbolTableSection):
            for symbol in section.iter_symbols():
                if symbol.name == 'win':
                    print(f"Found 'win' function at offset: {hex(symbol['st_value'])}")
                    return
                # Also look for main to establish a baseline if needed
                if symbol.name == 'main':
                    print(f"Found 'main' function at offset: {hex(symbol['st_value'])}")

analyze_elf(path)
