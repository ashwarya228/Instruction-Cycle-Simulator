import streamlit as st

st.set_page_config(
    page_title="Instruction Cycle Simulator",
    page_icon="💻",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #fce7f3, #e0f7fa);
    color: #20264a;
}
h1, h2, h3 {
    color: #373078;
}
div.stButton > button {
    background-color: #7868e6;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 22px;
}
div.stButton > button:hover {
    background-color: #5144b5;
    color: white;
}
.panel {
    background: rgba(255,255,255,0.85);
    border: 2px solid #d9d5ff;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("💻 Instruction Cycle Simulator")
st.markdown("### ✨ Computer Organization and Architecture")
st.write("Explore how a CPU fetches, decodes, executes and completes instructions.")

st.info("📚 Learning mode: Follow each instruction through the four stages.")

if "pc" not in st.session_state:
    st.session_state.pc = 0
    st.session_state.r1 = 0
    st.session_state.r2 = 5
    st.session_state.memory = {20: 0}
    st.session_state.stage = 0
    st.session_state.history = []

stages = ["📥 Fetch", "🧠 Decode", "⚙️ Execute", "🔄 Update"]
instructions = ["LOAD R1, 05", "ADD R1, R2", "STORE R1, 20", "SUB R1, R2", "HALT"]

st.markdown("## 🔄 The Four Stages")
cols = st.columns(4)
for col, stage in zip(cols, stages):
    col.markdown(
        f"<div class='panel' style='text-align:center'><h3>{stage}</h3></div>",
        unsafe_allow_html=True
    )

left, right = st.columns([1, 1])

with left:
    st.markdown("## 🎛️ CPU Control")
    st.metric("Program Counter (PC)", st.session_state.pc)
    st.metric("Current Stage", stages[st.session_state.stage])
    current = min(st.session_state.pc, len(instructions) - 1)
    st.code(instructions[current], language="text")
    st.write("**Register R1:**", st.session_state.r1)
    st.write("**Register R2:**", st.session_state.r2)
    st.write("**Memory[20]:**", st.session_state.memory[20])

with right:
    st.markdown("## 📖 Instruction Guide")
    st.write("**LOAD** — Load a value into a register.")
    st.write("**ADD** — Add two register values.")
    st.write("**STORE** — Save a register value to memory.")
    st.write("**SUB** — Subtract one register value from another.")
    st.write("**HALT** — Stop program execution.")

    st.markdown("## 🪄 Run the Simulator")
    if st.button("▶️ Execute Next Stage", use_container_width=True):
        if st.session_state.pc >= len(instructions):
            st.success("Program completed! 🎉")
        else:
            instruction = instructions[st.session_state.pc]
            stage = st.session_state.stage

            if stage == 0:
                message = f"Fetched: {instruction}"
            elif stage == 1:
                message = f"Decoded: {instruction}"
            elif stage == 2:
                if instruction == "LOAD R1, 05":
                    st.session_state.r1 = 5
                    message = "Loaded 5 into R1."
                elif instruction == "ADD R1, R2":
                    st.session_state.r1 += st.session_state.r2
                    message = "Added R2 to R1."
                elif instruction == "STORE R1, 20":
                    st.session_state.memory[20] = st.session_state.r1
                    message = "Stored R1 in Memory[20]."
                elif instruction == "SUB R1, R2":
                    st.session_state.r1 -= st.session_state.r2
                    message = "Subtracted R2 from R1."
                else:
                    message = "HALT: Program stopped."
            else:
                message = "Program counter updated."

            st.session_state.history.append(
                f"{stages[stage]} — {message}"
            )

            if stage == 3:
                st.session_state.stage = 0
                st.session_state.pc += 1
            else:
                st.session_state.stage += 1

            st.rerun()

    if st.button("🔄 Reset Simulator", use_container_width=True):
        for key in ["pc", "r1", "r2", "memory", "stage", "history"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.markdown("## 📝 Execution History")
if st.session_state.history:
    for item in reversed(st.session_state.history):
        st.write("✨", item)
else:
    st.write("Your instruction execution history will appear here.")

st.markdown("---")
st.markdown(
    "<div style='text-align:center'>💜 Made for Engineering Students | "
    "Learn COA One Instruction at a Time 💜</div>",
    unsafe_allow_html=True
)
