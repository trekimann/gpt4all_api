from pyllamacpp.model import Model

class LLM_API:
    def __init__(self, model_dir = './models/gpt4all-lora-quantized-ggml.bin', n_ctx=512):
        self.model_dir = model_dir
        self.n_ctx = n_ctx
        self.model = None

    def load_model(self, model_path):
        self.model = Model(ggml_model=model_path, n_ctx=self.n_ctx)

    def generate_text(self, prompt, n_predict=55, n_threads=8, new_text_callback=None):
        if self.model is not None:
            return self.model.generate(prompt, n_predict=n_predict, n_threads=n_threads, new_text_callback=new_text_callback)
        else:
            raise ValueError("No model loaded.")
