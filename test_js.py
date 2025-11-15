import gradio as gr

def say_hello(name):
    return f"Hello, {name}!"

with gr.Blocks() as demo:
    name_input = gr.Textbox(label="Enter your name")
    output = gr.Textbox(label="Greeting")
    btn = gr.Button("Greet")
    
    btn.click(
        fn=say_hello,
        inputs=name_input,
        outputs=output,
        _js="() => { alert('Button clicked!'); }"
    )

demo.launch()