import argparse, os
from ActorFormation import automatic_formation


def parse_args():
    parser = argparse.ArgumentParser(description='Yumesute auto team-up')
    parser.add_argument('user', nargs='?', metavar='File name for user data', default='Yumesute', help='账号数据名称')
    parser.add_argument('-d', '--data', metavar='DIR for server data', default='data', help='服务器内资源路径')
    parser.add_argument('-mc', '--mandatory_characters', type=int, nargs=10, default=[0]*10,
                        help='交替输入必选角色及其固定位置, 不选则填0, 以空格分割')
    parser.add_argument('-mp', '--mandatory_posters', type=int, nargs=10, default=[0]*10,
                        help='交替输入必选海报及其对应位置, 不选则填0, 以空格分割')
    parser.add_argument('-ml', '--mandatory_leader', type=int, default=0, help='固定队长位置, 不选则填0')
    parser.add_argument('-u', '--update', type=str, default='https://github.com/esterTion/yumesute_master_db_diff')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    userdata_path = os.path.join(args.user + '.json')
    character_master_path = os.path.join(args.data, 'CharacterMaster.json')
    poster_ability_path = os.path.join(args.data, 'PosterAbilityMaster.json')
    accessory_path = os.path.join(args.data, 'accessory_processed.json')
    effect_master_path = os.path.join(args.data, 'EffectMaster.json')
    result = automatic_formation(
        userdata_path,
        character_master_path,
        poster_ability_path,
        effect_master_path,
        tuple(args.mandatory_characters),
        tuple(args.mandatory_posters)
    )

