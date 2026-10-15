import streamlit as st
import re

st.set_page_config(
    page_title="Instruction Cycle Simulator",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- PASTEL DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #f8f6ff 0%, #eef4ff 55%, #fdf6ff 100%);
}
.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    background: linear-gradient(120deg, #dcd6ff, #dceaff, #f4e1ff);
    border: 1px solid #d4ccff;
    padding: 28px;
    border-radius: 26px;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px #8c83c51c;
}
.hero h1 {
    color: #292858;
    font-size: 2.5rem;
    font-weight: 900;
    margin: 0;
}
.hero p {
    color: #56567d;
    font-size: 1.05rem;
    margin-bottom: 0;
}
.section-title {
    color: #383568;
    font-size: 1.35rem;
    font-weight: 900;
    margin: 10px 0;
}
.stage-card {
    border-radius: 18px;
    padding: 18px 12px;
    text-align: center;
    min-height: 138px;
    border: 2px solid #ffffff;
    box-shadow: 0 5px 15px #4b47851a;
}
.stage-card h3 {
    font-size: 1.05rem;
    color: #292858;
    margin: 4px 0;
}
.stage-card p {
    color: #53536f;
    font-size: .87rem;
    margin: 4px 0;
}
.stage-icon {font-size: 1.8rem;}
.stage-active {
    border: 3px solid #7770db;
    box-shadow: 0 0 0 4px #7770db22, 0 7px 20px #4b478525;
    transform: translateY(-2px);
}
.panel {
    background: #ffffffd9;
    border: 1px solid #e2ddfa;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 5px 20px #514a8b0d;
    margin-bottom: 14px;
}
.metric-card {
    background: linear-gradient(135deg, #f0edff, #eaf3ff);
    border: 1px solid #dcd7fa;
    border-radius: 16px;
    padding: 14px;
    text-align: center;
}
.metric-label {
    color: #66618e;
    font-size: .85rem;
    font-weight: 800;
}
.metric-value {
    color: #292858;
    font-size: 1.65rem;
    font-weight: 900;
}
.instruction {
    background: #f0efff;
    border: 1px solid #d9d3ff;
    color: #393566;
    border-radius: 12px;
    padding: 12px;
    margin: 7px 0;
    font-family: monospace;
}
.stButton > button {
    border-radius: 12px;
    font-weight: 800;
    min-height: 44px;
}
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #8b7bea, #79b7f5);
}
div[data-testid="stSidebar"] {
    background: #f0edff;
}
.small-note {
    color: #777397;
    font-size: .85rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- SAMPLE PROGRAMS ----------
PROGRAMS = {
    "Beginner: Load, Add and Store": """LOAD R1, 05
LOAD R2, 03
ADD R1, R2
STORE R1, 20
HALT""",
    "Subtraction Example": """LOAD R1, 12
LOAD R2, 04
SUB R1, R2
STORE R1, 21
HALT""",
    "Move and Add Example": """LOAD R1, 06
MOV R2, R1
ADD R1, R2
STORE R1, 22
HALT""",
}

REGISTER_NAMES = ("R1", "R2")
def parse_number(value):
    value = value.strip()
    if value.lower().startswith(("0x", "0b")):
        return int(value, 0)
    return int(value, 10)
STAGES = [
    ("🔍", "FETCH", "Read the next instruction", "#fff0d9"),
    ("🧠", "DECODE", "Understand the instruction", "#ffe8f1"),
    ("⚙️", "EXECUTE", "Perform the operation", "#ddf8ed"),
    ("🔄", "UPDATE", "Advance the program counter", "#e9e4ff"),
]

def reset_machine(program_text):
    st.session_state.registers = {"R1": 0, "R2": 0}
    st.session_state.memory = {20: 0, 21: 0, 22: 0}
    st.session_state.pc = 0
    st.session_state.stage = 0
    st.session_state.ir = "—"
    st.session_state.decoded = "Waiting for instruction"
    st.session_state.history = []
    st.session_state.halted = False
    st.session_state.finished = False
    st.session_state.program_snapshot = program_text

def parse_program(text):
    result = []
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        line = re.sub(r"\s+", " ", line.upper())
        result.append((line_number, line))
    return result

def record(stage_name, message):
    st.session_state.history.insert(
        0, {"stage": stage_name, "message": message}
    )

def execute_instruction(instruction):
    """Execute one supported instruction."""
    registers = st.session_state.registers
    memory = st.session_state.memory

    parts = instruction.replace(",", " ").split()
    if not parts:
        return "Empty instruction"

    opcode = parts[0]

    if opcode == "HALT":
        if len(parts) != 1:
            raise ValueError("Use HALT without operands.")
        st.session_state.halted = True
        return "HALT: execution stop requested."

    if opcode in ("LOAD", "MOV"):
        if len(parts) != 3:
            raise ValueError(f"Use {opcode} destination, value.")
        dest, source = parts[1], parts[2]
        if dest not in REGISTER_NAMES:
            raise ValueError("Destination must be R1 or R2.")

        if opcode == "LOAD":
            # LOAD R1, 05 loads the immediate value 5.
           value = parse_number(source)
            elif opcode == "MOV":
    value = parse_number(source)
    registers[dest] = value
            return f"{dest} ← {value}"

        # MOV accepts a register or a number.
        if source in REGISTER_NAMES:
            value = registers[source]
        else:
            value = int(source, 0)
        registers[dest] = value
        return f"{dest} ← {value}"

    if opcode in ("ADD", "SUB"):
        if len(parts) != 3:
            raise ValueError(f"Use {opcode} destination, source.")
        dest, source = parts[1], parts[2]
        if dest not in REGISTER_NAMES or source not in REGISTER_NAMES:
            raise ValueError("ADD and SUB require R1/R2 registers.")
        if opcode == "ADD":
            registers[dest] += registers[source]
            symbol = "+"
        else:
            registers[dest] -= registers[source]
            symbol = "−"
        return f"{dest} ← {dest} {symbol} {source} = {registers[dest]}"

    if opcode == "STORE":
        if len(parts) != 3:
            raise ValueError("Use STORE register, address.")
        source, address_text = parts[1], parts[2]
        if source not in REGISTER_NAMES:
            raise ValueError("STORE source must be R1 or R2.")
        value = parse_number(address_text)
        memory[address] = registers[source]
        return f"Memory[{address}] ← {registers[source]}"

    raise ValueError(
        f"Unknown instruction '{opcode}'. "
        "Supported: LOAD, STORE, ADD, SUB, MOV, HALT."
    )

def step_stage(program):
    """Advance exactly one stage of the instruction cycle."""
    if st.session_state.finished or st.session_state.halted:
        st.session_state.finished = True
        return

    pc = st.session_state.pc
    stage = st.session_state.stage

    if pc >= len(program):
        st.session_state.finished = True
        record("DONE", "All instructions have been processed.")
        return

    line_number, instruction = program[pc]
    stage_name = STAGES[stage][1].title()

    try:
        if stage == 0:  # FETCH
            st.session_state.ir = instruction
            st.session_state.decoded = "Waiting for decode"
            message = f"Fetched: {instruction}"
            record(stage_name, message)

        elif stage == 1:  # DECODE
            st.session_state.decoded = instruction
            message = f"Decoded: {instruction}"
            record(stage_name, message)

        elif stage == 2:  # EXECUTE
            message = execute_instruction(instruction)
            record(stage_name, f"{instruction} → {message}")

        else:  # UPDATE
            st.session_state.pc += 1
            message = f"Program Counter → {st.session_state.pc}"
            record(stage_name, message)
            st.session_state.stage = 0

            if st.session_state.halted or st.session_state.pc >= len(program):
                st.session_state.finished = True
                record("DONE", "Program execution completed.")
            return

        st.session_state.stage += 1

    except (ValueError, IndexError) as error:
        st.session_state.error_message = (
            f"Line {line_number}: {error}"
        )
        st.session_state.finished = True
        record("ERROR", st.session_state.error_message)

def run_program(program):
    max_steps = len(program) * 4 + 4
    for _ in range(max_steps):
        if st.session_state.finished:
            break
        step_stage(program)

# ---------- INITIALIZE STATE ----------
if "registers" not in st.session_state:
    st.session_state.error_message = ""
    st.session_state.program_text = PROGRAMS["Beginner: Load, Add and Store"]
    reset_machine(st.session_state.program_text)

if "error_message" not in st.session_state:
    st.session_state.error_message = ""

# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <div style="font-size:2rem">💜 🖥️ ✨</div>
    <h1>Instruction Cycle Simulator</h1>
    <p>Computer Organization and Architecture · Learn how a CPU thinks, one stage at a time.</p>
    <p>🌷 Fetch → Decode → Execute → Update 🌷</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "📘 Learning mode: advance one stage at a time, "
    "observe register and memory changes, and follow the execution history."
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🎨 Control Centre")
    st.markdown("Choose a sample program or edit the instructions.")
    selected_example = st.selectbox(
        "📚 Example programs",
        list(PROGRAMS.keys()),
        key="example_choice",
    )

    if st.button("Load selected example", use_container_width=True):
        st.session_state.program_text = PROGRAMS[selected_example]
        reset_machine(st.session_state.program_text)
        st.session_state.error_message = ""
        st.rerun()

    st.markdown("---")
    st.markdown("### 📖 Instruction Guide")
    st.markdown("**LOAD R1, 05** — Put value 5 into R1.")
    st.markdown("**MOV R2, R1** — Copy R1 into R2.")
    st.markdown("**ADD R1, R2** — Add R2 to R1.")
    st.markdown("**SUB R1, R2** — Subtract R2 from R1.")
    st.markdown("**STORE R1, 20** — Save R1 at memory address 20.")
    st.markdown("**HALT** — Stop the program.")
    st.markdown("---")
    st.markdown("### 💡 How to use")
    st.markdown("1. Choose or edit a program.")
    st.markdown("2. Execute one stage at a time.")
    st.markdown("3. Observe registers and memory.")
    st.markdown("4. Reset to start again.")

# ---------- PROGRAM EDITOR ----------
st.markdown('<div class="section-title">📝 Your Instruction Program</div>',
            unsafe_allow_html=True)

st.caption(
    "Write one instruction per line. Values such as 05 are decimal. "
    "Use # to add a comment."
)

program_text = st.text_area(
    "Program instructions",
    key="program_text",
    height=150,
    help="Supported instructions: LOAD, STORE, ADD, SUB, MOV, HALT.",
)

if program_text != st.session_state.program_snapshot:
    reset_machine(program_text)
    st.session_state.error_message = ""

program = parse_program(program_text)

# ---------- STAGE CARDS ----------
st.markdown('<div class="section-title">🔄 The Four Stages</div>',
            unsafe_allow_html=True)

stage_columns = st.columns(4)
for index, (icon, name, description, color) in enumerate(STAGES):
    active_class = (
        "stage-card stage-active"
        if index == st.session_state.stage and not st.session_state.finished
        else "stage-card"
    )
    status = (
        "✨ CURRENT STAGE"
        if index == st.session_state.stage and not st.session_state.finished
        else "READY"
    )
    with stage_columns[index]:
        st.markdown(
            f"""
            <div class="{active_class}" style="background:{color}">
                <div class="stage-icon">{icon}</div>
                <h3>{name}</h3>
                <p>{description}</p>
                <p><b>{status}</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------- PROGRESS ----------
st.markdown('<div class="section-title">📈 Execution Progress</div>',
            unsafe_allow_html=True)

total_stages = max(1, len(program) * 4)
completed_stages = min(
    total_stages,
    st.session_state.pc * 4 + st.session_state.stage
)
if st.session_state.finished:
    completed_stages = total_stages

progress = completed_stages / total_stages
st.progress(progress)
st.caption(
    f"{completed_stages} of {total_stages} stage steps completed · "
    f"Program Counter (PC): {st.session_state.pc}"
)

if st.session_state.finished:
    st.success("🎉 Program completed! Press Reset Simulator to run it again.")

if st.session_state.error_message:
    st.error(st.session_state.error_message)

# ---------- MAIN DASHBOARD ----------
left, right = st.columns([1.05, 1.2], gap="large")

with left:
    st.markdown('<div class="section-title">🧩 CPU Control</div>',
                unsafe_allow_html=True)

    current_instruction = (
        program[st.session_state.pc][1]
        if st.session_state.pc < len(program)
        else "No instruction remaining"
    )

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("**📍 Current Instruction**")
    st.code(current_instruction, language="text")
    st.markdown("**📥 Instruction Register (IR)**")
    st.code(st.session_state.ir, language="text")
    st.markdown("**🧠 Decoded Instruction**")
    st.write(st.session_state.decoded)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 💎 CPU Registers")
    r1_col, r2_col = st.columns(2)
    with r1_col:
        st.markdown(
            f"""<div class="metric-card">
            <div class="metric-label">REGISTER R1</div>
            <div class="metric-value">{st.session_state.registers['R1']}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with r2_col:
        st.markdown(
            f"""<div class="metric-card">
            <div class="metric-label">REGISTER R2</div>
            <div class="metric-value">{st.session_state.registers['R2']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("### 🗄️ Memory")
    memory = st.session_state.memory
    if memory:
        memory_columns = st.columns(min(3, len(memory)))
        for i, (address, value) in enumerate(sorted(memory.items())):
            with memory_columns[i % len(memory_columns)]:
                st.markdown(
                    f"""<div class="metric-card">
                    <div class="metric-label">ADDRESS {address}</div>
                    <div class="metric-value">{value}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No memory addresses have been written yet.")

with right:
    st.markdown('<div class="section-title">🚀 Run the Simulator</div>',
                unsafe_allow_html=True)

    stage_labels = ["Fetch", "Decode", "Execute", "Update"]
    current_stage_label = (
        stage_labels[st.session_state.stage]
        if not st.session_state.finished else "Completed"
    )

    st.markdown(
        f"""<div class="panel">
        <b>Current stage:</b> {current_stage_label}<br>
        <span class="small-note">Click once to advance one stage.</span>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.button(
        "✨ Execute Next Stage",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.finished or not program,
    ):
        step_stage(program)
        st.rerun()

    if st.button(
        "⚡ Run Complete Program",
        use_container_width=True,
        disabled=st.session_state.finished or not program,
    ):
        run_program(program)
        st.rerun()

    if st.button("🔄 Reset Simulator",
                 use_container_width=True):
        reset_machine(program_text)
        st.session_state.error_message = ""
        st.rerun()

    st.markdown("### 💡 What happens in each stage?")
    explanations = [
        ("🔍 Fetch", "The CPU reads the instruction at the current PC."),
        ("🧠 Decode", "The control unit identifies the operation and operands."),
        ("⚙️ Execute", "The CPU performs the requested operation."),
        ("🔄 Update", "The PC advances to the next instruction."),
    ]
    for title, description in explanations:
        with st.expander(title):
            st.write(description)

# ---------- EXECUTION HISTORY ----------
st.markdown("---")
st.markdown('<div class="section-title">📜 Execution History</div>',
            unsafe_allow_html=True)

if st.session_state.history:
    for item in st.session_state.history[:30]:
        st.markdown(
            f"""<div class="instruction">
            <b>{item['stage']}</b> &nbsp; · &nbsp; {item['message']}
            </div>""",
            unsafe_allow_html=True,
        )
    if len(st.session_state.history) > 30:
        st.caption("Showing the latest 30 history entries.")
else:
    st.info("Your execution history will appear here when you start.")

st.markdown("""
<div style="text-align:center;padding:24px;color:#777397">
    💜 Instruction Cycle Simulator · COA Engineering Project<br>
    <span class="small-note">Small simulation, big understanding ✨</span>
</div>
""", unsafe_allow_html=True)
