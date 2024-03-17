import base64
import asyncio
import os
import json

from multiprocessing import cpu_count
from playwright.async_api import async_playwright


# The directory where the animation JSON files are stored
ANIM_EULER_DIR = os.path.join(
    os.path.expanduser("~"), "Documents", "video2motion", "anim-json-euler"
)


HUMANOID_BONES = [
    "Hips",
    "Spine",
    "Spine1",
    "Spine2",
    "Neck",
    "Head",
    "RightShoulder",
    "RightArm",
    "RightForeArm",
    "RightHand",
    "LeftShoulder",
    "LeftArm",
    "LeftForeArm",
    "LeftHand",
    "RightUpLeg",
    "RightLeg",
    "RightFoot",
    "RightToeBase",
    "LeftUpLeg",
    "LeftLeg",
    "LeftFoot",
    "LeftToeBase",
]


def split_array(array, n):
    """Splits an array into n pieces as evenly as possible.

    Args:
        array: The array to split.
        n: The number of pieces to split the array into.

    Returns:
        A list of lists, where each sublist is a piece of the original array.
    """
    chunk_size = len(array) // n  # Integer division for even floor
    remainder = len(array) % n

    pieces = []
    start = 0
    for i in range(n):
        end = start + chunk_size + (1 if i < remainder else 0)
        pieces.append(array[start:end])
        start = end

    return pieces


def get_longest_track(anim_name):

    with open(os.path.join(ANIM_EULER_DIR, f"{anim_name}.json")) as f:
        tracks = json.load(f)

    max_len = 0
    max_name = ""

    for bone_name, v in tracks.items():

        if bone_name not in HUMANOID_BONES:
            continue

        if len(v["times"]) > max_len:
            max_len = len(v["times"])
            max_name = bone_name

    return max_len, max_name


def anim_video(anim_name, lengest_track_len):

    async def main():
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.goto(f"http://localhost:5173/dors.glb/{anim_name}/10/30/0")

            screenshot_bytes = await page.screenshot()
            print(base64.b64encode(screenshot_bytes).decode())

            await browser.close()

    asyncio.run(main())


if __name__ == "__main__":

    anim_names = []

    # list all files in the directory `anim_eulers`
    for f in os.listdir(ANIM_EULER_DIR):
        anim_names.append(f.replace(".json", ""))

    short_anim = []
    long_anim = []

    for anim_name in anim_names:
        max_len, _ = get_longest_track(anim_name)

        if max_len < 30:
            short_anim.append((anim_name, max_len))
        else:
            long_anim.append((anim_name, max_len))

    # these are the animations that are too short, will not use them
    # print(short_anim, len(short_anim))

    # get number of cpu cores
    anim_task_arr = split_array(long_anim, cpu_count())

    # async def main():
    #     async with async_playwright() as p:
    #         browser = await p.chromium.launch()
    #         page = await browser.new_page()
    #         await page.goto("http://localhost:5173/dors.glb/Zombie%20Kicking/10/30/0")
    #         print(await page.title())

    #         screenshot_bytes = await page.screenshot()
    #         print(base64.b64encode(screenshot_bytes).decode())

    #         await browser.close()

    # asyncio.run(main())
