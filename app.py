import streamlit as st

st.set_page_config(page_title="Instruction Cycle Simulator", page_icon="💜", layout="wide")

st.markdown("""
<style>
.stApp {background:linear-gradient(135deg,#fffaf5,#f2efff,#eef8ff);color:#252442}
.block-container{padding-top:2rem;padding-bottom:2rem}
h1,h2,h3,h4,h5,h6{color:#29264b!important}
.stApp p,.stApp li,.stApp label{color:#302e4a}
.hero{background:linear-gradient(120deg,#e8dcff,#dcefff);padding:28px;border-radius:24px;border:1px solid #d3c6f0;margin-bottom:20px;color:#29264b}
.hero h1,.hero p,.hero div{color:#29264b!important}
.stage-card{background:#fff;color:#29264b;border:1px solid #d6ccef;border-radius:16px;padding:16px;min-height:135px;margin-bottom:10px}
.stage-card h4,.stage-card p{color:#29264b!important}
.stage-active{background:#e9e1ff;border:2px solid #7961c5}
.info-card{background:#fff;color:#29264b;padding:18px;border-radius:16px;border:1px solid #d6ccef;text-align:center}
.info-card p,.info-card h2{color:#29264b!important}
.stTextArea textarea,.stTextInput input{background:#fff!important;color:#252442!important;-webkit-text-fill-color:#252442!important;border:1px solid #bcb0df!important;caret-color:#252442!important}
.stSelectbox div,.stSelectbox input{color:#252442!important}
.stButton button{background:#e6ddff;color:#29264b!important;border:1px solid #b9a9e5;border-radius:12px;font-weight:600}
.stButton button:hover{background:#d7c9ff;border-color:#7961c5}
[data-testid="stDataFrame"]{background:#fff;color:#252442!important}
[data-testid="stExpander"]{background:#fff;border:1px solid #d6ccef;border-radius:12px}
</style>
""", unsafe_allow_html=True)

REGISTERS = ("R1", "R2")
EXAMPLES = {
    "Beginner: Load, Add and Store": "LOAD R1, 05\nLOAD R2, 03\nADD R1, R2\nSTORE R1, 20\nHALT",
    "Subtraction Example": "LOAD R1, 09\nLOAD R2, 04\nSUB R1, R2\nSTORE R1, 20\nHALT",
    "Move Example": "LOAD R1, 07\nMOV R2, R1\nADD R1, R2\nSTORE R1, 21\nHALT",
}
STAGES = [
    ("📥 Fetch", "Fetch the next instruction."),
    ("🔎 Decode", "Understand the operation and operands."),
    ("⚙️ Execute", "Perform the CPU operation."),
    ("🔄 Update", "Update the program counter."),
]

def parse_number(value):
    value = value.strip()
    if value.lower().startswith(("0x", "0b")):
        return int(value, 0)
    return int(value, 10)

def get_instructions(program):
    result = []
    for line_no, line in enumerate(program.splitlines(), 1):
        line = line.strip()
        if line and not line.startswith("#"):
            result.append({"line": line_no, "text": line})
    return result

def decode_instruction(text):
    parts = text.replace(",", " ").split()
    if not parts:
        raise ValueError("Empty instruction.")
    opcode, operands = parts[0].upper(), parts[1:]
    if opcode in ("LOAD", "MOV", "ADD", "SUB", "STORE"):
        if len(operands) != 2:
            raise ValueError(f"{opcode} requires two operands.")
    elif opcode == "HALT":
        if operands:
            raise ValueError("HALT takes no operands.")
    else:
        raise ValueError(f"Unknown instruction: {opcode}")
    if opcode in ("LOAD", "MOV", "ADD", "SUB"):
        if operands[0].upper() not in REGISTERS:
            raise ValueError(f"Destination must be R1 or R2 in {opcode}.")
        operands[0] = operands[0].upper()
    if opcode == "STORE":
        if operands[0].upper() not in REGISTERS:
            raise ValueError("STORE source must be R1 or R2.")
        operands[0] = operands[0].upper()
    return opcode, operands

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

