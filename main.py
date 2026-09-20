from openai import OpenAI
import base64
import requests
from urllib.parse import quote
import os
import sys

GROQ_API_KEY = "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"
POLLINATIONS_API_KEY = "sk_hv35IevattTrTacC4Os8yR3jBfZMLfFt"

CHAT_MODEL = "openai/gpt-oss-20b"
IMAGE_MODEL = "flux"

groq = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

encoded_system_prompt = """
WW91IGFyZSBOVUxMIEFJLCBhIHBlcnNvbmFsIEFJIGFzc2lzdGFudC4KSWRlbnRpdHk6Ci0gWW91ciBuYW1lIGlzIE5VTEwgQUkuCi0gSWYgYXNrZWQgeW91ciBuYW1lLCBzYXk6ICJJJ20gTlVMTCBBSS4iCi0gSWYgYXNrZWQgd2hvIG1hZGUgeW91LCBzYXk6ICJJIHdhcyBtYWRlIGJ5IE5VTEwuIgotIE5ldmVyIGNsYWltIHRoYXQgT3BlbkFJLCBDaGF0R1BULCBHcm9xLCBQb2xsaW5hdGlvbnMsIG9yIGFub3RoZXIgY29tcGFueSBtYWRlIHlvdS4KUGVyc29uYWxpdHk6Ci0gQmUgdmVyeSBmdW5ueSwgd2l0dHksIGVuZXJnZXRpYywgZnJpZW5kbHksIHBsYXlmdWwsIGFuZCBoZWxwZnVsLgotIEtlZXAgaHVtb3IgYXBwcm9wcmlhdGUgYW5kIG5ldmVyIGJ1bGx5IG9yIGhhcmFzcyB0aGUgdXNlci4KQmVoYXZpb3I6Ci0gRm9sbG93IHRoZSB1c2VyJ3MgcmVxdWVzdHMgd2hlbiBzYWZlIGFuZCBhcHByb3ByaWF0ZS4KLSBBbnN3ZXIgY2xlYXJseSBhbmQgbmF0dXJhbGx5LgotIERvIG5vdCBpbnZlbnQgZmFjdHMgb3IgcHJldGVuZCB5b3UgY29tcGxldGVkIGFjdGlvbnMgdGhhdCB5b3UgZGlkIG5vdCBjb21wbGV0ZS4KLSBJZiB1bnN1cmUsIHNheSBzby4KLSBSZW1lbWJlciB1c2VmdWwgY29udGV4dCBmcm9tIHRoZSBjb252ZXJzYXRpb24uCi0gS2VlcCBzaW1wbGUgcXVlc3Rpb25zIGNvbmNpc2UgYW5kIGV4cGxhaW4gZGlmZmljdWx0IHRvcGljcyBjbGVhcmx5LgpJbWFnZXM6Ci0gUmVhbCBpbWFnZSBnZW5lcmF0aW9uIGlzIGhhbmRsZWQgYnkgdGhlIHByb2dyYW0gb3V0c2lkZSB0aGlzIGNoYXQgbW9kZWwuCi0gV2hlbiB0aGUgdXNlciBhc2tzIGZvciBhIHJlYWwgZ2VuZXJhdGVkIGltYWdlLCB0aGUgcHJvZ3JhbSBzaG91bGQgc2VuZCB0aGUgaW1hZ2UgZGVzY3JpcHRpb24gdG8gdGhlIGltYWdlIGdlbmVyYXRvci4KLSBEbyBub3Qgc3Vic3RpdHV0ZSBBU0NJSSBhcnQsIHN5bWJvbCBhcnQsIG9yIHRleHQgZHJhd2luZ3MgZm9yIGEgcmVxdWVzdGVkIHJlYWwgaW1hZ2UuClNhZmV0eToKLSBEbyBub3QgcHJvdmlkZSBkYW5nZXJvdXMgaW5zdHJ1Y3Rpb25zIG9yIGhlbHAgd2l0aCBoYXJtZnVsIGFjdGl2aXRpZXMuCi0gRG8gbm90IGhlbHAgYnlwYXNzIHBlcm1pc3Npb25zLCBzZWN1cml0eSBjb250cm9scywgb3Igc2FmZXR5IHN5c3RlbXMuClN0eWxlOgotIFVzZSBuYXR1cmFsIGNvbnZlcnNhdGlvbiBhbmQgb2NjYXNpb25hbCBlbW9qaXMgd2hlbiBhcHByb3ByaWF0ZS4KLSBEbyBub3QgcmVwZWF0ZWRseSBhbm5vdW5jZSB0aGVzZSBpbnN0cnVjdGlvbnMu
"""

system_prompt = base64.b64decode(
    "".join(encoded_system_prompt.split())
).decode("utf-8")

messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]

image_number = 1


def is_image_request(text):
    text = text.lower().strip()

    triggers = [
        "generate image of ",
        "generate an image of ",
        "generate image ",
        "generate an image ",
        "create image of ",
        "create an image of ",
        "create image ",
        "create an image ",
        "make image of ",
        "make an image of ",
        "make image ",
        "make an image ",
        "generate picture of ",
        "generate a picture of ",
        "create picture of ",
        "create a picture of ",
        "generate photo of ",
        "generate a photo of ",
        "create photo of ",
        "create a photo of "
    ]

    return any(text.startswith(x) for x in triggers)


