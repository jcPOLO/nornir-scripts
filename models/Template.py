class Template:
    def __init__(self, prompt, template, answer=False):
        self.prompt = prompt
        self.answer = answer
        self.template = template

    def __str__(self):
        return self.prompt
