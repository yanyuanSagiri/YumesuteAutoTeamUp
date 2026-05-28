# YumesuteAutoTeamUp
Auto team-up script for Yumesute

ymst自动配队器

## 账号数据提取

通过 https://redive.estertion.win/wds/calc/YumesuteExporter.exe 提取账号的 .json 文件

## 游戏内数据资源

配队器需要**当前版本**的:

- `CharacterMaster.json`: 用来检索账号所拥有的角色的相关数据.
- `PosterAbilityMaster.json`: 用来检索账号所拥有的海报的相关数据.
- `EffectMaster.json`: 用来检索已有(角色和)海报的词条.
- `accessory_processed.json`: 用来进行饰品筛选. 该文件为本项目特别设计, 请在本仓库中进行下载.

~~当然, 没抽卡就不用~~

你也可以通过如下方式进行游戏数据的部署, **注意会下载全部文件**. 其他的在 server 中可能用到.

- 直接访问及时更新的[Database地址](https://github.com/esterTion/yumesute_master_db_diff)进行下载.
- 等效地, 可以在本地的 git bash 中执行

```bash
git clone https://github.com/esterTion/yumesute_master_db_diff
```

该命令将会在你选择的当前 git bash 路径生成名为 `yumesute_master_db_diff` 的, 包含其内容的文件夹.

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

该命令将会在你选择的当前 git bash 路径直接下载每个文件.

## 目前使用方法

已修改输入逻辑, 允许确定队长位置, 允许设置必选角色/海报, 允许固定必选角色/海报位置.

目前支持输入的参数包括:

| 参数     | 类型        | 默认值                  | 必需  | 说明                                                     |
|--------|-----------|----------------------|-----|--------------------------------------------------------|
| `user` | `str`     | `Yumesute.json`      | 否   | 无需输入 `user`, 直接输入(放置到项目根目录的)账号数据全称即可. <br> **名称不允许空格** |
| `-mc`  | `int[10]` | `[0]*10`             | 否   | 结构类似 `[必选角色1, 其固定位置1, 必选角色2, ...]` <br> 无需求则补 `0`      |
| `-mp`  | `int[10]` | `[0]*10`             | 否   | 结构类似 `[必选海报1, 其固定位置1, 必选海报2, ...]` <br> 无需求则补 `0`      |
| `-ml`  | `int`     | 0                    | 否   | 固定队长位置                                                 |
| `-u`   | `string`  | 游戏内数据资源              | 否   | 更新角色, 海报等资源的信息                                         |
| `-d`   | `string`  | `/path/to/your/data` | 否   | 本地存储游戏内数据资源的路径                                         |

已提供简易脚本于 `/scripts` 中. 你可以通过

```bash
git bash your_path_to_root/scripts/teamup.sh [账号数据地址] [参数1] [值] [参数2] [值] [...]
```

运行配队器. 输出根据 @[Ohnkyta](https://github.com/OhnkytaBlabdey) 的 ymst-calc-server 要求, 提供:

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

(实际上server那边没做好, 角色/海报/饰品都套了网页版输入编队的 `partyManager` 的逻辑, 属无效的下标映射. **等待 @[Ohnkyta](https://github.com/OhnkytaBlabdey) 完善代码后才可使用**)