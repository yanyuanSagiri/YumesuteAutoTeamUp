import argparse
import os
import asyncio
import json

from ActorFormation import automatic_formation
from pipeline import start_pipeline


def parse_args():
    parser = argparse.ArgumentParser(description='Yumesute auto team-up')
    parser.add_argument('user', nargs='?', metavar='File name for user data', default='Yumesute.json', help='账号数据名称')
    parser.add_argument('-d', '--data', metavar='DIR for game data', default='data', help='游戏内资源路径')
    parser.add_argument('-mc', '--mandatory_characters', type=int, nargs=10, default=[0]*10,
                        help='交替输入必选角色及其固定位置, 不选则填0, 以空格分割')
    parser.add_argument('-mp', '--mandatory_posters', type=int, nargs=10, default=[0]*10,
                        help='交替输入必选海报及其绑定角色, 不选则填0, 以空格分割')
    parser.add_argument('-ml', '--mandatory_leader', type=int, default=0, help='固定队长位置, 不选则填0')
    return parser.parse_args()


async def main():
    args = parse_args()
    userdata_path = os.path.join(args.user)
    character_master_path = os.path.join(args.data, 'CharacterMaster.json')
    poster_ability_path = os.path.join(args.data, 'PosterAbilityMaster.json')
    accessory_path = os.path.join(args.data, 'accessory_processed.json')
    effect_master_path = os.path.join(args.data, 'EffectMaster.json')

    with open(userdata_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)
    accessory_user = user_data["accessories"]

    with open(accessory_path, "r", encoding="utf-8") as f:
        accessory_data = json.load(f)
    accessory_list = {item["CharacterBaseMasterId"]: item for item in accessory_data}

    sync_queue, (accessory_task, saver_task) = start_pipeline(
        accessory_user=accessory_user,
        accessory_list=accessory_list,
        api_url="http://127.0.0.1:3456/calc",
        data_file=userdata_path,
        sensenotation=1146,
        leader=args.mandatory_leader,
        score_only=True,
        concurrency=10,
        # save_func=save_result
    )

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(  # ActorFormation.py
        None,
        automatic_formation,
        userdata_path, character_master_path, poster_ability_path, effect_master_path,
        tuple(args.mandatory_characters), tuple(args.mandatory_posters),
        sync_queue
    )

    await accessory_task
    await saver_task
    print("Finished")


if __name__ == "__main__":
    asyncio.run(main())