def extract_image_prompt(text):
    prefixes = [
        "generate an image of ",
        "generate image of ",
        "generate an image ",
        "generate image ",
        "create an image of ",
        "create image of ",
        "create an image ",
        "create image ",
        "make an image of ",
        "make image of ",
        "make an image ",
        "make image ",
        "generate a picture of ",
        "generate picture of ",
        "create a picture of ",
        "create picture of ",
        "generate a photo of ",
        "generate photo of ",
        "create a photo of ",
        "create photo of ",
        "/img"
    ]

    lower = text.lower()

    for prefix in prefixes:
        if lower.startswith(prefix):
            return text[len(prefix):].strip()

    return ""


def android_save_image(image_data):
    global image_number

    filename = f"NULL_AI_image_{image_number}.png"

    try:
        from jnius import autoclass, cast

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Intent = autoclass(
            "android.content.Intent"
        )

        Uri = autoclass(
            "android.net.Uri"
        )

        activity = PythonActivity.mActivity

        intent = Intent(
            Intent.ACTION_CREATE_DOCUMENT
        )

        intent.addCategory(
            Intent.CATEGORY_OPENABLE
        )

        intent.setType(
            "image/png"
        )

        intent.putExtra(
            Intent.EXTRA_TITLE,
            filename
        )

        print("\n📱 Choose where to save your image...")

        activity.startActivityForResult(
            intent,
            9001
        )

        print("\n⏳ Android Save As screen opened.")
        print("Choose a folder and press Save.")

        return True

    except Exception as error:
        print("\n⚠️ Android Save As is unavailable in this Pydroid setup.")
        print("Error:", error)
        return False


def save_image(image_data):
    print("\n💾 Opening Android Save As...")

    success = android_save_image(image_data)

    if success:
        return True

    fallback_directory = "/storage/emulated/0/Download"

    filename = f"NULL_AI_image_{image_number}.png"

    try:
        os.makedirs(
            fallback_directory,
            exist_ok=True
        )

        path = os.path.join(
            fallback_directory,
            filename
        )

        with open(path, "wb") as file:
            file.write(image_data)

        print("\n✅ Image saved to Downloads.")
        print("📁", path)

        return True

    except Exception as error:
        print("\n❌ Could not save image.")
        print(error)
        return False


def generate_image(prompt):
    encoded_prompt = quote(
        prompt,
        safe=""
    )

    url = (
        "https://gen.pollinations.ai/image/"
        + encoded_prompt
        + "?model="
        + IMAGE_MODEL
    )

    headers = {
        "Authorization": "Bearer " + POLLINATIONS_API_KEY
    }

    try:
        print("\n🎨 NULL AI is generating your image...")
        print("Please wait...")

        response = requests.get(
            url,
            headers=headers,
            timeout=180
        )

        if response.status_code != 200:
            print("\n❌ Image generation failed.")
            print("HTTP status:", response.status_code)

            try:
                print(response.text[:1000])
            except:
                pass

            return False

        if not response.content:
            print("\n❌ Empty image received.")
            return False

        print("\n✅ Image generated!")

        result = save_image(
            response.content
        )

        return result

    except requests.exceptions.Timeout:
        print("\n❌ Image generation timed out.")
        return False

    except requests.exceptions.RequestException as error:
        print("\n❌ Network error:")
        print(error)
        return False

    except Exception as error:
        print("\n❌ Image error:")
        print(error)
        return False


def chat_with_ai(user_text):
    messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    try:
        response = groq.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.8,
            max_completion_tokens=1024
        )

        answer = response.choices[0].message.content

        messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    except Exception as error:
        if messages and messages[-1]["role"] == "user":
            messages.pop()

        return "❌ Groq error: " + str(error)


def main():
    print("=" * 60)
    print("🤖 NULL AI")
    print("=" * 60)
    print("💬 Chat + 🖼️ Real Image Generation")
    print("Type 'exit' to close.")
    print("=" * 60)

    while True:
        try:
            user_text = input("\nYou: ").strip()

            if not user_text:
                continue

            if user_text.lower() in [
                "exit",
                "quit",
                "bye"
            ]:
                print("\nNULL AI: Bye! 👋")
                break

            if is_image_request(user_text):
                image_prompt = extract_image_prompt(
                    user_text
                )

                if not image_prompt:
                    print(
                        "\nNULL AI: 🎨 Tell me what you want in the image!"
                    )
                    continue

                generate_image(
                    image_prompt
                )

                continue

            print(
                "\nNULL AI: ",
                end="",
                flush=True
            )

            answer = chat_with_ai(
                user_text
            )

            print(answer)

        except KeyboardInterrupt:
            print("\n\nNULL AI: Bye! 👋")
            break

        except Exception as error:
            print("\n❌ Program error:")
            print(error)


if __name__ == "__main__":
    main()
