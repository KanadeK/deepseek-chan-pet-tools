# DeepSeek-chan Pet Tools / DeepSeek娘宠物工具

制作 DeepSeek娘动画宠物时实际使用的两个 Python 辅助脚本：从最终精灵图生成动画预览，以及统一基础动画的角色尺寸。

This repository contains the preview renderer and frame-registration helper used while creating a DeepSeek-chan animated pet. The tools process existing sprite pixels; they do not generate character artwork.

## 安装

需要 Python 3.9 或更新版本，以及 PATH 中可运行的 FFmpeg（支持 libx264）。

```bash
python -m pip install -r requirements.txt
```

## 生成预览

准备你自己的透明 RGBA 精灵图 `pet.png`，大小为 **1536×2288**，八列十一行，每格 **192×208**。

```bash
python render_final_previews.py --atlas pet.png --output-dir outputs/previews
```

输出九种状态的逐帧 PNG、带状态标注的全动作 GIF 和 MP4、待机→跳跃→待机 GIF、十六方向视线 GIF，以及四张带标注的静态帧。

| 行 | 状态 | 帧数 |
| --- | --- | ---: |
| 0 | idle / 待机 | 6 |
| 1 | running-right / 向右移动 | 8 |
| 2 | running-left / 向左移动 | 8 |
| 3 | waving / 挥手 | 4 |
| 4 | jumping / 跳跃 | 5 |
| 5 | failed / 失败反应 | 8 |
| 6 | waiting / 等待输入 | 6 |
| 7 | running / 工作、思考 | 6 |
| 8 | review / 检查成果 | 6 |
| 9–10 | 从正上方开始顺时针的十六个视线方向 | 8 + 8 |

每行从左侧填充，未使用单元格保持透明。播放时长由 `pet_layout.py` 定义。

## 修正基础动画尺寸

此脚本针对本次制作中出现的情况：提取器为跳跃预留了上方空间，导致其身体比其他状态小。它以跳跃的起始、落地帧身高为参照，给全部非跳跃状态应用一个共同缩放，不改变跳跃高度或各行帧序。

输入是已提取的 192×208 PNG 帧目录，例如 `frames/idle/00.png`、`frames/jumping/00.png` 和 `frames/jumping/04.png`。

```bash
python register_standard_frames.py --frames-root frames --report registration.json
```

**它会原地修改帧目录**，并先在同级创建 `frames-before-registration` 完整备份。若备份已存在，脚本拒绝再次运行。适用条件是本次提取器采用约 203 像素落地基线、非跳跃行已经使用共同尺度，且所需缩放比例处于 0.8–1.0；其他情况应先检查源图。该操作完成后需要重新合成和验证精灵图。

## 制作流程与范围

1. 确认参考角色形象。
2. 生成统一主形象，再分别生成九种动作条、四个主要视线方向与两个八帧视线条。
3. 提取完整连通角色，保留跳跃的垂直位移，统一尺度与落地位置。
4. 合成精灵图，清理背景边缘，检查透明空格、动作语义和方向连续性。
5. 使用这里的脚本生成预览。完整 Pets 创建流程仍需其内置验证器及上传、创建、选择工具。

预览渲染只检查尺寸，不能代替精灵图结构验证或人工视觉验收。Pets 插件自带的生成、提取、合成、验证脚本与服务端实现不在本仓库分发。

## 角色素材来源

本次角色参考来自 [Q版三视图](https://aigengtu.com/zh/meme/064)、[「最强」表情图](https://aigengtu.com/zh/meme/079)，形象来源说明参见 ZipZipPipe 的 [《大AI和小AI们》](https://www.bilibili.com/video/BV1tE9XBbErS/)。

本仓库发布代码和流程说明。角色图片、原始参考图、个人宠物 ID、上传会话及临时下载链接不随代码发布。MIT 许可证覆盖本仓库代码与文档，不对第三方角色形象作出授权；使用角色素材需遵循其原作者条件。

## 验证

公开前使用本次实际生成的 v2 精灵图运行预览脚本，并在原始帧副本上运行配准脚本；确认产出 GIF、MP4、57 张基础动画帧和 16 个视线方向，配准保留起跳与落地差异。

## License

[MIT](LICENSE)
