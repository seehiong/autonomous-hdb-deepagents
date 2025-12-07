import gradio as gr
import asyncio
from autonomous_hdb_deepagents.agent.cli import run_cli

# ---------------------------------------------------------
# ASYNC-SAFE AGENT CALLER
# ---------------------------------------------------------
async def query_agent_async(message: str):
    try:
        return await run_cli(message)
    except Exception as e:
        return f"❌ Error: {e}"


# ---------------------------------------------------------
# ENHANCED CSS (modern, minimal, full-height)
# ---------------------------------------------------------
CUSTOM_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }

body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); font-family: 'Segoe UI', system-ui, sans-serif; }

.gradio-container { 
    padding: 0 !important; 
    margin: 0 !important; 
    max-width: 100% !important;
    height: 100vh !important;
    background: transparent !important;
}

#main-container { 
    height: 100vh; 
    display: flex; 
    flex-direction: column;
    gap: 0;
}

#header-section {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    padding: 20px 24px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    flex-shrink: 0;
}

#header-section h1 {
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}

#header-section p {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 4px;
}

#samples-section {
    padding: 16px 24px;
    background: rgba(15, 23, 42, 0.5);
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    flex-shrink: 0;
    overflow-x: auto;
    overflow-y: hidden;
}

#samples-section > div:first-child {
    display: none;
}

.samples-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 8px;
    width: 100%;
}

.sample-btn {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(14, 165, 233, 0.1) 100%) !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    color: #38bdf8 !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    text-align: left !important;
    white-space: normal !important;
    height: auto !important;
    min-height: 44px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
}

.sample-btn:hover {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(14, 165, 233, 0.2) 100%) !important;
    border-color: #38bdf8 !important;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2) !important;
    transform: translateY(-2px);
}

.sample-btn:active {
    transform: translateY(0);
}

#chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
}

#chatbox {
    flex: 1 !important;
    height: auto !important;
    overflow-y: auto !important;
    padding: 24px !important;
    background: transparent !important;
    border: none !important;
}

#chatbox .message {
    margin-bottom: 16px;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

#chatbox .message.user {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%);
    border-left: 3px solid #38bdf8;
}

#chatbox .message.assistant {
    background: rgba(30, 41, 59, 0.5);
    border-left: 3px solid #0ea5e9;
}

/* Custom scrollbar */
#chatbox::-webkit-scrollbar { width: 8px; }
#chatbox::-webkit-scrollbar-track { background: rgba(148, 163, 184, 0.1); border-radius: 4px; }
#chatbox::-webkit-scrollbar-thumb { 
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
    border-radius: 4px;
}
#chatbox::-webkit-scrollbar-thumb:hover { background: #0ea5e9; }

#input-section {
    padding: 20px 24px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%);
    border-top: 1px solid rgba(148, 163, 184, 0.1);
    flex-shrink: 0;
    backdrop-filter: blur(10px);
}

#input-row {
    display: flex;
    gap: 12px;
    align-items: flex-end;
}

#msg-input {
    flex: 1 !important;
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1.5px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
}

#msg-input:focus {
    border-color: #38bdf8 !important;
    background: rgba(15, 23, 42, 0.9) !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1) !important;
}

#msg-input::placeholder {
    color: #64748b !important;
}

.submit-btn {
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
    border: none !important;
    color: #0f172a !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-size: 14px !important;
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3) !important;
}

.submit-btn:hover {
    box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4) !important;
    transform: translateY(-2px);
}

.submit-btn:active {
    transform: translateY(0);
}

/* Hide label text for better space */
#msg-input label { display: none !important; }

/* Message styling for better readability */
.prose { color: #e2e8f0; }
.prose code { background: rgba(148, 163, 184, 0.1); color: #38bdf8; padding: 2px 6px; border-radius: 4px; }
"""


# ---------------------------------------------------------
# NORMAL CHAT RESPONSE
# ---------------------------------------------------------
async def respond(message, history):
    history = history or []
    history.append({"role": "user", "content": message})

    reply = await query_agent_async(message)
    history.append({"role": "assistant", "content": reply})

    return history, ""


# ---------------------------------------------------------
# SAMPLE QUESTION → auto-fire with instant display
# ---------------------------------------------------------
async def sample_fire(question, history):
    history = history or []
    
    # Add user question
    history.append({"role": "user", "content": question})
    
    # Fetch and add response
    reply = await query_agent_async(question)
    history.append({"role": "assistant", "content": reply})
    
    return history, ""


# ---------------------------------------------------------
# GRADIO UI
# ---------------------------------------------------------
with gr.Blocks(title="HDB DeepAgent Chat", elem_id="main-container") as demo:
    demo.css = CUSTOM_CSS

    # Header
    with gr.Group(elem_id="header-section"):
        gr.Markdown("# 🏢 **Autonomous HDB DeepAgent**")
        gr.Markdown("Ask anything about HDB resale & MRT proximity")

    # Sample Questions
    with gr.Group(elem_id="samples-section"):
        samples = [
            "Find flats near Bukit Batok MRT",
            "Show me 4-room flats in Toa Payoh under 500k",
            "Which flats are within 400m of an MRT in Tampines?",
            "Find cheapest 5-room units near Punggol MRT",
            "Best value flats near Woodlands MRT under 600k",
            "Show 3-room flats in Bishan near MRT",
        ]

        with gr.Row(elem_classes="samples-grid"):
            sample_buttons = []
            for q in samples:
                btn = gr.Button(q, elem_classes="sample-btn", scale=1)
                sample_buttons.append((btn, q))

    # Chat Area
    with gr.Group(elem_id="chat-container"):
        chat = gr.Chatbot(elem_id="chatbox", height=600)

    # Input Section
    with gr.Group(elem_id="input-section"):
        with gr.Row(elem_id="input-row"):
            msg = gr.Textbox(
                placeholder="Ask something like: Find flats near Bukit Batok MRT",
                elem_id="msg-input",
                scale=10,
                show_label=False,
            )
            submit_btn = gr.Button("Send", elem_classes="submit-btn", scale=0)

    # Event Handlers
    msg.submit(respond, inputs=[msg, chat], outputs=[chat, msg])
    submit_btn.click(respond, inputs=[msg, chat], outputs=[chat, msg])

    # Sample buttons with streaming response
    for btn, question in sample_buttons:
        btn.click(
            sample_fire,
            inputs=[gr.State(question), chat],
            outputs=[chat, msg],
        )


# ---------------------------------------------------------
# LAUNCH SERVER
# ---------------------------------------------------------
demo.launch(server_name="0.0.0.0", server_port=7860)