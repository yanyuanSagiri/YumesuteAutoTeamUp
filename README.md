# YumesuteAutoTeamUp
Auto team-up script for Yumesute

ymst自动配队器

### 账号数据提取

通过 https://redive.estertion.win/wds/calc/YumesuteExporter.exe 提取账号的 .json 文件

### 游戏内数据资源

https://github.com/esterTion/yumesute_master_db_diff

配对器需要当前版本的:

- CharacterMaster.json: 用来检索账号所拥有的角色的相关数据.
- PosterAbilityMaster.json: 用来检索账号所拥有的海报的相关数据.
- EffectMaster.json: 用来检索已有(角色和)海报的词条

### 目前使用方法

在 ActorFormation.py 中完成路径匹配即可. 输出是队伍的匹配结果列表.