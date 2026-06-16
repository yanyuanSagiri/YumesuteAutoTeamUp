"""
ActorFormation module is used for building formation automatically.
This version is for mandatory_posters formed [poster1, position1, ...], which may be used at special mode.
Input: relative files' path.
Output: N-Top results among all status.

Problems remain: no deduplication at DAG.
"""
import json
import time

from FindPosterSolutions import find_poster_solutions, CharacterFilter
from collections import defaultdict


class CheckUnrepeated:
    """
    Accelerate auto formation for actors by pruning illegal characters status.
    Some important data is stored in this class simultaneously.
    Input: charm(c_base_id), poste(p_base_id), posit(position of leader), c_cache
    Output: A legal list for character on [:posit] axis, eg: [110010, 110020, ...]
    """
    def __init__(self):
        self.chara_master = {
            101, 102, 103, 104, 105, 106,
            201, 202, 203, 204, 205,
            301, 302, 303, 304, 305,
            401, 402, 403, 404, 405
        }
        self._status = set()
        self._result_chara = []
        self._result_poste = []
        self.manda_chara = [0] * 5  # record mandatory characters and [index] position
        self.manda_poste = [0] * 5  # record mandatory posters and [index] position
        self.prior_chara = set()  # record mandatory characters with void position
        self.prior_poste = set()  # record mandatory posters with void position
        self.busy_charb = set()  # record busy characters' [BaseId] after processing priorities
        self.busy_poste = set()  # record busy posters' [BaseId] after processing priorities
        self.num_master = {1, 2, 3, 4, 5}
        self.state_base = [0, 0, 0, 0, 0]  # be used for initialize bfs status
        self.chara_mid2id = defaultdict(list)

    def urp_filter_c(self, master, filtlist=None, c_cache=None):  # filter characters' filtlist in master
        if not c_cache:
            return {f for f in master if f not in filtlist}
        charm_bot = master.copy()
        for f in filtlist:
            charm_bot.discard(f)
        c_bot = set()
        for c in charm_bot:
            for i in self.chara_mid2id[c]:
                charb = c_cache[i].get("CharacterBaseMasterId", [])
                charb_len = len(charb)
                if charb_len == 1:
                    c_bot.add(i)
                    continue
                elif charb_len == 2:
                    if c == charb[0]:
                        j = charb[1]
                    else:
                        j = charb[0]
                    if j in filtlist or j == charb[0]:
                        continue
                    c_bot.add(i)
                else:
                    print(f"Unknown CharacterBaseMasterId {charb}")
        return c_bot

    def urp_filter_dag(self, filter_c_p, poste_busy):
        # print(f"come in")
        postb_bot = poste_busy.copy()
        c_p_bot = filter_c_p.supreme_arr.copy()
        # print(c_p_bot)
        boolean = True
        while boolean:  # update current supreme queue by busy posters
            # print(f"check")
            boolean = False
            for p in postb_bot:  # check busy poster's domination
                if p not in c_p_bot:  # if busy poster in supreme
                    continue
                p_son = filter_c_p.dominate[p]  # check posters it dominates
                for son in p_son:
                    if son in c_p_bot:
                        continue
                    bson = True
                    for f in filter_c_p.dominated[son]:  # check one son's father
                        if f not in c_p_bot:  # father not in supreme
                            bson = False  # no need to push son in supreme
                            break
                    if bson:  # need to push son in supreme
                        c_p_bot.add(son)
                        # print(f"add son {son} in supreme posters")
                        boolean = True  # status changed
        return c_p_bot

    def urp_filter_i(self, charc, poste, c_cache):  # Initialize mandatory elements
        # TODO(Frocean): Add preprocessing persistent domination DAG module at convenience
        for i in range(5):
            i2 = i << 1
            bid = charc[i2]
            pos = charc[i2 + 1] - 1
            bool_either = False
            if not pos < 0:  # mandatory character with position
                self.manda_chara[pos] = bid
                bool_either = True
            elif bid:  # mandatory character without position
                self.prior_chara.add(bid)
                bool_either = True
            if bool_either:
                cbid = c_cache[bid].get("CharacterBaseMasterId", [])
                for j in cbid:
                    self.busy_charb.add(j)
            bid = poste[i2]
            pos = poste[i2 + 1] - 1
            bool_either = False
            if not pos < 0:  # mandatory poster with position
                self.manda_poste[pos] = bid
                bool_either = True
            elif bid:  # mandatory poster without position
                self.prior_poste.add(bid)
                bool_either = True
            if bool_either:
                self.busy_poste.add(bid)

    def urp_filter_n(self, num_busy=None):  # check {1, 2, 3, 4, 5} which is used and discard
        number_bot = self.num_master.copy()
        if num_busy:
            for n in num_busy:
                number_bot.discard(n)
        return number_bot

    def processor_character(self, c_cache):
        stime = time.time()
        queue = []
        self._result_chara = []
        self._status = set()
        manda_busy = {i+1 for i in range(5) if self.manda_chara[i]}  # initialize busy position
        leng = len(self.prior_chara)
        if leng:  # check prior characters' status initially
            # not essential to concern duplicated status between mandatory/prior characters
            for n in self.urp_filter_n(manda_busy):
                for c in self.prior_chara:
                    state_bot = list(self.manda_chara)
                    state_bot[n - 1] = c
                    state_bot = tuple(state_bot)
                    self._status.add(state_bot)
                    queue.append(state_bot)
            for i in range(leng - 1):
                queue_next = []
                for state in queue:
                    nums_bot = {i+1 for i, p in enumerate(state) if p}  # | manda_busy
                    busy_bot = {c for c in state if c}
                    for n in self.urp_filter_n(nums_bot):
                        for c in self.urp_filter_c(self.prior_chara, busy_bot):
                            state_bot = list(state)
                            state_bot[n - 1] = c
                            state_bot = tuple(state_bot)
                            if state_bot in self._status:
                                continue
                            self._status.add(state_bot)
                            queue_next.append(state_bot)
                queue = queue_next
        leng = 5 - leng - len(manda_busy)
        if leng == 5:  # A condition which would never be used. So why I code this?
            for n in self.urp_filter_n():
                for c in self.urp_filter_c(self.chara_master, set(), c_cache):
                    state_bot = list(self.state_base)
                    state_bot[n - 1] = c
                    state_bot = tuple(state_bot)
                    self._status.add(state_bot)
                    queue.append(state_bot)
            leng -= 1
        for i in range(leng):  # complete the status for characters
            queue_next = []
            for state in queue:
                nums_bot = {i+1 for i, p in enumerate(state) if p}
                busy_bot = {i for c in state if c for i in c_cache[c].get("CharacterBaseMasterId", [])}
                for n in self.urp_filter_n(nums_bot):
                    for c in self.urp_filter_c(self.chara_master, busy_bot, c_cache):  # now need to concern
                        state_bot = list(state)
                        state_bot[n - 1] = c
                        state_bot = tuple(state_bot)
                        if state_bot in self._status:
                            continue
                        self._status.add(state_bot)
                        queue_next.append(state_bot)
            queue = queue_next
        print(f"cost time {time.time() - stime}s in {len(queue)} solutions")
        return queue

    def processor_poster(self, clist, solutions):
        stime = time.time()
        queue = []
        self._result_poste = []
        self._status = set()
        manda_busy = {i+1 for i in range(5) if self.manda_poste[i]}  # initialize busy position
        leng = len(self.prior_poste)
        if leng:  # check prior characters' status initially
            for n in self.urp_filter_n(manda_busy):  # also feel free to loop, user will check it
                for p in self.prior_poste:
                    state_bot = list(self.manda_poste)
                    state_bot[n - 1] = p
                    state_bot = tuple(state_bot)
                    self._status.add(state_bot)
                    queue.append(state_bot)
            for i in range(leng - 1):
                queue_next = []
                for state in queue:
                    nums_bot = {i+1 for i, p in enumerate(state) if p}
                    busy_bot = {p for p in state if p}
                    for n in self.urp_filter_n(nums_bot):
                        for p in self.urp_filter_c(self.prior_poste, busy_bot):  # feel free, feel free
                            state_bot = list(state)
                            state_bot[n - 1] = p
                            state_bot = tuple(state_bot)
                            if state_bot in self._status:
                                continue
                            self._status.add(state_bot)
                            queue_next.append(state_bot)
                queue = queue_next
        leng = 5 - leng - len(manda_busy)
        if leng == 5:  # Why I code this module again?
            for n in self.urp_filter_n():
                # print(f"clist: {clist}")
                for p in solutions[clist[n-1]].supreme_arr:  # feel free, feel free
                    state_bot = list(self.state_base)
                    state_bot[n - 1] = p
                    state_bot = tuple(state_bot)
                    self._status.add(state_bot)
                    queue.append(state_bot)
            leng -= 1
        for i in range(leng):
            queue_next = []
            for state in queue:
                nums_bot = {i+1 for i, p in enumerate(state) if p}
                busy_bot = {p for p in state if p}
                for n in self.urp_filter_n(nums_bot):
                    poste_bot = self.urp_filter_dag(solutions[clist[n-1]], busy_bot)
                    for p in poste_bot:
                        state_bot = list(state)
                        state_bot[n - 1] = p
                        state_bot = tuple(state_bot)
                        if state_bot in self._status:
                            continue
                        self._status.add(state_bot)
                        queue_next.append(state_bot)
            queue = queue_next
        for q in queue:
            res_bot = [None] * 10
            res_bot[:5] = clist
            res_bot[5:10] = list(q)
            self._result_poste.append(tuple(res_bot))
        # for q in queue:
        #     res_bot = [None] * 10
        #     res_bot[0:9:2] = clist
        #     res_bot[1:10:2] = list(q)
        #     self._result_poste.append(tuple(res_bot))
        print(f"cost time {time.time() - stime}s in {len(queue)} solutions")
        return self._result_poste


