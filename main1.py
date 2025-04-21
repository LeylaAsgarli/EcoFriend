import os
from dotenv import load_dotenv
import discord
import requests
import json
import sqlite3
import random
from discord.ext import commands
from discord import app_commands

load_dotenv()

# Intent setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- OpenRouter API Setup ---
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")


headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://yourprojecturl.com",
    "X-Title": "YourBotName",
    "Content-Type": "application/json"
}

# --- SQLite Setup ---
conn = sqlite3.connect("usernames.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        discord_id TEXT PRIMARY KEY,
        username TEXT UNIQUE
    )
''')
conn.commit()


# --- Events ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)


# --- AI /ask Command ---
@bot.tree.command(name="ask", description="Ask the AI anything!")
@app_commands.describe(question="What do you want to ask?")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    prompto = (
        "Give a simple one-sentence short answer to the question"
    )
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": prompto
        }]
    
    }

    response = requests.post(OPENROUTER_API_URL,
                             headers=headers,
                             data=json.dumps(payload))

    if response.status_code == 200:
        try:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
        except:
            reply = "Sorry, I couldn't understand the response!"
    else:
        reply = f"Error: {response.status_code} - {response.text}"

    await interaction.followup.send(reply)


# --- /ecotip Command ---
@bot.tree.command(name="ecotip",
                  description="Get a motivational eco-friendly tip!")
async def ecotip(interaction: discord.Interaction):
    await interaction.response.defer()

    prompt = (
        "You are an inspirational eco-activist helping people help the world. "
        "Give a simple one-sentence tip on how someone can be more eco-friendly. "
        "Make it sound motivational and use relevant emojis. Keep it short and friendly."
    )

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{
            "role": "system",
            "content": prompt
        }]
    }

    response = requests.post(OPENROUTER_API_URL,
                             headers=headers,
                             data=json.dumps(payload))

    if response.status_code == 200:
        try:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
        except:
            reply = "Sorry, I couldn't understand the response!"
    else:
        reply = f"Error: {response.status_code} - {response.text}"

    await interaction.followup.send(reply)


#ecoquiz command

animal_data = {
    "What is the scientific name of pandas?": "Ailuropoda melanoleuca",
    "What is the scientific name of tiger?": "Panthera tigris",
    "What is the scientific name of lions?": "Panthera leo",
    "What is the scientific name of elephants?": "Loxodonta africana",
    "What is the scientific name of koalas?": "Phascolarctos cinereus"
}

climate_data = {
    "Which gas is most responsible for climate change?":
    "Carbon dioxide",
    "Which greenhouse gas is 25x more potent than CO₂?":
    "Methane",
    "What gas do trees absorb from the air?":
    "Carbon dioxide",
    "Which gas is released by livestock digestion?":
    "Nitrous oxide",
    "Which gas is used in refrigerants and damages the ozone layer?":
    "Chlorofluorocarbons"
}

recycling_data = {
    "Which of these materials is 100% recyclable?":
    "Aluminum",
    "What can take 20-500 years to decompose?":
    "Plastic",
    "Recycling  1 ton of _______ saves 46 gallons of oil. Fill in the gap.":
    "Cardboard",
    "What is a correct explanation of e-waste?":
    "Electronic waste",
    "It only takes six days to turn old ____ into new ones. Fill in the gap":
    "Paper"
}

deforestation_data = {
    "Which rainforest is the largest on Earth?":
    "Amazon Rainforest",
    "Which endangered animal is native to Borneo's forests?":
    "Orangutan",
    "We have 1800 _____ left in the world. Fill in the gap":
    "Panda",
    "Which is is native to the southwestern United States, Mexico, Central and South America, and the Caribbean islands of Trinidad and Margarita?":
    "Ocelot",
    "Which tree species is commonly logged in tropical forests?":
    "Mahogany"
}

water_data = {
    "What is the process of removing salt from seawater?": "Desalination",
    "What is the term for harmful algae blooms in water?": "Algal bloom",
    "Which lake is the largest in India?": "Vembanad",
    "What is the frozen part of Earth's water called?": "Cryosphere",
    "What is the underground layer that stores freshwater?": "Aquifer"
}

topics = [
    animal_data, climate_data, recycling_data, deforestation_data, water_data
]

# --- Quiz Command ---


@bot.tree.command(name="ecoquiz",
                  description="Test your eco-knowledge with a fun question!")
async def ecoquiz(interaction: discord.Interaction):
    await interaction.response.defer()

    questions = []
    correct_answers = []
    all_options = []

    for topic in topics:
        question, answer = random.choice(list(topic.items()))
        wrong_answers = random.sample(
            [v for v in topic.values() if v != answer], 4)
        options = wrong_answers + [answer]
        random.shuffle(options)

        questions.append(question)
        correct_answers.append(answer)
        all_options.append(options)

    class QuizView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=120)
            self.q_index = 0
            self.score = 0
            self.user_answers = []

            self.send_question()

        def send_question(self):
            self.clear_items()
            question = questions[self.q_index]
            options = all_options[self.q_index]
            for option in options:
                self.add_item(AnswerButton(option, self))

        async def next_question(self, interaction: discord.Interaction):
            self.q_index += 1
            if self.q_index >= len(questions):
                await self.show_results(interaction)
            else:
                self.send_question()
                await interaction.message.edit(
                    content=
                    f"**Question {self.q_index + 1}/5:** {questions[self.q_index]}",
                    view=self)

        async def show_results(self, interaction: discord.Interaction):
            feedback = {
                5: "🌟 Eco Legend! You really know your planet!",
                4: "🌿 Green Genius! Almost perfect.",
                3: "🍃 Eco Curious! Not bad at all.",
                2: "🌱 Learning Sprout! Keep it growing.",
                1: "🪨 Room to Grow! Let's go greener.",
                0: "😬 Maybe go hug a tree and try again?"
            }
            result_text = f"✅ You got **{self.score}/5** correct!\n{feedback[self.score]}"
            await interaction.message.edit(content=result_text, view=None)

    class AnswerButton(discord.ui.Button):

        def __init__(self, label, view):
            super().__init__(label=label, style=discord.ButtonStyle.primary)
            self.quiz_view = view

        async def callback(self, interaction: discord.Interaction):
            correct = correct_answers[self.quiz_view.q_index]
            if self.label == correct:
                self.quiz_view.score += 1
                await interaction.response.send_message("✅ Correct!",
                                                        ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"❌ Nope! The correct answer was: `{correct}`",
                    ephemeral=True)
            await self.quiz_view.next_question(interaction)

    view = QuizView()
    await interaction.followup.send(f"**Question 1/5:** {questions[0]}",
                                    view=view)


#treeplant command
@bot.tree.command(name="treeplant",
                  description="Start your tree-planting journey!")
async def treeplant(interaction: discord.Interaction):

    class PlantSelectionView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class RoseButton(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌹 Rose",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        content=
                        "2. Choose a Planting Spot\n\"Where do you want to plant your rose?\"",
                        view=Step2_RoseView(),
                        embed=discord.Embed().set_image(
                            url=
                            "file:///C:/Users/qiyme/Pictures/Screenshots/RoseScreenshot%202025-04-21%20221150.png"
                        ))

            class SunflowerButton(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌻 Sunflower",
                                     style=discord.ButtonStyle.success)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        content=
                        "2. Choose a Planting Spot\n\"Where do you want to plant your sunflower?\"",
                        view=Step2_SunflowerView(),
                        embed=discord.Embed().set_image(
                            url=
                            "https://img.freepik.com/free-vector/hand-painted-watercolor-sunflowers-collection_52683-67113.jpg"
                        ))

            self.add_item(RoseButton())
            self.add_item(SunflowerButton())

    class Step2_RoseView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class FullSun(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="☀️ Full Sun",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ Great choice! Roses love sunlight. Let's move on!",
                        ephemeral=True)
                    await interaction.followup.send(
                        "3. Check the Soil\n\"What kind of soil will you use?\"",
                        view=Step3_RoseView())

            class PartialShade(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="☁️ Partial Shade",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ More sun = more blooms! Try again.", ephemeral=True)

            class UnderTree(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌲 Under a Tree",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Too much shade and falling branches! Try again",
                        ephemeral=True)

            self.add_item(FullSun())
            self.add_item(PartialShade())
            self.add_item(UnderTree())

    class Step3_RoseView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class LoamySoil(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🏖️ Sandy Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        '❌ It won’t hold enough nutrients or water. Try again',
                        ephemeral=True)

            class RockySoil(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🪨 Rocky Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Too rough for rose roots! Try again",
                        ephemeral=True)

            class SandySoil(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌱 Rich Loamy Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ Perfect soil! Let's prep the rose.", ephemeral=True)
                    await interaction.followup.send(
                        "4. Prepare the Rose\n\"What type of rose do you have?\"",
                        view=Step4_RoseView())

            self.add_item(LoamySoil())
            self.add_item(RockySoil())
            self.add_item(SandySoil())

    class Step4_RoseView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class BareRoot(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌿 Bare-Root",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "➡️ Soak roots and trim any damage first!",
                        ephemeral=True)
                    await interaction.followup.send(
                        "5. Planting Depth\n\"Where should the graft union be?\"",
                        view=Step5_RoseView())

            class Container(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🪴 Container",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "➡️ Loosen those roots so they spread out!",
                        ephemeral=True)
                    await interaction.followup.send(
                        "5. Planting Depth\n\"Where should the graft union be?\"",
                        view=Step5_RoseView())

            self.add_item(BareRoot())
            self.add_item(Container())

    class Step5_RoseView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class JustBelow(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🕳️ Above Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Too exposed! Try again", ephemeral=True)

            class AboveSoil(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌍 Just Below Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ Perfect for protection and growth!", ephemeral=True)
                    await interaction.followup.send(
                        "6. Water & Mulch\n\"Nice! Time to protect the roots and give your rose a drink!\"",
                        view=Step6_RoseView())

            class FarBelow(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="⛄ Far Below Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Too deep for most climates!Try again",
                        ephemeral=True)

            self.add_item(JustBelow())
            self.add_item(AboveSoil())
            self.add_item(FarBelow())

    class Step6_RoseView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class WaterMulch(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="Water💧",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ You hydrated your plant and locked in moisture!",
                        ephemeral=True)
                    await interaction.followup.send(
                        "7. Care Tips\n\"How will you take care of your rose?\"",
                        view=Step7_RoseView())

            class LetItRest(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="Mulch🌸",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ Smart! Mulch keeps the soil cool and cozy.",
                        ephemeral=True)
                    await interaction.followup.send(
                        "7. Care Tips\n\"How will you take care of your rose?\"",
                        view=Step7_RoseView())

            self.add_item(WaterMulch())
            self.add_item(LetItRest())

    class Step7_RoseView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class Weekly(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🧃 Water every week",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ That helps roots grow deep and strong! 🌳 You completed planting your rose! Congratulations!",
                        ephemeral=True)

            class Daily(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🚿 Water every day",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ That’s too much — roses hate soggy feet! Try again",
                        ephemeral=True)

            class Ignore(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🍂 Ignore it for a month",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Your rose needs love to thrive! Try again",
                        ephemeral=True)

            self.add_item(Weekly())
            self.add_item(Daily())
            self.add_item(Ignore())

    class Step2_SunflowerView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            class FullSun(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌑 Shade",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Sunflowers love the sun — try again!",
                        ephemeral=True)

            class Shade(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="☀️ Full Sun",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ Sunflowers need full sunlight to grow tall!",
                        ephemeral=True)
                    await interaction.followup.send(
                        "3. Soil Type\n\"What kind of soil are you planting in?\"",
                        view=Step3_SunflowerView())

            self.add_item(FullSun())
            self.add_item(Shade())

    class Step3_SunflowerView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            # Well Drained Soil Button (Correct Answer)
            class WellDrained(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌾 Well-drained Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ Great! Sunflowers don’t like wet feet!",
                        ephemeral=True)
                    # Proceed to next step
                    await interaction.followup.send(
                        "4. How will you plant?\n\"Which method suits you best?\"",
                        view=Step4_SunflowerView())

            # Clay Soil Button (Incorrect Answer)
            class ClaySoil(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌻 Clay Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Not ideal. Sunflowers prefer well-drained soil.",
                        ephemeral=True)

            # Sandy Soil Button (Incorrect Answer)
            class SandySoil(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🏜 Sandy Soil",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Sunflowers need richer soil, not sandy.",
                        ephemeral=True)

            # Add buttons in a shuffled order (manually shuffled for this example)
            self.add_item(
                SandySoil())  # First button is Sandy Soil (incorrect)
            self.add_item(
                WellDrained())  # Second button is Well-drained Soil (correct)
            self.add_item(ClaySoil())  # Third button is Clay Soil (incorrect)

    class Step4_SunflowerView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            # Direct Sow Button (Correct Answer)
            class DirectSow(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌻 Direct Sow",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ That’s the best way! Let’s continue.",
                        ephemeral=True)
                    # Proceed to next step
                    await interaction.followup.send(
                        "5. Spacing\n\"How far apart will you plant the seeds?\"",
                        view=Step5_SunflowerView())

            # Transplant Button (Incorrect Answer)
            class Transplant(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌱 Transplant",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Transplanting is not ideal for sunflowers. They grow best when directly sown.",
                        ephemeral=True)

            # Add buttons in a shuffled order (manually shuffled for this example)
            self.add_item(DirectSow())  # First button is Direct Sow (correct)
            self.add_item(
                Transplant())  # Second button is Transplant (incorrect)

    class Step5_SunflowerView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            # Proper Spacing Button (Correct Answer)
            class ProperSpacing(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌱 12-18 inches apart",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "✅ Great! That’s the perfect spacing for sunflowers.",
                        ephemeral=True)
                    # Proceed to next step (or finish the quiz)
                    await interaction.followup.send(
                        "6. Final Step\n\"Let’s wrap up the process.\"",
                        view=FinalStepView())

            # Too Close Spacing Button (Incorrect Answer)
            class TooClose(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌱 3-6 inches apart",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Too close! Sunflowers need space to grow.",
                        ephemeral=True)

            # Too Far Spacing Button (Incorrect Answer)
            class TooFar(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌱 24-30 inches apart",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "❌ Too far! Sunflowers should be closer together.",
                        ephemeral=True)

            # Add buttons in a shuffled order (manually shuffled for this example)
            self.add_item(TooClose())  # First button is Too Close (incorrect)
            self.add_item(
                ProperSpacing())  # Second button is Proper Spacing (correct)
            self.add_item(TooFar())  # Third button is Too Far (incorrect)

    # Final Step for conclusion
    class FinalStepView(discord.ui.View):

        def __init__(self):
            super().__init__(timeout=60)

            # Finish Button
            class FinishButton(discord.ui.Button):

                def __init__(self):
                    super().__init__(label="🌻 Finish",
                                     style=discord.ButtonStyle.primary)

                async def callback(self, interaction):
                    await interaction.response.send_message(
                        "🎉 Congratulations! You've successfully learned how to plant sunflowers.",
                        ephemeral=True)

            # Add Finish button
            self.add_item(FinishButton())

    await interaction.response.send_message(
        "1. Choose your plant:\n\"Which flower do you want to plant?\"",
        view=PlantSelectionView())


# --- /hi Command ---
@bot.tree.command(name="hi",
                  description="Introduce the bot and show available commands")
async def hi(interaction: discord.Interaction):
    intro_message = (
        f"🌱 **Hi {interaction.user.mention}! I'm EcoFriend – your eco-friendly buddy! Start with using /username YourName to sign in.** 🌍\n"
        f"Here's what I can do:\n"
        f"• `/ask` – Ask me anything about climate, or any other topic! 🌎\n"
        f"• `/ecotip` – Get a quick eco tip to help the Earth 🍃\n"
        f"• `/treeplant` – Play a fun tree planting mini-game!🌳\n"
        f"• `/ecochallenge` – Get a fun challenge to help our environment!♻️\n"
        f"• `/ecoquiz` – Test your knowledge with the climate quiz ❓\n"
        f"• `/accessmyusername` – Access your username! 🛠️\n"
        f"• `/hi` – Use this command to get this introduction message!\n")
    await interaction.response.send_message(intro_message)


# --- /username Command ---
@bot.tree.command(name="username", description="Register a unique username")
@app_commands.describe(user_name="Your desired username")
async def username(interaction: discord.Interaction, user_name: str):
    discord_id = str(interaction.user.id)

    cursor.execute("SELECT * FROM users WHERE username = ?", (user_name, ))
    if cursor.fetchone():
        await interaction.response.send_message(
            "❌ Username taken! Try another one.")
        return

    try:
        cursor.execute(
            "INSERT INTO users (discord_id, username) VALUES (?, ?)",
            (discord_id, user_name))
        conn.commit()
        await interaction.response.send_message(
            f"✅ Username `{user_name}` registered successfully!")
    except sqlite3.IntegrityError:
        await interaction.response.send_message(
            "⚠️ You already have a username. Use `/accessmyusername` to see it."
        )


# --- /accessmyusername Command ---
@bot.tree.command(name="accessmyusername",
                  description="See your registered username")
async def accessmyusername(interaction: discord.Interaction):
    discord_id = str(interaction.user.id)
    cursor.execute("SELECT username FROM users WHERE discord_id = ?",
                   (discord_id, ))
    result = cursor.fetchone()

    if result:
        await interaction.response.send_message(
            f"👤 Your username is: `{result[0]}`")
    else:
        await interaction.response.send_message(
            "❗ You haven't registered a username. Use `/username your_name`.")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
