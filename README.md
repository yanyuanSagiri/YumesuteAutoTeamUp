# YumesuteAutoTeamUp
Auto team-up script for Yumesute

ymst自动配队器

### 账号数据提取

通过 https://redive.estertion.win/wds/calc/YumesuteExporter.exe 提取账号的 .json 文件

### 游戏内数据资源

https://github.com/esterTion/yumesute_master_db_diff

配队器需要**当前版本**的:

- CharacterMaster.json: 用来检索账号所拥有的角色的相关数据.
- PosterAbilityMaster.json: 用来检索账号所拥有的海报的相关数据.
- EffectMaster.json: 用来检索已有(角色和)海报的词条

~~没抽卡就不用~~

### 目前使用方法

已修改输入逻辑, 允许确定队长位置, 允许设置必选角色/海报, 允许固定必选角色/海报位置.

目前支持输入的参数包括:

| 参数    | 类型        | 默认值                  | 必需  | 说明                                         |
|-------|-----------|----------------------|-----|--------------------------------------------|
| `-mc` | `int[10]` | `[0]*10`             | 否   | 结构类似 `[必选角色1, 其固定位置1, ...]` <br> 无需求则补 `0` |
| `-mp` | `int[10]` | `[0]*10`             | 否   | 结构类似 `[必选海报1, 其固定位置1, ...]` <br> 无需求则补 `0` |
| `-ml` | `int`     | 0                    | 否   | 固定队长位置                                     |
| `-u`  | `string`  | 游戏内数据资源              | 否   | 更新角色, 海报等资源的信息                             |
| `-d`  | `string`  | `/path/to/your/data` | 否   | 本地存储游戏内数据的路径                               |

已提供简易脚本于 `/scripts` 中.
输出是一个list, 每项为长度 `10` 的元组, 为队伍匹配结果.

`
(角色1, 海报1, 角色2, 海报2, 角色3, 海报3, 角色4, 海报4, 角色5, 海报5)
`