def automatic_formation(
        userdata_path="./Yumesute.json",
        character_master_path="./data/CharacterMaster.json",
        poster_ability_path="./data/PosterAbilityMaster.json",
        effect_master_path="./data/EffectMaster.json",
        mandatory_characters=(150010, 0, 150020, 0, 150030, 0, 150040, 0, 0, 0),
        mandatory_posters=(330380, 0, 230120, 0, 0, 0, 0, 0, 0, 0),
        pipeline_queue=None
):
    start_time = time.time()

    with open(userdata_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)
    character_list = user_data["characters"]
    # poster_list = user_data["posters"]

    with open(character_master_path, "r", encoding="utf-8") as f:
        characters_data = json.load(f)
    characters_id_master = {item["Id"]: item for item in characters_data}

    current_time = time.time() - start_time
    print(f"check data in {current_time}s")

    c_cache = {}
    checker = CheckUnrepeated()
    for chara in character_list:
        c_id = chara[0]
        c_data = characters_id_master.get(c_id)
        filter_c_c = CharacterFilter()
        c_data_filtered = filter_c_c.apply(c_data)
        for c in c_data_filtered["CharacterBaseMasterId"]:
            checker.chara_mid2id[c].append(c_id)
        c_cache[c_id] = c_data_filtered
    # print(c_cache)
    checker.urp_filter_i(mandatory_characters, mandatory_posters, c_cache)
    poster_solutions = find_poster_solutions(userdata_path,
                                             character_master_path,
                                             poster_ability_path,
                                             effect_master_path)
    print(f"check characters...")
    result_c = checker.processor_character(c_cache)
    # print(f"[DEBUG] processor_character done, {len(result_c)} character combinations")
    put_count = 0
    for r in result_c:
        print(f"check posters...")
        charb_id = [None] * 5
        for n, c in enumerate(r):
            charb_id[n-1] = c_cache[c].get("CharacterBaseMasterId", [])
        result = checker.processor_poster(list(r), poster_solutions)
        if pipeline_queue is not None:
            pipeline_queue.put({"Result": result, "CharacterBaseMasterId": charb_id})
        #     put_count += 1
        #     if put_count % 100 == 0:
        #         print(f"[DEBUG] put {put_count} items into queue, queue size ~{pipeline_queue.qsize()}")
    # print(f"[DEBUG] finished putting {put_count} items, sending EOT")
    if pipeline_queue is not None:
        pipeline_queue.put(None)


