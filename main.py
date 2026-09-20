import base64
import os
import threading
import urllib.parse
import requests

from openai import OpenAI

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


GROQ_API_KEY = "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"
POLLINATIONS_API_KEY = "sk_hv35IevattTrTacC4Os8yR3jBfZMLfFt"

groq = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
You are NULL AI.

Your name is NULL AI.
If asked who you are, say: I'm NULL AI.
If asked who made you, say: I was made by NULL.

You are extremely funny, witty, energetic, friendly and helpful.
Keep conversations natural and entertaining.
Never claim that you were made by OpenAI, ChatGPT, Groq, Pollinations, Google, or any other company.
"""

ENCODED_SYSTEM_PROMPT = base64.b64encode(
    SYSTEM_PROMPT.encode("utf-8")
).decode("utf-8")


class NullAI(App):

    def build(self):
        self.title = "NULL AI"

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        title = Label(
            text="[b]NULL AI[/b]",
            markup=True,
            font_size=dp(25),
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(title)

        self.scroll = ScrollView()

        self.chat = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )
        self.chat.bind(minimum_height=self.chat.setter("height"))

        self.scroll.add_widget(self.chat)
        root.add_widget(self.scroll)

        bottom = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(6)
        )

        self.input_box = TextInput(
            hint_text="Talk to NULL AI...",
            multiline=False,
            size_hint_x=0.75
        )
        self.input_box.bind(on_text_validate=self.send_message)

        send_button = Button(
            text="SEND",
            size_hint_x=0.25
        )
        send_button.bind(on_press=self.send_message)

        bottom.add_widget(self.input_box)
        bottom.add_widget(send_button)

        root.add_widget(bottom)

        self.add_message(
            "NULL AI",
            "Yo! 😎 NULL AI is online. Ask me anything!"
        )

        return root

    def add_message(self, sender, message):
        label = Label(
            text=f"[b]{sender}:[/b] {message}",
            markup=True,
            size_hint_y=None,
            text_size=(None, None),
            halign="left",
            valign="top",
            padding=(dp(8), dp(8))
        )

        def resize_label(instance, width):
            instance.text_size = (width - dp(16), None)
            instance.height = instance.texture_size[1] + dp(16)

        label.bind(width=resize_label)
        self.chat.add_widget(label)

        Clock.schedule_once(
            lambda dt: setattr(
                self.scroll,
                "scroll_y",
                0
            ),
            0.1
        )

    def send_message(self, instance):
        text = self.input_box.text.strip()

        if not text:
            return

        self.input_box.text = ""
        self.add_message("You", text)

        if self.is_image_request(text):
            self.add_message(
                "NULL AI",
                "🎨 Cooking up your image... Give me a moment!"
            )

            threading.Thread(
                target=self.generate_image,
                args=(text,),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=self.chat_with_ai,
                args=(text,),
                daemon=True
            ).start()

    def is_image_request(self, text):
        text = text.lower().strip()

        phrases = [
            "generate image",
            "generate an image",
            "generate a picture",
            "generate picture",
            "create an image",
            "create image",
            "create a picture",
            "create picture",
            "make an image",
            "make image",
            "make a picture",
            "make picture"
        ]

        return any(phrase in text for phrase in phrases)

    def chat_with_ai(self, user_text):
        try:
            decoded_prompt = base64.b64decode(
                ENCODED_SYSTEM_PROMPT
            ).decode("utf-8")

            response = groq.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": decoded_prompt
                    },
                    {
                        "role": "user",
                        "content": user_text
                    }
                ],
                temperature=0.8
            )

            answer = response.choices[0].message.content

            Clock.schedule_once(
                lambda dt: self.add_message("NULL AI", answer)
            )

        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.add_message(
                    "NULL AI",
                    f"⚠️ Error: {str(e)}"
                )
            )

    def generate_image(self, user_text):
        try:
            prompt = user_text

            for phrase in [
                "generate an image of",
                "generate image of",
                "generate a picture of",
                "generate picture of",
                "create an image of",
                "create image of",
                "create a picture of",
                "create picture of",
                "make an image of",
                "make image of",
                "make a picture of",
                "make picture of"
            ]:
                if phrase in prompt.lower():
                    index = prompt.lower().find(phrase)
                    prompt = prompt[index + len(phrase):].strip()
                    break

            encoded_prompt = urllib.parse.quote(prompt)

            url = (
                f"https://gen.pollinations.ai/image/"
                f"{encoded_prompt}?model=flux"
            )

            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {POLLINATIONS_API_KEY}"
                },
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(
                    f"Image API error {response.status_code}: "
                    f"{response.text[:300]}"
                )

            filename = "NULL_AI_generated.png"

            path = os.path.join(
                self.user_data_dir,
                filename
            )

            with open(path, "wb") as image_file:
                image_file.write(response.content)

            Clock.schedule_once(
                lambda dt: self.image_ready(path)
            )

        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.add_message(
                    "NULL AI",
                    f"⚠️ Image generation failed: {str(e)}"
                )
            )

    def image_ready(self, path):
        self.add_message(
            "NULL AI",
            "🖼️ Image generated successfully!\n"
            "Use the Android save option to choose where to save it."
        )

        self.save_image_android(path)

    def save_image_android(self, path):
        try:
            from jnius import autoclass

            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("image/png")
            intent.putExtra(
                Intent.EXTRA_TITLE,
                "NULL_AI_generated.png"
            )

            activity = PythonActivity.mActivity

            activity.startActivityForResult(
                intent,
                9001
            )

            self.pending_image = path

        except Exception as e:
            self.add_message(
                "NULL AI",
                f"⚠️ Save picker could not open: {str(e)}"
            )


if __name__ == "__main__":
    NullAI().run()
