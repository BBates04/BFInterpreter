import sys
import array
from typing import Callable

# Check for correct number of arguments
if len(sys.argv) != 2:
    print("Usage: bfi.py <file_path>")
    sys.exit(1) # Exit with an error code

# Get file path
file_path : str = sys.argv[1]

# Enforce only .txt and .bf files
if not (file_path.lower().endswith('.txt') or file_path.lower().endswith('.bf')):
    print(f"ERROR: Invalid file type. Must be a .txt file (e.g., '{file_path}.txt').")
    sys.exit(1)

# Stores program contents
content : str = ""

# Set up 'tape'
TAPE_SIZE : int = 30000 # Minimum size as per BF language requirements
INITIAL_VALUE : int = 0 # Initial value for tape entries.

tape : array.array[int] = array.array('B', [INITIAL_VALUE] * TAPE_SIZE) # Create the tape

TAPE_ITEM_MODULO : int = 2 ** (tape.itemsize * 8) # define value to modulo against for tape item wraparound

# Initialise data pointer
dp : int = 0

# Initialise instruction pointer
ip : int = 0

# Open file and extract to content
try:
    with open(file_path, 'r') as file:
        print(f"Opening file: {file_path}...")
        # Read the entire content into content
        content = file.read()
except FileNotFoundError:
    print(f"ERROR: file '{file_path}' not found")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: unexpected error occurred - {e}")
    sys.exit(1)
print("Successfully opened file\n")

def find_matching_bracket(forwards : bool) -> int:

    # Finds the matching bracket, [ or ], starting from ip
    #
    # Args:
    # forwards - boolean determining direction of movement through code, and implicitly
    #   whether looking for a closing (forwards = True) or opening (forwards = False) bracket
    # Returns:
    # index of the matching bracket.

    # Initialise values depending on direction
    direction : int = -1
    target_char: str = '['
    nested_char: str = ']'
    error_message: str = f"could not find opening [ for jump from ] at {ip}"
    condition : Callable[[int], bool] = lambda k: k > -1

    if forwards:
        direction : int = 1
        target_char: str = ']'
        nested_char: str = '['
        error_message: str = f"could not find closing ] for jump from [ at {ip}"
        condition: Callable[[int], bool] = lambda k: k < len(content)

    nested_count: int = 0
    i: int = ip + direction # Start checking after the initial bracket
        
    while condition(i):
        char = content[i]
        
        if char == nested_char:
            # Found nested bracket of same type, increment count
            nested_count += 1
        elif char == target_char:
            if nested_count == 0:
                # Found matching bracket
                return i
            else:
                # Found nested bracket of target type, decrement count
                nested_count -= 1
        
        i += direction
        
    # If loop finishes, the matching bracket was not found
    print(f"ERROR: {error_message}")
    sys.exit(1)

# Main loop
while ip < len(content) and ip > -1:
    match content[ip]:
        case '>':
            dp = (dp + 1) % TAPE_SIZE
        case '<':
            dp = (dp - 1) % TAPE_SIZE
        case '+':
            tape[dp] = (tape[dp] + 1) % TAPE_ITEM_MODULO
        case '-':
            tape[dp] = (tape[dp] - 1) % TAPE_ITEM_MODULO
        case '.':
            sys.stdout.buffer.write(tape[dp].to_bytes())
            sys.stdout.buffer.flush() # Flush the buffer to the output
        case ',':
            byte_data : bytes = sys.stdin.buffer.read(1) # Reads exactly one byte
            if byte_data:
                tape[dp] = byte_data[0]
            else: # No byte read, write 0 and continue
                tape[dp] = 0
        case '[':
            if tape[dp] == 0: # Jump to closing bracket
                ip = find_matching_bracket(True)
        case ']':
            if tape[dp] != 0: # Jumpt to opening bracket
                ip = find_matching_bracket(False)
        case _:
            # Ignore non-command characters
            pass
    ip += 1

# Successful execution
print("\n\nProgram executed successfully")
sys.exit(0)