def init_state():
    defaults = {
        "registers": {"R1": 0, "R2": 0}, "memory": {20: 0, 21: 0, 22: 0},
        "pc": 0, "stage_index": 0, "decoded": None, "current_instruction": "",
        "history": [], "error": "", "finished": False, "halted": False,
        "status": "Ready to execute", "program_snapshot": EXAMPLES["Beginner: Load, Add and Store"],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

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
    text = current["text"]
    try:
        if stage == 0:
            st.session_state.current_instruction = text
            st.session_state.decoded = None
            st.session_state.history.insert(0, {"Stage":"Fetch","Instruction":text,"Details":f"Fetched instruction at line {current['line']}"})
            st.session_state.status = "Instruction fetched"
            st.session_state.stage_index = 1
        elif stage == 1:
            opcode, operands = decode_instruction(text)
            st.session_state.decoded = (opcode, operands)
            st.session_state.history.insert(0, {"Stage":"Decode","Instruction":text,"Details":f"Decoded operation: {opcode}"})
            st.session_state.status = "Instruction decoded"
            st.session_state.stage_index = 2
        elif stage == 2:
            if st.session_state.decoded is None:
                raise ValueError("Fetch and decode the instruction first.")
            opcode, operands = st.session_state.decoded
            regs, mem = st.session_state.registers, st.session_state.memory
            if opcode == "LOAD":
                dest, source = operands
                value = parse_number(source)
                regs[dest] = value
                details = f"{dest} loaded with {value}"
            elif opcode == "MOV":
                dest, source = operands
                value = regs[source.upper()] if source.upper() in REGISTERS else parse_number(source)
                regs[dest] = value
                details = f"{value} moved into {dest}"
            elif opcode == "ADD":
                dest, source = operands
                regs[dest] += regs[source.upper()]
                details = f"{dest} = {regs[dest]}"
            elif opcode == "SUB":
                dest, source = operands
                regs[dest] -= regs[source.upper()]
                details = f"{dest} = {regs[dest]}"
            elif opcode == "STORE":
                source, addr_text = operands
                address = parse_number(addr_text)
                if not 0 <= address <= 255:
                    raise ValueError("Memory address must be between 0 and 255.")
                mem[address] = regs[source]
                details = f"Stored {regs[source]} at memory address {address}"
            else:  # HALT
                st.session_state.halted = True
                details = "HALT instruction executed"
            st.session_state.history.insert(0, {"Stage":"Execute","Instruction":text,"Details":details})
            st.session_state.status = details
            st.session_state.stage_index = 3
        elif stage == 3:
            st.session_state.history.insert(0, {"Stage":"Update","Instruction":text,"Details":f"Program counter: {st.session_state.pc} → {st.session_state.pc + 1}"})
            st.session_state.pc += 1
            if st.session_state.halted:
                st.session_state.finished = True
                st.session_state.status = "Program completed successfully"
            elif st.session_state.pc >= len(instructions):
                st.session_state.finished = True
                st.session_state.status = "Program completed"
            st.session_state.stage_index = 0
            st.session_state.decoded = None
    except (ValueError, OverflowError) as exc:
        st.session_state.error = f"Line {current['line']}: {exc}"
        st.session_state.status = "Execution stopped because of an error"
        st.session_state.finished = True
        st.session_state.history.insert(0, {"Stage":"Error","Instruction":text,"Details":st.session_state.error})

def run_program():
    for _ in range(500):
        if st.session_state.finished:
            break
        advance_stage()

init_state()
st.markdown("""
<div class="hero">
<div style="font-size:30px;">💜 💻 ✨</div>
<h1>Instruction Cycle Simulator</h1>
<p style="font-size:17px;">Computer Organization and Architecture</p>
<p>Understand how a CPU processes instructions, one stage at a time.</p>
<p>🌷 Fetch → Decode → Execute → Update 🌷</p>
</div>
""", unsafe_allow_html=True)
st.info("📘 Learning mode: advance through CPU stages, observe register and memory changes, and review execution history.")

st.subheader("📝 Your Instruction Program")
if "program_text" not in st.session_state:
    st.session_state.program_text = EXAMPLES["Beginner: Load, Add and Store"]
choice = st.selectbox("Choose a sample program", list(EXAMPLES.keys()))
if st.button("📚 Load Selected Example"):
    st.session_state.program_text = EXAMPLES[choice]
    reset_machine(st.session_state.program_text)
    st.rerun()
program = st.text_area("Enter one instruction per line", key="program_text", height=145,
                       help="Supported instructions: LOAD, MOV, ADD, SUB, STORE, HALT.")
if st.session_state.program_snapshot != program:
    reset_machine(program)
st.session_state.program_snapshot = program

st.subheader("🔄 The Four Stages")
cols = st.columns(4)
for i, (title, desc) in enumerate(STAGES):
    cls = "stage-card stage-active" if i == st.session_state.stage_index and not st.session_state.finished else "stage-card"
    with cols[i]:
        st.markdown(f'<div class="{cls}"><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)
if st.session_state.finished:
    st.progress(1.0, text="Execution finished")
else:
    st.progress(st.session_state.stage_index / 4, text=f"Current stage: {STAGES[st.session_state.stage_index][0]}")
if st.session_state.finished and not st.session_state.error:
    st.success("🎉 " + st.session_state.status)
elif st.session_state.status != "Ready to execute":
    st.info(st.session_state.status)
if st.session_state.error:
    st.error(st.session_state.error)

left, right = st.columns(2)
with left:
    st.subheader("🧩 CPU Control")
    st.markdown(f"**Program Counter (PC):** {st.session_state.pc}")
    st.markdown("**Current instruction:** " + (st.session_state.current_instruction or "Waiting for fetch"))
    st.markdown(f"**Status:** {st.session_state.status}")
with right:
    st.subheader("🚀 Run the Simulator")
    if st.button("▶️ Execute Next Stage", use_container_width=True, disabled=st.session_state.finished):
        advance_stage()
        st.rerun()
    if st.button("⏩ Run Complete Program", use_container_width=True, disabled=st.session_state.finished):
        run_program()
        st.rerun()
    if st.button("🔄 Reset Simulator", use_container_width=True):
        reset_machine(st.session_state.program_text)
        st.rerun()

st.subheader("📊 CPU Registers")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="info-card"><p>REGISTER R1</p><h2>{st.session_state.registers["R1"]}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="info-card"><p>REGISTER R2</p><h2>{st.session_state.registers["R2"]}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="info-card"><p>PROGRAM COUNTER</p><h2>{st.session_state.pc}</h2></div>', unsafe_allow_html=True)

st.subheader("🗃️ Memory")
mem_cols = st.columns(3)
for col, address in zip(mem_cols, (20, 21, 22)):
    with col:
        st.markdown(f'<div class="info-card"><p>ADDRESS {address}</p><h2>{st.session_state.memory.get(address, 0)}</h2></div>', unsafe_allow_html=True)

st.subheader("📜 Execution History")
if st.session_state.history:
    st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
else:
    st.caption("Your execution steps will appear here.")

st.subheader("💡 Instruction Guide")
with st.expander("View supported instructions"):
    st.markdown("""
- `LOAD R1, 05` — Load the value 5 into R1.
- `MOV R2, R1` — Copy the value of R1 into R2.
- `ADD R1, R2` — Add R2 to R1 and store the result in R1.
- `SUB R1, R2` — Subtract R2 from R1 and store the result in R1.
- `STORE R1, 20` — Store R1's value at memory address 20.
- `HALT` — Stop the program.

Decimal values such as `05`, hexadecimal values such as `0x10`, and binary values such as `0b1010` are supported.
""")
st.markdown("""
<hr>
<div style="text-align:center;color:#514b6c;">
💜 Instruction Cycle Simulator · COA Engineering Project<br>
<small>Small simulation, big understanding ✨</small>
</div>
""", unsafe_allow_html=True)

  