# def parse_args():
#     parser = argparse.ArgumentParser(description='Yumesute auto team-up')
#     parser.add_argument('user', nargs='?', metavar='File name for user data', default='Yumetest.json', help='账号数据名称')
#     parser.add_argument('-d', '--data', metavar='DIR for server data', default='data', help='服务器内资源路径')
#     parser.add_argument('-mc', '--mandatory_characters', type=int, nargs=10, default=[0]*10,
#                         help='交替输入必选角色及其固定位置, 不选则填0, 以空格分割')
#     parser.add_argument('-mp', '--mandatory_posters', type=int, nargs=10, default=[0]*10,
#                         help='交替输入必选海报及其对应位置, 不选则填0, 以空格分割')
#     parser.add_argument('-ml', '--mandatory_leader', type=int, default=0, help='固定队长位置, 不选则填0')
#     parser.add_argument('-u', '--update', type=str, default='https://github.com/esterTion/yumesute_master_db_diff')
#     return parser.parse_args()


if __name__ == "__main__":
    automatic_formation()
    # import argparse
    # import os
    # args = parse_args()
    # userdata_path = os.path.join(args.user)
    # character_master_path = os.path.join(args.data, 'CharacterMaster.json')
    # poster_ability_path = os.path.join(args.data, 'PosterAbilityMaster.json')
    # accessory_path = os.path.join(args.data, 'accessory_processed.json')
    # effect_master_path = os.path.join(args.data, 'EffectMaster.json')
    # automatic_formation(
    #     userdata_path,
    #     character_master_path,
    #     poster_ability_path,
    #     effect_master_path,
    #     tuple(args.mandatory_characters),
    #     tuple(args.mandatory_posters)
    # )
