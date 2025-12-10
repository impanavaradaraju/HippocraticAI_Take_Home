import os
import openai
import json

"""
Before submitting the assignment, describe here in a few sentences
what you would have built next if you spent 2 more hours on this project:

I would add story category detection (e.g., animals, space, friendships)
and tailor the storyteller prompt for each genre. I would also build a tiny
web UI so parents and children can generate stories with illustrations together.
Finally, I would add a readability checker to ensure the vocabulary stays
age-appropriate for 5-10-year-olds.
"""

def call_model(prompt: str, max_tokens=3000, temperature=0.2) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")  
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]

STORYTELLER_PROMPT = """
You are a warm, imaginative children's storyteller.
Write a calming bedtime story appropriate for ages 5-10.

Rules:
- Soft, gentle tone.
- 400-700 words.
- Clear beginning → middle → end.
- No fear, violence, or intense danger.
- Include a small lesson (kindness, bravery, curiosity).
- End with a calm, soothing paragraph.

User request:
"{request}"

Write the story now:
"""


def generate_story(request: str) -> str:
    return call_model(STORYTELLER_PROMPT.format(request=request), temperature=0.8)


#Judging
JUDGE_PROMPT = """
You are a children's story quality judge.

Evaluate this story for ages 5-10:

\"\"\"{story}\"\"\"

Return ONLY a JSON object with this format:
{{
  "scores": {{
      "age": 1-5,
      "tone": 1-5,
      "structure": 1-5,
      "engagement": 1-5,
      "clarity": 1-5
  }},
  "needs_revision": true/false,
  "notes": "short explanation",
  "revision_instructions": "specific, concise edits",
  "revised_story": "a revised version that fixes the issues"
}}
"""


def judge_story(story: str) -> dict:
    raw = call_model(JUDGE_PROMPT.format(story=story), temperature=0.3)

    try:
        start = raw.find("{")
        end = raw.rfind("}")
        return json.loads(raw[start:end + 1])
    except:
        return {
            "scores": {},
            "needs_revision": False,
            "notes": "JSON parse error — using original story.",
            "revision_instructions": "",
            "revised_story": story,
        }


#Refining 
def refine_story(request: str, max_rounds=2):
    story = generate_story(request)

    for _ in range(max_rounds):
        judge_data = judge_story(story)
        if not judge_data.get("needs_revision", False):
            return story, judge_data

        story = judge_data.get("revised_story", story)

    return story, judge_data


#Extra Addition
REFLECTION_PROMPT = """
Create a 'Reflection Card' for the following bedtime story:

\"\"\"{story}\"\"\"

Return ONLY a JSON object like this:
{{
  "questions": [
      "Question 1...",
      "Question 2...",
      "Question 3..."
  ],
  "affirmation": "A positive bedtime affirmation starting with 'I am...'"
}}
"""


def reflection_card(story: str) -> dict:
    raw = call_model(REFLECTION_PROMPT.format(story=story), temperature=0.4)

    try:
        start = raw.find("{")
        end = raw.rfind("}")
        return json.loads(raw[start:end+1])
    except:
        return {
            "questions": [
                "What part of the story did you like most?",
                "How did the main character show kindness or courage?",
                "If you were in the story, what would you do?"
            ],
            "affirmation": "I am safe, loved, and ready for sweet dreams."
        }

def main():
    print("Welcome to the Bedtime Story Generator!")
    request = input("What kind of story would you like tonight? ")

    print("\n Creating your story...\n")
    final_story, judge = refine_story(request)

    print("Your Bedtime Story ")
    print(final_story)
    print("\n")

    print("Judge Feedback (for debugging)")
    print(json.dumps(judge, indent=2))
    print("\n")

    print("Reflection Card")
    card = reflection_card(final_story)
    for i, q in enumerate(card["questions"], 1):
        print(f"{i}. {q}")
    print("\nAffirmation:")
    print(f"{card['affirmation']}")


if __name__ == "__main__":
    main()
