import asyncio
import os
import json
import time
from multiprocessing import cpu_count, Process

import cv2
import tqdm
import numpy as np
from playwright.async_api import async_playwright


# The directory where the animation JSON files are stored
ANIM_EULER_DIR = os.path.join(
    os.path.expanduser("~"), "Documents", "video2motion", "anim-json-euler"
)

VIDEOS_DIR = os.path.join(
    os.path.expanduser("~"), "Documents", "video2motion", "videos"
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
    """
    Get the longest track in the animation.
    """

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


async def anim_video(anim_name, lengest_track_len):
    """
    Create a video for the animation by combining the frames.
    """

    elevation = 30
    azimuth = 0

    target_video_path = os.path.join(
        VIDEOS_DIR, f"{anim_name}-{elevation}-{azimuth}.avi"
    )

    if os.path.exists(target_video_path):
        print(f"Video already exists: {target_video_path}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 800, "height": 600},
            screen={"width": 800, "height": 600},
        )

        frame_data = []

        for frame_idx in tqdm.tqdm(range(lengest_track_len)):

            await page.goto(
                f"http://localhost:5173/dors.glb/{anim_name}/{elevation}/{azimuth}/{frame_idx}"
            )

            # Wait until #done are visible
            await page.locator("#done").wait_for()

            # `screenshot_bytes` is a bytes object
            screenshot_bytes = await page.screenshot(type="jpeg", quality=100)
            # converts the byte string data into a NumPy array with uint8 data type
            nparr = np.frombuffer(screenshot_bytes, np.uint8)
            # decodes into an OpenCV format, cv2.IMREAD_COLOR indicating to load a color image.
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # print(img_np.shape)  # (720, 1280, 3)

            # save img to local file
            # cv2.imwrite(f"frames\{anim_name}_{frame_idx}.jpg", img_np)

            frame_data.append(img_np)

        await browser.close()

        # save the frames as a video
        out = cv2.VideoWriter(
            target_video_path,
            cv2.VideoWriter_fourcc(*"DIVX"),
            50,
            (800, 600),
        )

        for i in range(len(frame_data)):
            out.write(frame_data[i])

        out.release()

        print(f"Video saved: {target_video_path}")


class GenerateVideoTask(Process):

    def __init__(self, anim_tasks, queue_idx) -> None:
        Process.__init__(self)

        self.anim_tasks = anim_tasks
        self.queue_idx = queue_idx

    def run(self) -> None:

        for anim_name, max_len in self.anim_tasks:
            print(f"{self.queue_idx} Processing: {anim_name}, {max_len} frames.")

            asyncio.run(anim_video(anim_name, max_len))


if __name__ == "__main__":

    # list all files in the directory `anim_eulers`
    anim_names = [f.replace(".json", "") for f in os.listdir(ANIM_EULER_DIR)]

    print(f"Total number of animations: {len(anim_names)}")

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

    print(f"Total number of long animations: {len(long_anim)}")

    # get number of cpu cores
    anim_task_arr = split_array(long_anim, cpu_count())

    processes = [
        GenerateVideoTask(anim_tasks=tasks, queue_idx=idx)
        for idx, tasks in enumerate(anim_task_arr)
    ]

    start_time = time.time()

    # run the process,
    for process in processes:
        process.start()

    for process in processes:
        # report the daemon attribute
        print(
            process.daemon,
            process.name,
            process.pid,
            process.exitcode,
            process.is_alive(),
        )

        process.join()

    end_time = time.time()

    print(f"Time taken: {end_time - start_time}")
