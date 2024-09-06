from shiny import App, reactive, render, ui
from openai import OpenAI
import os

try:
    from setup import api_key1
except ImportError:
    api_key1 = os.getenv("OPENAI_API_KEY")

app_ui = ui.page_fluid(
    ui.h1("Daily Morning Affirmation Generator"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_password(
                "api_key", 
                "OpenAI API Key",
                value = api_key1,
            ),
            ui.input_select(
                "theme", 
                "Affirmation Theme", 
                choices=[
                    "Motivation", 
                    "Self-Love", 
                    "Focus", 
                    "Confidence", 
                    "Gratitude",
                ],
            ),
            ui.input_select(
                "character",
                "Character",
                choices=[
                    "",
                    "Marvin the Paranoid Android",
                    "Ron Swanson",
                    "Eric Cartman", 
                    "Dwight Schrute",
                    "Michael Scott",
                    "Donald Trump",
                ],
                selected=""
            ),
            ui.input_action_button("generate", "Generate Affirmation"),
            open="open",
        ),
        ui.h3("Your Daily Affirmation"),
        ui.output_text("affirmation_output"),
    )
)

def server(input, output, session):
    affirmation = reactive.Value("")

    @reactive.Effect
    @reactive.event(input.generate)
    def generate_affirmation():
        api_key = input.api_key()
        if not api_key:
            ui.notification_show("Please enter your OpenAI API key.", type="error")
            return

        client = OpenAI(api_key=api_key)
        theme = input.theme()

        prompt = f"""Generate a short, personalized 
        daily affirmation on the following theme: {theme}."""
        
        if input.character() != "" and input.character() is not None:
            character = input.character()
            prompt = f"""{prompt}.
            The affirmation should be in the style of {character}."""
        prompt = f"""{prompt}.
        The affirmation should be positive, empowering, 
        and no longer than two sentences.
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a highly 
                     proficient assistant tasked with providing 
                     positive affirmations."""},
                    {"role": "user", "content": prompt,},
                ]
            )
            response_data = response.choices[0].message.content
            affirmation.set(response_data)
        except Exception as e:
            ui.notification_show(f"Error: {str(e)}", type="error")

    @output
    @render.text
    def affirmation_output():
        return affirmation()

app = App(app_ui, server)
