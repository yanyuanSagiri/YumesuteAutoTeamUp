"""
ActorFormation module is used for building formation automatically.
Input: relative files' path.
Output: N-Top results among all status.
"""
import json, copy, time

from FindPosterSolutions import find_poster_solutions, CharacterFilter
from collections import defaultdict, deque


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
        self.posit_master = {1: None, 2: None, 3: None, 4: None, 5: None}
        self.POSIT = False
        self.num_master = {1, 2, 3, 4, 5}
        self.team_final = [None] * 10
        self.charb_busy = set()
        self.poste_busy = set()
        self.chara_mid2id = defaultdict(list)
        self._status = set()
        self._result = []

    def urp_filter_c(self, posit, c_cache):
        if self.posit_master[posit]:
            return {self.posit_master[posit][0]}
        cm_bot = self.chara_master.copy()
        for c in self.charb_busy:
            cm_bot.discard(c)
        c_bot = set()
        for c in cm_bot:
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
                    if j in self.charb_busy or j == charb[0]:
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

    def urp_filter_l(self, charb, poste, posit, c_cache):
        if charb:
            characters = c_cache[charb].get("CharacterBaseMasterId")
            for c in characters:
                self.charb_busy.add(c)
        if poste:
            self.poste_busy.update(poste)
        if posit in [1, 2, 3, 4, 5]:
            self.posit_master[posit] = [charb, poste]
            self.team_final[(posit << 1) - 2] = charb
            self.team_final[(posit << 1) - 1] = poste
            self.POSIT = True
            self.num_master.discard(posit)

    def urp_filter_n(self, num_busy=None):  # check {1, 2, 3, 4, 5} which is used and discard
        number_bot = self.num_master.copy()
        if num_busy:
            for n in num_busy:
                number_bot.discard(n)
        return number_bot

    # def urp_bfs_p(self, team_f, posit_id, chara_poste):
        # for p in posit_id:
        #     c_id = (p - 1) << 1
        #     p_id = (p << 1) - 1
        #     avail_poste = self.urp_filter_dag(chara_poste[team_f[c_id]])

    def poster_processor(self, c1, c2, c3, c4, c5, solutions):
        # stime = time.time()
        self._result = []
        self._status = set()
        posit_bot = self.team_final.copy()
        posit_bot[0:9:2] = [c1, c2, c3, c4, c5]
        queue = deque()
        for n in self.urp_filter_n():  # generate initial queue status
            c_id = (n - 1) << 1
            # print(f"now set position{n}")
            poste_bot = self.urp_filter_dag(solutions[posit_bot[c_id]], self.poste_busy)
            # print(poste_bot)
            for p in poste_bot:
                state = frozenset({(n, p)})
                # print(f"put poster {p} at position {n}")
                self._status.add(state)
                queue.append(state)
        q_len = 5 - len(self.poste_busy)  # depth
        for i in range(q_len - 1):
            next_queue = []
            for state in queue:
                nums_bot = {n for n, _ in state}
                busy_bot = {b for _, b in state} | self.poste_busy
                # print(f"now check frontier state {state}")
                # print(f"positions: {nums_bot}")
                # print(f"posters: {busy_bot}")
                for n in self.urp_filter_n(nums_bot):
                    # print(f"try put poster at position {n}")
                    c_id = (n - 1) << 1
                    poste_bot = self.urp_filter_dag(solutions[posit_bot[c_id]], busy_bot)
                    # print(poste_bot)
                    for p in poste_bot:
                        state_bot = state | {(n, p)}
                        # print(state_bot)
                        if state_bot in self._status:
                            # print(f"skipped")
                            continue
                        else:
                            # print(f"add state {state_bot}")
                            self._status.add(state_bot)
                            next_queue.append(state_bot)
            queue = next_queue
            # if i+2 == 4:
                # print(f"4 posters cost time {time.time() - stime}")
            # print(f"Check status: {i+2}/{q_len}")
        # print(queue)
        for q in queue:
            res_bot = [None] * 10
            res_bot[0:9:2] = [c1, c2, c3, c4, c5]
            for n, p in q:
                res_bot[(n << 1) - 1] = p
            # print(res_bot)
            self._result.append(res_bot)
        return self._result

        # self.urp_bfs_p(posit_bot, self.urp_filter_n(), solutions)
        # for i1 in self.urp_filter_n():  # place poster in sequence for fixed characters
        #     for i2 in self.urp_filter_n():
        #         for i3 in self.urp_filter_n():
        #             for i4 in self.urp_filter_n():
        #                 if self.POSIT:
        #                     self.urp_filter_p(posit_bot, [i1, i2, i3, i4], solutions)
        #                 else:
        #                     for i5 in self.urp_filter_n():
        #                         self.urp_filter_p(posit_bot, [i1, i2, i3, i4, i5], solutions)
        # self.urp_filter_p(c1, solutions[c1]):


def automatic_formation(
        userdata_path="./Yumesute.json",
        character_master_path="./CharacterMaster.json",
        leader_character=0, leader_poster=0, leader_position=0
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
    print(f"check data in {current_time} s")

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
    checker.urp_filter_l(leader_character, leader_poster, leader_position, c_cache)
    poster_solutions = find_poster_solutions()
    for c1 in checker.urp_filter_c(1, c_cache):
        data_c1 = c_cache.get(c1).get("CharacterBaseMasterId")
        checker.charb_busy.update(data_c1)
        for c2 in checker.urp_filter_c(2, c_cache):
            data_c2 = c_cache.get(c2).get("CharacterBaseMasterId")
            checker.charb_busy.update(data_c2)
            for c3 in checker.urp_filter_c(3, c_cache):
                data_c3 = c_cache.get(c3).get("CharacterBaseMasterId")
                checker.charb_busy.update(data_c3)
                for c4 in checker.urp_filter_c(4, c_cache):
                    data_c4 = c_cache.get(c4).get("CharacterBaseMasterId")
                    checker.charb_busy.update(data_c4)
                    for c5 in checker.urp_filter_c(5, c_cache):
                        data_c5 = c_cache.get(c5).get("CharacterBaseMasterId")
                        # checker.charb_busy.update(data_c5)
                        start_time = time.time()
                        checker.poster_processor(c1, c2, c3, c4, c5, poster_solutions)
                        current_time = time.time() - start_time
                        print(f"check all posters results in one character formation in {current_time} s")
                        # checker.charb_busy.difference_update(data_c5)
                    checker.charb_busy.difference_update(data_c4)
                checker.charb_busy.difference_update(data_c3)
            checker.charb_busy.difference_update(data_c2)
        checker.charb_busy.difference_update(data_c1)


resource_path = (
    "./Yumetest.json",
    "./CharacterMaster.json",
    "./PosterAbilityMaster.json",
    "./EffectMaster.json"
)

if __name__ == "__main__":
    automatic_formation()
