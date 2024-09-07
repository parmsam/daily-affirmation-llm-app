from shiny import App, reactive, render, ui
from openai import OpenAI
import os
import base64
from gtts import gTTS

try:
    from setup import api_key1
except ImportError:
    api_key1 = os.getenv("OPENAI_API_KEY")
    
app_info = """
This app creates a daily affirmation using the OpenAI API based on a theme and
optional character. 
"""

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
                    "Dwight Schrute",
                    "Michael Scott",
                    "Ron Swanson",
                    "Eric Cartman", 
                    "Yoda",
                    "Chewbacca",
                    "R2-D2",
                    "Grogu",
                    "Groot",
                    "Donald Trump",
                    "Stewie Griffin",
                    "Peter Griffin",
                    "Chandler Bing",
                    "Dr. Gregory House",
                    "George Costanza",
                    "Kramer",
                    "Elon Musk",
                    "Borat",
                    "Kim Kardashian",
                ],
                selected=""
            ),
            ui.input_action_button("generate", "Generate Affirmation"),
            open="open",
        ),
        ui.h3("Your Daily Self-Affirmation"),
        # ui.markdown(app_info),
        ui.output_text("affirmation_output"),
        ui.input_action_button("speak", "Speak"),
        ui.output_ui("audio_output"),
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
            # Clear the audio file
            if os.path.exists("speech.mp3"):
                os.remove("speech.mp3")
                # remove the audio tag from the UI
                
        except Exception as e:
            ui.notification_show(f"Error: {str(e)}", type="error")

    @output
    @render.text
    def affirmation_output():
        return affirmation()
    
    @reactive.Effect
    @reactive.event(input.speak)
    def speak_text():
        text = affirmation.get()
        if text == "":
            text = "You have not generated an affirmation yet."
        if text:
            # replace " with nothing to avoid issues with the TTS"
            text = text.replace('"', "")
            tts = gTTS(text=text, lang='en')
            tts.save("speech.mp3")
            
    @render.ui
    @reactive.event(input.speak, input.generate)
    def audio_output():
        if os.path.exists("speech.mp3"):
            with open("speech.mp3", "rb") as audio_file:
                encoded = base64.b64encode(audio_file.read()).decode()
            return ui.tags.audio(
                ui.tags.source(src=f"data:audio/mp3;base64,{encoded}", type="audio/mp3"),
                controls=True
            )
        return ui.p("Click 'Speak' to hear the text.")

app = App(app_ui, server)
