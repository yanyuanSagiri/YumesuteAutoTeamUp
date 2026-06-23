# Yumesute 自动组队工具

## 项目简介

Yumesute 自动组队工具是一个基于 Python 的异步程序，用于自动生成游戏最优阵容。程序通过标准输入接收用户数据，经过算法处理后，通过标准输出返回组队结果。

## 使用方法

```bash
python Start.py [user] [options]
```

### 基本示例

```bash
# 使用默认参数
echo '{"characters":[], "posters":[], "accessories":[]}' | python Start.py

# 指定用户数据文件
python Start.py Yumetest.json

# 通过管道传入用户数据
python Start.py < Yumetest.json

# 自定义必选角色和海报
python Start.py -mc 150010 1 150020 0 0 0 0 0 0 0 -mp 330380 150030 0 0 0 0 0 0 0 0
```

## 命令行参数

| 参数 | 缩写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `user` | - | 字符串 | `Yumesute.json` | 用户数据文件名 |
| `--data` | `-d` | 字符串 | `data` | 游戏资源数据目录路径 |
| `--mandatory_characters` | `-mc` | 整数列表(10个) | `[150010, 0, 150020, 0, 150030, 0, 150040, 0, 0, 0]` | 必选角色及其固定位置（交替输入：角色ID, 位置） |
| `--mandatory_posters` | `-mp` | 整数列表(10个) | `[330380, 150030, 230120, 150040, 0, 0, 0, 0, 0, 0]` | 必选海报及其绑定角色（交替输入：海报ID, 角色ID） |

### 必选角色参数格式

`-mc` 参数接受 10 个整数，按以下格式交替输入：

```
角色1ID 角色1位置 角色2ID 角色2位置 ...
```

- 角色ID 或位置为 `0` 表示不固定

### 必选海报参数格式

`-mp` 参数接受 10 个整数，按以下格式交替输入：

```
海报1ID 绑定角色1ID 海报2ID 绑定角色2ID ...
```

- 海报ID 或绑定角色ID 为 `0` 表示不固定

## 输入格式

程序通过标准输入（stdin）接收 JSON 格式的用户数据：

```json
{
  "characters": [...],
  "posters": [...],
  "accessories": [...]
}
```

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `characters` | 数组 | 用户拥有的角色列表 |
| `posters` | 数组 | 用户拥有的海报列表 |
| `accessories` | 数组 | 用户拥有的饰品列表 |

## 输出格式

程序通过标准输出（stdout）输出 JSON 格式的组队结果：

### 正常输出

每行一个 JSON 对象，表示一个组队方案：

```json
{"team": [...], "score": ...}
```

### 结束标志

```json
{"FIN": true}
```

### 错误输出

```json
{"error": "错误信息"}
```

## 核心功能模块

### 1. `parse_args()`

解析命令行参数，返回参数对象。

### 2. `stdin_reader(fin: asyncio.Event)`

异步读取标准输入，处理外部反馈：
- 监听输入流，解析 JSON 消息
- 收到 `{"FIN": true}` 时触发结束事件
- 预留处理团队状态和分数的接口（TODO）

### 3. `stdout_writer(que: asyncio.Queue)`

异步写入标准输出：
- 从队列中获取组队结果
- 转换为 JSON 并输出
- 收到 `None` 时输出结束标志并退出

### 4. `state_expander(sync_queue, out_queue, accessory_user, accessory_list, leader)`

状态扩展器，处理阵容的饰品搭配：
- 从同步队列获取基础阵容
- 调用 `processor_accessory` 处理饰品组合
- 将扩展后的完整阵容放入输出队列

### 5. `main()`

主函数，协调整个流程：
1. 解析命令行参数
2. 从标准输入读取用户数据
3. 加载游戏资源数据
4. 创建异步任务：读取器、写入器、状态扩展器
5. 调用 `automatic_formation` 生成基础阵容
6. 等待所有任务完成

## 数据流

```
stdin (用户数据)
    │
    ▼
┌─────────────────────┐
│   main() 初始化     │
│   加载资源数据      │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ automatic_formation │ ← ActorFormation.py
│ 生成基础阵容        │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  state_expander     │ ← pipeline.py
│  扩展饰品组合        │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│   stdout_writer     │
│   输出组队结果      │
└─────────────────────┘
    │
    ▼
stdout (JSON 结果)
```

## 依赖项

### 标准库

- `argparse` - 命令行参数解析
- `os` - 文件路径操作
- `asyncio` - 异步编程支持
- `json` - JSON 数据处理
- `queue` - 线程安全队列
- `sys` - 标准输入输出

### 项目模块

- `ActorFormation` - 角色阵容生成算法（`automatic_formation`）
- `pipeline` - 饰品处理流程（`processor_accessory`）

## 数据文件

程序运行需要以下数据文件（位于 `data` 目录下）：

| 文件名 | 说明 |
|--------|------|
| `CharacterMaster.json` | 角色主数据 |
| `PosterAbilityMaster.json` | 海报能力主数据 |
| `accessory_processed.json` | 饰品处理数据 |
| `EffectMaster.json` | 效果主数据 |

## 注意事项

1. 程序使用异步架构，通过标准输入/输出与外部进程通信
2. 必选角色和海报参数必须严格按格式输入 10 个整数
3. 用户数据必须包含 `characters`、`posters`、`accessories` 三个必填字段
4. 程序结束后会输出 `"Finished"` 提示
