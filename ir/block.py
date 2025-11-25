# ir/block.py

class Block:
    def __init__(self, name):
        self.name = name           # e.g. "entry", "L1"
        self.instructions = []     # list of Instruction

    def append(self, instr):
        instr.parent = self
        self.instructions.append(instr)

    def __str__(self):
        out = f"{self.name}:\n"
        for instr in self.instructions:
            out += f"  {instr}\n"
        return out
