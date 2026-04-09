import asyncio
from dotenv import load_dotenv
from lesson import LessonController, Stage

load_dotenv()


async def main():
    controller = LessonController(words=["cat", "dog", "bird", "car", "house"])

    print("Charlie (happy): Hi! I'm Charlie, your English teacher!")
    print("Charlie (happy): Today we're going to learn some new words together!")
    print("Charlie (happy): Type OK when you're ready to start!")

    while controller.stage != Stage.DONE:
        user_input = input("Child: ").strip()
        response = await controller.handle(user_input)

        text = response.get("text", "")
        emotion = response.get("emotion", "happy")

        print(f"Charlie ({emotion}): ", end="", flush=True)
        for char in text:
            print(char, end="", flush=True)
            await asyncio.sleep(0.02)
        print()


if __name__ == "__main__":
    asyncio.run(main())
