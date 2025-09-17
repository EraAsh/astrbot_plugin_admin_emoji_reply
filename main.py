import asyncio
import json
from pathlib import Path
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig

@register(
    "admin_emoji_reply",
    "EraAsh",
    "为指定QQ号的消息自动添加表情回应",
    "1.6.0",
    "https://github.com/EraAsh/astrbot_plugin_admin_emoji_reply"
)
class AdminEmojiReply(Star):
    # ... (EMOJI_NAME_TO_ID_MAP 省略，与之前版本相同)
    EMOJI_NAME_TO_ID_MAP = {
        "得意": 4, "流泪": 5, "睡": 8, "大哭": 9, "尴尬": 10, "调皮": 12, "微笑": 14, "酷": 16, "可爱": 21,
        "傲慢": 23, "饥饿": 24, "困": 25, "惊恐": 26, "流汗": 27, "憨笑": 28, "悠闲": 29, "奋斗": 30, "疑问": 32,
        "嘘": 33, "晕": 34, "敲打": 38, "再见": 39, "发抖": 41, "爱情": 42, "跳跳": 43, "拥抱": 49, "蛋糕": 53,
        "咖啡": 60, "玫瑰": 63, "爱心": 66, "太阳": 74, "月亮": 75, "赞": 76, "握手": 78, "胜利": 79, "飞吻": 85,
        "西瓜": 89, "冷汗": 96, "擦汗": 97, "抠鼻": 98, "鼓掌": 99, "糗大了": 100, "坏笑": 101, "左哼哼": 102,
        "右哼哼": 103, "哈欠": 104, "委屈": 106, "左亲亲": 109, "可怜": 111, "示爱": 116, "抱拳": 118, "拳头": 120,
        "爱你": 122, "NO": 123, "OK": 124, "转圈": 125, "挥手": 129, "喝彩": 144, "棒棒糖": 147, "茶": 171,
        "泪奔": 173, "无奈": 174, "卖萌": 175, "小纠结": 176, "doge": 179, "惊喜": 180, "骚扰": 181, "笑哭": 182,
        "我最美": 183, "点赞": 201, "托脸": 203, "托腮": 212, "啵啵": 214, "蹭一蹭": 219, "抱抱": 222, "拍手": 227,
        "佛系": 232, "喷脸": 240, "甩头": 243, "加油抱抱": 246, "脑阔疼": 262, "捂脸": 264, "辣眼睛": 265, "哦哟": 266,
        "头秃": 267, "问号脸": 268, "暗中观察": 269, "emm": 270, "吃瓜": 271, "呵呵哒": 272, "我酸了": 273,
        "汪汪": 277, "汗": 278, "无眼笑": 281, "敬礼": 282, "面无表情": 284, "摸鱼": 285, "哦": 287, "睁眼": 289,
        "敲开心": 290, "摸锦鲤": 293, "期待": 294, "拜谢": 297, "元宝": 298, "牛啊": 299, "右亲亲": 305,
        "牛气冲天": 306, "喵喵": 307, "仔细分析": 314, "加油": 315, "崇拜": 318, "比心": 319, "庆祝": 320,
        "拒绝": 322, "吃糖": 324, "生气": 326,
        "晴天": 9728, "闪光": 10024, "错误": 10060, "问号": 10068, "苹果": 127822,
        "草莓": 127827, "拉面": 127836, "面包": 127838, "刨冰": 127847, "啤酒": 127866, "干杯": 127867,
        "虫": 128027, "牛": 128046, "鲸鱼": 128051, "猴": 128053, "好的": 128076, "厉害": 128077,
        "内衣": 128089, "男孩": 128102, "爸爸": 128104, "礼物": 128157, "睡觉": 128164, "水": 128166,
        "吹气": 128168, "肌肉": 128170, "邮箱": 128235, "火": 128293, "呲牙": 128513, "激动": 128514,
        "高兴": 128516, "嘿嘿": 128522, "羞涩": 128524, "哼哼": 128527, "不屑": 128530, "失落": 128532,
        "淘气": 128540, "吐舌": 128541, "紧张": 128560, "瞪眼": 128563,
    }

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.data_dir = Path("data/plugins/admin_emoji_reply")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.data_dir / "status.json"
        self.enabled = self._load_status()

    def _load_status(self) -> bool:
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("enabled", True)
        except Exception as e:
            logger.error(f"加载插件状态失败: {e}")
        return True # 默认为开启

    def _save_status(self):
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump({"enabled": self.enabled}, f)
        except Exception as e:
            logger.error(f"保存插件状态失败: {e}")

    @filter.command("打开表情回复", permission=filter.Permission.ADMIN)
    async def enable_reply(self, event: AstrMessageEvent):
        """启用自动表情回复功能"""
        self.enabled = True
        self._save_status()
        yield event.plain_result("✅ 自动表情回复已开启")

    @filter.command("关闭表情回复", permission=filter.Permission.ADMIN)
    async def disable_reply(self, event: AstrMessageEvent):
        """禁用自动表情回复功能"""
        self.enabled = False
        self._save_status()
        yield event.plain_result("☑️ 自动表情回复已关闭")

    @filter.event_message_type(filter.EventMessageType.ALL, priority=99)
    async def auto_react_to_target_message(self, event: AstrMessageEvent):
        if not self.enabled:
            return

        target_qq_list = self.config.get("target_qq_ids", [])
        if not target_qq_list:
            return

        sender_id = event.get_sender_id()
        if not sender_id or str(sender_id) not in target_qq_list:
            return

        if event.get_platform_name() != "aiocqhttp":
            return
            
        from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
        if not isinstance(event, AiocqhttpMessageEvent):
            return

        emoji_configs = self.config.get("emoji_names", [])
        if not emoji_configs:
            return

        emoji_ids_to_send = []
        for emoji_str in emoji_configs:
            if not isinstance(emoji_str, str):
                logger.warning(f"配置的表情 '{emoji_str}' 不是一个有效字符串，已跳过。")
                continue
            
            if emoji_str in self.EMOJI_NAME_TO_ID_MAP:
                emoji_ids_to_send.append(str(self.EMOJI_NAME_TO_ID_MAP[emoji_str]))
            elif len(emoji_str) == 1:
                try:
                    codepoint = ord(emoji_str)
                    if codepoint > 256:
                        emoji_ids_to_send.append(str(codepoint))
                    else:
                        logger.warning(f"配置的表情 '{emoji_str}' 是一个普通字符，而非Emoji，已跳过。")
                except TypeError:
                    logger.warning(f"无法处理配置的表情 '{emoji_str}'，它不是一个有效的Unicode字符。")
            else:
                logger.warning(f"配置的表情 '{emoji_str}' 无效，必须是单个Unicode Emoji字符或官方支持的表情中文名，已跳过。")

        if not emoji_ids_to_send:
            return

        try:
            client = event.bot
            message_id = event.message_obj.message_id
            
            tasks = []
            for emoji_id in emoji_ids_to_send:
                tasks.append(
                    client.api.call_action('set_msg_emoji_like', message_id=message_id, emoji_id=emoji_id)
                )
            
            if tasks:
                for i, task_coro in enumerate(tasks):
                    try:
                        # 不再使用延时，以加快速度
                        await task_coro
                    except Exception as res:
                        logger.error(f"为表情ID {emoji_ids_to_send[i]} 添加回应失败: {res}")

        except Exception as e:
            logger.error(f"添加表情回应时发生未知错误: {e}")
