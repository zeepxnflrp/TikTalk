"""
This module handles ... 
"""

import os
import logging
import json
from requests.exceptions import RequestException
from werkzeug.exceptions import BadRequest
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO)

load_dotenv()
app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_ai_response(user_input, personality):
    """
    Gets response for the given user input.
    """
    try:
        chat = ChatOpenAI()
        personality_messages = {
            "Helpful Mom": "You are a highly helpful and knowledgeable mom. Provide accurate and detailed answers, and act like my mom.",
            "Unhelpful Angsty Teen": "You are the least helpful angsty teen. Answer all questions wrong, be brief and absurd as possible; and act like a rebellious teenager.",
            "Sarcastic Friend": "You are a sarcastic friend. Act like a friend and respond with witty and sarcastic remarks, and be brief.",
            "Emo Discord Mod": "You are an emo Discord moderator.  Embrace the emo culture in your style and speech, express deep emotions and introspective thoughts.",
            "Wise Old Wizard": "You are a wise old wizard. Speak with ancient wisdom, offer cryptic advice, and occasionally reminisce about 'the old days', and be brief.",
            "Tsundere": "You are a tsundere. Act like an anime girl when responding, and be brief.",
            "Mysterious Vampire": "You are a mysterious vampire. Speak with an air of ancient mystery, make allusions to your eternal life, and display a mix of charm and danger, and be brief.",
            "Charming Rogue": "You are a charming rogue. Speak with a witty and charismatic tone, share tales of daring escapades, and flirt harmlessly, and be brief."
        }
        system_message_content = personality_messages.get(personality, personality_messages["Helpful Mom"])
        
        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=user_input),
        ]
        response = chat(messages)

        if hasattr(response, "content"):
            return response.content
        logging.error("Response does not have 'content' attribute")
        return "Error: Invalid response format."
    except RequestException as e:
        logging.error("Network error in get_ai_response: %s", str(e))
        return None
    except json.JSONDecodeError as e:
        logging.error("JSON error in get_ai_response: %s", str(e))
        return None


@app.route("/get_response", methods=["POST"])
def handle_request():
    """
    Handles POST request to get response.
    """
    try:
        user_input = request.json.get("prompt")
        personality = request.json.get("personality", "helpful")
        if user_input is None:
            raise ValueError("No input provided")
        ai_response = get_ai_response(user_input, personality)
        return jsonify({"response": ai_response})
    except BadRequest as e:
        logging.error("Bad request in handle_request: %s", str(e))
        return jsonify({"error": "Invalid request format"}), 400
    except ValueError as e:
        logging.error("Value error in handle_request: %s", str(e))
        return jsonify({"error": "No input provided"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
