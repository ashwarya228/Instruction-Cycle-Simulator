
import streamlit as st
import re

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Instruction Cycle Simulator",
    page_icon="💜",
    layout="wide"
)

# --------------------------------------------------
# DESIGN
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fffaf5, #f2efff, #eef8ff);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(120deg, #eee5ff, #e4f4ff);
    padding: 28px;
    border-radius: 24px;
    border: 1px solid #e2d9f5;
    margin-bottom: 20px;
}
.stage-card {
    background: white;
    border: 1px solid #e5def4;
    border-radius: 16px;
    padding: 16px;
    min-height: 125px;
    margin-bottom: 10px;
}
.stage-active {
    background: #eee7ff;
    border: 2px solid #8b75dc;
}
.info-card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e5def4;
    text-align: center;
}
.small-note {
    color: #68647b;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CONSTANTS AND SAMPLE PROGRAMS
# --------------------------------------------------
REGISTER_NAMES = ("R1", "R2")

EXAMPLES = {
    "Beginner: Load, Add and Store": """LOAD R1, 05
LOAD R2, 03
ADD R1, R2
STORE R1, 20
HALT""",

    "Subtraction Example": """LOAD R1, 09
LOAD R2, 04
SUB R1, R2
STORE R1, 20
HALT""",

    "Move Example": """LOAD R1, 07
MOV R2, R1
ADD R1, R2
STORE R1, 21
HALT"""
}

STAGES = [
    ("📥 Fetch", "The CPU fetches the next instruction."),
    ("🔎 Decode", "The CPU understands the instruction."),
    ("⚙️ Execute", "The CPU performs the operation."),
    ("🔄 Update", "The CPU updates the program counter.")
]

# --------------------------------------------------
# NUMBER CONVERSION
# Supports decimal numbers such as 05, hexadecimal
# such as 0x10, and binary such as 0b1010.
# --------------------------------------------------
def parse_number(value):
    value = value.strip()

    if value.lower().startswith(("0x", "0b")):
        return int(value, 0)

    return int(value, 10)


# --------------------------------------------------
# PROGRAM PARSING
# --------------------------------------------------
def get_instructions(program):
    instructions = []

    for line_number, line in enumerate(program.splitlines(), start=1):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        instructions.append({
            "line": line_number,
            "text": line
        })

    return instructions


def decode_instruction(instruction):
    parts = instruction.replace(",", " ").split()

    if not parts:
        raise ValueError("Empty instruction.")

    opcode = parts[0].upper()
    operands = parts[1:]

    if opcode in ("LOAD", "MOV", "ADD", "SUB", "STORE"):
        if len(operands) != 2:
            raise ValueError(
                f"{opcode} requires two operands."
            )

    elif opcode == "HALT":
        if len(operands) != 0:
            raise ValueError("HALT takes no operands.")

    else:
        raise ValueError(f"Unknown instruction: {opcode}")

    if opcode in ("LOAD", "MOV", "ADD", "SUB"):
        if operands[0].upper() not in REGISTER_NAMES:
            raise ValueError(
                f"Destination must be R1 or R2 in {opcode}."
            )
        operands[0] = operands[0].upper()

    if opcode == "STORE":
        if operands[0].upper() not in REGISTER_NAMES:
            raise ValueError("STORE source must be R1 or R2.")
        operands[0] = operands[0].upper()

    return opcode, operands


# --------------------------------------------------
# SIMULATOR STATE
# --------------------------------------------------
def reset_machine(program):
    st.session_state.registers = {"R1": 0, "R2": 0}
    st.session_state.memory = {20: 0, 21: 0, 22: 0}
    st.session_state.pc = 0
    st.session_state.stage_index = 0
    st.session_state.decoded = None
    st.session_state.current_instruction = ""
    st.session_state.history = []
    st.session_state.error = ""
    st.session_state.finished = False
    st.session_state.halted = False
    st.session_state.status = "Ready to execute"
    st.session_state.program_snapshot = program


def initialise_state():
    defaults = {
        "registers": {"R1": 0, "R2": 0},
        "memory": {20: 0, 21: 0, 22: 0},
        "pc": 0,
        "stage_index": 0,
        "decoded": None,
        "current_instruction": "",
        "history": [],
        "error": "",
        "finished": False,
        "halted": False,
        "status": "Ready to execute",
        "program_snapshot": EXAMPLES["Beginner: Load, Add and Store"]
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialise_state()


# --------------------------------------------------
# FETCH, DECODE, EXECUTE, UPDATE
# --------------------------------------------------
def advance_stage():
    if st.session_state.finished:
        return

    instructions = get_instructions(st.session_state.program_text)

    if st.session_state.pc >= len(instructions):
        st.session_state.finished = True
        st.session_state.status = "Program completed"
        return

    stage = st.session_state.stage_index
    current = instructions[st.session_state.pc]
    instruction_text = current["text"]

    try:
        # STAGE 1: FETCH
        if stage == 0:
            st.session_state.current_instruction = instruction_text
            st.session_state.decoded = None
            st.session_state.history.insert(0, {
                "Stage": "Fetch",
                "Instruction": instruction_text,
                "Details": f"Fetched instruction at line {current['line']}"
            })
            st.session_state.status = "Instruction fetched"
            st.session_state.stage_index = 1

        # STAGE 2: DECODE
        elif stage == 1:
            opcode, operands = decode_instruction(instruction_text)
            st.session_state.decoded = (opcode, operands)
            st.session_state.history.insert(0, {
                "Stage": "Decode",
                "Instruction": instruction_text,
                "Details": f"Decoded operation: {opcode}"
            })
            st.session_state.status = "Instruction decoded"
            st.session_state.stage_index = 2

        # STAGE 3: EXECUTE
        elif stage == 2:
            if st.session_state.decoded is None:
                raise ValueError("Fetch and decode the instruction first.")

            opcode, operands = st.session_state.decoded
            registers = st.session_state.registers
            memory = st.session_state.memory

            if opcode == "LOAD":
                dest, source = operands
                value = parse_number(source)
                registers[dest] = value
                details = f"{dest} loaded with {value}"

            elif opcode == "MOV":
                dest, source = operands

                if source.upper() in REGISTER_NAMES:
                    value = registers[source.upper()]
                else:
                    value = parse_number(source)

                registers[dest] = value
                details = f"{value} moved into {dest}"

            elif opcode == "ADD":
                dest, source = operands
                value = registers[dest] + registers[source.upper()]
                registers[dest] = value
                details = f"{dest} = {value}"

            elif opcode == "SUB":
                dest, source = operands
                value = registers[dest] - registers[source.upper()]
                registers[dest] = value
                details = f"{dest} = {value}"

            elif opcode == "STORE":
                source, address_text = operands
                address = parse_number(address_text)

                if address < 0 or address > 255:
                    raise ValueError("Memory address must be between 0 and 255.")

                memory[address] = registers[source]
                details = f"Stored {registers[source]} at memory address {address}"

            elif opcode == "HALT":
                st.session_state.halted = True
                details = "HALT instruction executed"

            st.session_state.history.insert(0, {
                "Stage": "Execute",
                "Instruction": instruction_text,
                "Details": details
            })
            st.session_state.status = details
            st.session_state.stage_index = 3

        # STAGE 4: UPDATE
        elif stage == 3:
            st.session_state.history.insert(0, {
                "Stage": "Update",
                "Instruction": instruction_text,
                "Details": f"Program counter: {st.session_state.pc} → {st.session_state.pc + 1}"
            })

            st.session_state.pc += 1

            if st.session_state.halted:
                st.session_state.finished = True
                st.session_state.status = "Program completed successfully"
            elif st.session_state.pc >= len(instructions):
                st.session_state.finished = True
                st.session_state.status = "Program completed"

            st.session_state.stage_index = 0
            st.session_state.decoded = None

    except (ValueError, OverflowError) as error:
        st.session_state.error = (
            f"Line {current['line']}: {error}"
        )
        st.session_state.status = "Execution stopped because of an error"
        st.session_state.finished = True
        st.session_state.history.insert(0, {
            "Stage": "Error",
            "Instruction": instruction_text,
            "Details": st.session_state.error
        })


def run_complete_program():
    # A maximum-step guard prevents an accidental endless run.
    for _ in range(500):
        if st.session_state.finished:
            break
        advance_stage()


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <div style="font-size:32px;">💜 💻 ✨</div>
    <h1 style="color:#302b55; margin-bottom:8px;">
        Instruction Cycle Simulator
    </h1>
    <p style="font-size:17px; color:#514b6c;">
        Computer Organization and Architecture ·
        Learn how a CPU thinks, one stage at a time.
    </p>
    <p style="color:#514b6c;">
        🌷 Fetch → Decode → Execute → Update 🌷
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "📘 Learning mode: advance one stage at a time, "
    "observe register and memory changes, and follow the execution history."
)


# --------------------------------------------------
# PROGRAM EDITOR
# --------------------------------------------------
st.subheader("📝 Your Instruction Program")

if "program_text" not in st.session_state:
    st.session_state.program_text = EXAMPLES["Beginner: Load, Add and Store"]

selected_example = st.selectbox(
    "Choose a sample program",
    list(EXAMPLES.keys())
)

if st.button("📚 Load Selected Example", use_container_width=False):
    st.session_state.program_text = EXAMPLES[selected_example]
    reset_machine(st.session_state.program_text)
    st.rerun()

program_text = st.text_area(
    "Enter one instruction per line",
    key="program_text",
    height=145,
    help="Supported instructions: LOAD, MOV, ADD, SUB, STORE, HALT."
)

if st.session_state.program_snapshot != program_text:
    reset_machine(program_text)

# Keep the saved program in sync after edits.
st.session_state.program_snapshot = program_text


# --------------------------------------------------
# FOUR STAGES
# --------------------------------------------------
st.subheader("🔄 The Four Stages")

stage_columns = st.columns(4)

for index, (title, description) in enumerate(STAGES):
    css_class = "stage-card stage-active" if (
        index == st.session_state.stage_index
        and not st.session_state.finished
    ) else "stage-card"

    with stage_columns[index]:
        st.markdown(
            f"""
            <div class="{css_class}">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

stage_progress = 1.0 if st.session_state.finished else (
    st.session_state.stage_index / 4
)

st.progress(stage_progress, text=f"Current stage: {STAGES[st.session_state.stage_index][0]}" if not st.session_state.finished else "Execution finished")


# --------------------------------------------------
# STATUS AND ERRORS
# --------------------------------------------------
if st.session_state.finished and not st.session_state.error:
    st.success("🎉 " + st.session_state.status)
elif st.session_state.status != "Ready to execute":
    st.info(st.session_state.status)

if st.session_state.error:
    st.error(st.session_state.error)


# --------------------------------------------------
# CPU CONTROL AND RUN BUTTONS
# --------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("🧩 CPU Control")
    st.markdown(f"**Program Counter (PC):** {st.session_state.pc}")
    st.markdown(
        f"**Current instruction:** "
        f"{st.session_state.current_instruction or 'Waiting for fetch'}"
    )
    st.markdown(
        f"**Status:** {st.session_state.status}"
    )

with right:
    st.subheader("🚀 Run the Simulator")

    if st.button(
        "▶️ Execute Next Stage",
        use_container_width=True,
        disabled=st.session_state.finished
    ):
        advance_stage()
        st.rerun()

    if st.button(
        "⏩ Run Complete Program",
        use_container_width=True,
        disabled=st.session_state.finished
    ):
        run_complete_program()
        st.rerun()

    if st.button("🔄 Reset Simulator", use_container_width=True):
        reset_machine(st.session_state.program_text)
        st.rerun()


# --------------------------------------------------
# REGISTERS
# --------------------------------------------------
st.subheader("📊 CPU Registers")

reg1, reg2, pc_card = st.columns(3)

with reg1:
    st.markdown(
        f"""<div class="info-card">
        <p>REGISTER R1</p><h2>{st.session_state.registers["R1"]}</h2>
        </div>""",
        unsafe_allow_html=True
    )

with reg2:
    st.markdown(
        f"""<div class="info-card">
        <p>REGISTER R2</p><h2>{st.session_state.registers["R2"]}</h2>
        </div>""",
        unsafe_allow_html=True
    )

with pc_card:
    st.markdown(
        f"""<div class="info-card">
        <p>PROGRAM COUNTER</p><h2>{st.session_state.pc}</h2>
        </div>""",
        unsafe_allow_html=True
    )


# --------------------------------------------------
# MEMORY
# --------------------------------------------------
st.subheader("🗃️ Memory")

memory_columns = st.columns(3)

for index, address in enumerate((20, 21, 22)):
    with memory_columns[index]:
        st.markdown(
            f"""<div class="info-card">
            <p>ADDRESS {address}</p>
            <h2>{st.session_state.memory.get(address, 0)}</h2>
            </div>""",
            unsafe_allow_html=True
        )


# --------------------------------------------------
# EXECUTION HISTORY
# --------------------------------------------------
st.subheader("📜 Execution History")

if st.session_state.history:
    st.dataframe(
        st.session_state.history,
        use_container_width=True,
        hide_index=True
    )
else:
    st.caption("Your execution steps will appear here.")

# --------------------------------------------------
# INSTRUCTION GUIDE
# --------------------------------------------------
st.subheader("💡 Instruction Guide")

with st.expander("View supported instructions"):
    st.markdown("""
    - `LOAD R1, 05` — Load the value 5 into R1.
    - `MOV R2, R1` — Copy the value of R1 into R2.
    - `ADD R1, R2` — Add R2 to R1 and store the result in R1.
    - `SUB R1, R2` — Subtract R2 from R1 and store the result in R1.
    - `STORE R1, 20` — Store R1's value at memory address 20.
    - `HALT` — Stop the program.
    
    **Note:** The simulator uses decimal numbers by default.
    Hexadecimal values such as `0x10` and binary values such as
    `0b1010` are also supported.
    """)

st.markdown("""
<hr>
<div style="text-align:center; color:#716b86;">
    💜 Instruction Cycle Simulator · COA Engineering Project<br>
    <small>Small simulation, big understanding ✨</small>
</div>
""", unsafe_allow_html=True)
