# YumesuteAutoTeamUp
Auto team-up script for Yumesute

ymst自动配队器

目前仍在绝赞开发中, 但是其他部分的时间开销还是太大了而且没优化, 适配了也没用, 所以暂时用不了. ~~等 js 的前端计算器搬到后端来先~~

## 1. 账号数据提取

首先, 你需要将你游戏账号的数据导出.

唯一推荐的途径是通过 [@esterTion](https://github.com/esterTion) 提供的[引继码导出工具](https://redive.estertion.win/wds/calc/YumesuteExporter.exe), 提取账号的 .json 文件.
当然想自己解包也行, 你需要确保数据文件的格式类似为:

```text
{
  "characters": [[142360,255,1,2,5,5],[150040,260,true,2,5,5],[Id,等级(略),觉醒(略),故事(略),技能(略),开花(略)]],
  "posters": [[230330,6,0],[330380,10,4],[Id,等级,突破次数]],
  "accessories": [[330010,10,0],[320370,1,112],[Id,等级(略),下标(略)]],
}
```

其他内容实际上用不到, 可以直接全塞进来也可以不提供. 引继码导出工具默认提供所有 key, 可以直接拿来用.

## 2. 游戏内数据资源相关

角色/海报/饰品详细信息是存储在这类文件中的, 所以在得到你的账号数据后, 需要在这些文件中找到具体数据, 以进行具体的配队优化.

配队器需要**当前版本**的:

- `CharacterMaster.json`: 用来检索账号所拥有的角色的相关数据.
- `PosterAbilityMaster.json`: 用来检索账号所拥有的海报的相关数据.
- `EffectMaster.json`: 用来检索已有(角色和)海报的词条.
- `accessory_processed.json`: 用来进行饰品筛选. 该文件为本项目特别设计, 请在本仓库中进行下载.

~~当然, 没抽卡就不用~~

目前已将资源更新单独设计为一个模块, 运行 `/scripts/update.sh` 即可. 建议直接使用 git bash 运行.

---

如果因为网络或者其他问题导致自动更新脚本不可用, 你也可以暂时通过以下任一方式进行游戏数据的部署. **注意会下载全部文件**. 但其他文件在 server 中可能用到, 顺手的事儿.

- 直接访问及时更新的[Database地址](https://github.com/esterTion/yumesute_master_db_diff)进行下载.
- 等效地, 可以在本地的 git bash 中执行

```bash
git clone https://github.com/esterTion/yumesute_master_db_diff
```

该命令将会在终端的当前路径生成名为 `yumesute_master_db_diff` 的, 包含其内容的文件夹.

- 若未安装 git, 则可复制下面所有命令, 在 Powershell 中点击右键粘贴:

```shell
$baseUrl = "https://redive.estertion.win/wds/calc/master/"
$response = Invoke-WebRequest -Uri $baseUrl

$pattern = 'href="([^"]+\.(json|txt|version))"'
$matches = [regex]::Matches($response.Content, $pattern)

foreach ($match in $matches) {
    $filename = $match.Groups[1].Value
    $fileUrl = $baseUrl + $filename
    $outputPath = Join-Path -Path "." -ChildPath $filename
    
    Write-Host "正在下载: $filename" -ForegroundColor Green
    Invoke-WebRequest -Uri $fileUrl -OutFile $outputPath
}
```

该命令将会在终端的当前路径直接下载每个文件.

## 3. 目前使用方法

已修改输入逻辑, 允许确定队长位置, 允许设置必选角色/海报, 允许固定必选角色/海报位置.

### 3.0 注意事项

关于配队器的原理:

- 本配队器仅对海报和饰品选择进行了优化, 角色方面还是普通的去重加暴力搜索, 且在计算模块没完成前, 本人并不打算做角色部分的优化.
- 因此角色的状态很多, 请尽量确保多选择绝对用得上的角色, 待选角色数量也必须控制. ~~游戏强度迭代这么快, 很老的用不到的卡一眼看得出来, 请你作为专家系统自己处理预输入.~~
- 海报的状态同理, 但是写了 pareto 前沿进行词条剪枝, 目前能 hack 掉 99.961% 的海报组合. 因此在尽量多选择绝对用得上的海报的前提下, 剩余的空位可以放入你的整个 box, 影响不大.
- 建议至少选 `3` 个及以上必须入队的指定角色卡(不是角色), 以及 `2` 个及以上必须入队的海报. 像vs/星轮和fd这种必选的请不要让配队器考虑.

关于用户输入:

- ~~目前的 CLI 估计需要一点技术门槛, 之后看看有没有群友适配个 GUI~~
- 关于角色. 参数是先输入 `角色id`, 随后一个参数是其固定的轴(`1, .., 5`), 然后交替.
- 关于海报, 参数是先输入 `海报id`, 随后一个参数是其捆绑的 `角色id`, 然后交替.
- 详细配置见 3.1.

### 3.1 开始使用

已提供简易脚本于 `/scripts` 中. 你可以通过运行其中的 `teamup.sh` 开始配队. (推荐使用 git bash)

在终端通过输入指定参数可以实现个性化配队. 

```bash
git bash your_path_to_root/scripts/teamup.sh [账号数据地址] [参数1] [值] [参数2] [值] [...]
```

具体来说, 可以这样:

```bash
# 为方便展示, 使用 \ 作为换行符
<path_to_scripts> bash ./teamup.sh userdata717.json \
-mc 150010 0 150020 0 150030 0 150040 0 0 0 \
-mp 330380 150030 230120 150040 0 0 0 0 0 0 \
-ml 3
```

目前支持输入的参数包括:

| 参数     | 类型        | 默认值                  | 必需  | 说明                                                                                                             |
|--------|-----------|----------------------|-----|----------------------------------------------------------------------------------------------------------------|
| `user` | `str`     | `Yumesute.json`      | 否   | 是你的用户数据 `xxx.json`. 把它放在配队器项目的根目录. <br> 使用时无需输入 `user`, 直接输入 `xxx.json` 即可. <br> **名称中间不允许空格 ~~`x xx.json`~~** |
| `-mc`  | `int[10]` | `[0]*10`             | 否   | 结构类似 `[必选角色1, 其固定位置1, 必选角色2, ...]` <br> 无需求则补 `0`                                                              |
| `-mp`  | `int[10]` | `[0]*10`             | 否   | 结构类似 `[必选海报1, 绑定的角色i, 必选海报2, ...]` <br> 无需求则补 `0`                                                              |
| `-ml`  | `int`     | 0                    | 否   | 固定队长位置                                                                                                         |
| `-d`   | `string`  | `/path/to/your/data` | 否   | 本地存储游戏内数据资源的路径                                                                                                 |

### 3.2 配队状态输出格式与请求体相关

输出根据 [@Ohnkyta](https://github.com/OhnkytaBlabdey) 的 ymst-calc-server 要求, 提供:

```json
    {
        "data_file": "example.json",
        "team": {
            "actors": [142360, 150040, 150030, 150020, 150010],
            "posters": [340210, 330230, 330290, 230840, 330310],
            "accessories": [430220, 331710, 331710, 331710, 331710],
            "leader": 0
        },
        "sensenotation": 1146,
        "score_only": false
    }
```

至默认的端口 `3456` 上.

~~但那边有点小问题, 而且我看 server 这种有点太影响效率了, 毕竟这玩意儿是计算密集型, 还是等适配吧~~

### 3.3 结果筛选与统计

这部分暂时用不到, 不写.

预计会维护一个类似带字典的小根堆, 维护每个角色/海报状态下的最优解, 饰品和队长部分直接去重.