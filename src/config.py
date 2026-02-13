from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv
import os


@dataclass
class Config:
    """
    系统配置类 - 单例模式

    设计说明：
    - 使用 dataclass 简化配置属性定义
    - 所有配置项从环境变量读取，支持默认值
    - 类方法 get_instance() 实现单例访问
    """

    # === 券商（长桥）配置 ===
    longport_app_key: Optional[str] = None
    longport_app_secret: Optional[str] = None
    longport_access_token: Optional[str] = None
    longport_log_path: Optional[str] = None

    # === 自选股配置 ===
    stock_list: List[str] = field(default_factory=list)

    # === 飞书云文档配置 ===
    feishu_app_id: Optional[str] = None
    feishu_app_secret: Optional[str] = None
    feishu_folder_token: Optional[str] = None  # 目标文件夹 Token

    # === AI 分析配置 ===
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-3-flash-preview"  # 主模型
    gemini_model_fallback: str = "gemini-2.5-flash"  # 备选模型
    gemini_temperature: float = 0.7  # 温度参数（0.0-2.0，控制输出随机性，默认0.7）

    # Gemini API 请求配置（防止 429 限流）
    gemini_request_delay: float = 2.0  # 请求间隔（秒）
    gemini_max_retries: int = 5  # 最大重试次数
    gemini_retry_delay: float = 5.0  # 重试基础延时（秒）

    # OpenAI 兼容 API（备选，当 Gemini 不可用时使用）
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None  # 如: https://api.openai.com/v1
    openai_model: str = "gpt-4o-mini"  # OpenAI 兼容模型名称
    openai_temperature: float = 0.7  # OpenAI 温度参数（0.0-2.0，默认0.7）

    # === 搜索引擎配置（支持多 Key 负载均衡）===
    bocha_api_keys: List[str] = field(default_factory=list)  # Bocha API Keys
    tavily_api_keys: List[str] = field(default_factory=list)  # Tavily API Keys
    brave_api_keys: List[str] = field(default_factory=list)  # Brave Search API Keys
    serpapi_keys: List[str] = field(default_factory=list)  # SerpAPI Keys

    # === 通知配置（可同时配置多个，全部推送）===

    # 飞书 Webhook
    feishu_webhook_url: Optional[str] = None

    # 单股推送模式：每分析完一只股票立即推送，而不是汇总后推送
    single_stock_notify: bool = False

    # 报告类型：simple(精简) 或 full(完整)
    report_type: str = "simple"

    # 分析间隔时间（秒）- 用于避免API限流
    analysis_delay: float = 0.0  # 个股分析与大盘分析之间的延迟

    # 消息长度限制（字节）- 超长自动分批发送
    feishu_max_bytes: int = 20000  # 飞书限制约 20KB，默认 20000 字节

    # === 数据库配置 ===
    database_path: Optional[str] = ":memory:"

    # 是否保存分析上下文快照（用于历史回溯）
    save_context_snapshot: bool = True

    # === 回测配置 ===
    backtest_enabled: bool = True
    backtest_eval_window_days: int = 10
    backtest_min_age_days: int = 14
    backtest_engine_version: str = "v1"
    backtest_neutral_band_pct: float = 2.0

    # === 日志配置 ===
    log_dir: str = "./logs"  # 日志文件目录
    log_level: str = "INFO"  # 日志级别

    # === 系统配置 ===
    max_workers: int = 3  # 低并发防封禁
    debug: bool = False

    # === 定时任务配置 ===
    schedule_enabled: bool = False  # 是否启用定时任务
    schedule_time: str = "08:05"  # 每日推送时间（HH:MM 格式）
    market_review_enabled: bool = True  # 是否启用大盘复盘

    # === 实时行情增强数据配置 ===
    # 实时行情开关（关闭后使用历史收盘价进行分析）
    enable_realtime_quote: bool = True
    # 筹码分布开关（该接口不稳定，云端部署建议关闭）
    enable_chip_distribution: bool = True
    # 实时行情数据源优先级（逗号分隔）
    # 推荐顺序：tencent > akshare_sina > efinance > akshare_em > tushare
    # - tencent: 腾讯财经，有量比/换手率/市盈率等，单股查询稳定（推荐）
    # - akshare_sina: 新浪财经，基本行情稳定，但无量比
    # - efinance/akshare_em: 东财全量接口，数据最全但容易被封
    # - tushare: Tushare Pro，需要2000积分，数据全面（付费用户可优先使用）
    realtime_source_priority: str = "tencent,akshare_sina,efinance,akshare_em"
    # 实时行情缓存时间（秒）
    realtime_cache_ttl: int = 600
    # 熔断器冷却时间（秒）
    circuit_breaker_cooldown: int = 300

    # === 流控配置（防封禁关键参数）===
    # Akshare 请求间隔范围（秒）
    akshare_sleep_min: float = 2.0
    akshare_sleep_max: float = 5.0

    # 重试配置
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0

    # === WebUI 配置 ===
    webui_enabled: bool = False
    webui_host: str = "127.0.0.1"
    webui_port: int = 8000

    # === 机器人配置 ===
    bot_enabled: bool = True  # 是否启用机器人功能
    bot_command_prefix: str = "/"  # 命令前缀
    bot_rate_limit_requests: int = 10  # 频率限制：窗口内最大请求数
    bot_rate_limit_window: int = 60  # 频率限制：窗口时间（秒）
    bot_admin_users: List[str] = field(default_factory=list)  # 管理员用户 ID 列表

    # 飞书机器人（事件订阅）- 已有 feishu_app_id, feishu_app_secret
    feishu_verification_token: Optional[str] = None  # 事件订阅验证 Token
    feishu_encrypt_key: Optional[str] = None  # 消息加密密钥（可选）
    feishu_stream_enabled: bool = False  # 是否启用 Stream 长连接模式（无需公网IP）

    # 单例实例存储
    _instance: Optional["Config"] = None

    @classmethod
    def get_instance(cls) -> "Config":
        """
        获取配置单例实例

        单例模式确保：
        1. 全局只有一个配置实例
        2. 配置只从环境变量加载一次
        3. 所有模块共享相同配置
        """
        if cls._instance is None:
            cls._instance = cls._load_from_env()
        return cls._instance

    @classmethod
    def _load_from_env(cls) -> "Config":
        """
        从 .env 文件加载配置

        加载优先级：
        1. 系统环境变量
        2. .env 文件
        3. 代码中的默认值
        """
        # 确保环境变量已加载
        load_dotenv(".env")

        # 解析自选股列表（逗号分隔）
        stock_list_str = os.getenv("STOCK_LIST", "")
        stock_list = [code.strip() for code in stock_list_str.split(",") if code.strip()]

        # 如果没有配置，使用默认的示例股票
        if not stock_list:
            stock_list = ["600519", "000001", "300750"]

        # 解析搜索引擎 API Keys（支持多个 key，逗号分隔）
        bocha_keys_str = os.getenv("BOCHA_API_KEYS", "")
        bocha_api_keys = [k.strip() for k in bocha_keys_str.split(",") if k.strip()]

        tavily_keys_str = os.getenv("TAVILY_API_KEYS", "")
        tavily_api_keys = [k.strip() for k in tavily_keys_str.split(",") if k.strip()]

        serpapi_keys_str = os.getenv("SERPAPI_API_KEYS", "")
        serpapi_keys = [k.strip() for k in serpapi_keys_str.split(",") if k.strip()]

        brave_keys_str = os.getenv("BRAVE_API_KEYS", "")
        brave_api_keys = [k.strip() for k in brave_keys_str.split(",") if k.strip()]

        return cls(
            longport_app_key=os.getenv("LONGPORT_APP_KEY", ""),
            longport_app_secret=os.getenv("LONGPORT_APP_SECRET", ""),
            longport_access_token=os.getenv("LONGPORT_ACCESS_TOKEN", ""),
            longport_log_path=os.getenv("LONGPORT_LOG_PATH", ""),
            stock_list=stock_list,
            feishu_app_id=os.getenv("FEISHU_APP_ID"),
            feishu_app_secret=os.getenv("FEISHU_APP_SECRET"),
            feishu_folder_token=os.getenv("FEISHU_FOLDER_TOKEN"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
            gemini_model_fallback=os.getenv("GEMINI_MODEL_FALLBACK", "gemini-2.5-flash"),
            gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            gemini_request_delay=float(os.getenv("GEMINI_REQUEST_DELAY", "2.0")),
            gemini_max_retries=int(os.getenv("GEMINI_MAX_RETRIES", "5")),
            gemini_retry_delay=float(os.getenv("GEMINI_RETRY_DELAY", "5.0")),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            bocha_api_keys=bocha_api_keys,
            tavily_api_keys=tavily_api_keys,
            brave_api_keys=brave_api_keys,
            serpapi_keys=serpapi_keys,
            feishu_webhook_url=os.getenv("FEISHU_WEBHOOK_URL"),
            single_stock_notify=os.getenv("SINGLE_STOCK_NOTIFY", "false").lower() == "true",
            report_type=os.getenv("REPORT_TYPE", "simple").lower(),
            analysis_delay=float(os.getenv("ANALYSIS_DELAY", "0")),
            feishu_max_bytes=int(os.getenv("FEISHU_MAX_BYTES", "20000")),
            database_path=os.getenv("DATABASE_PATH", "./data/trade4.duckdb"),
            save_context_snapshot=os.getenv("SAVE_CONTEXT_SNAPSHOT", "true").lower() == "true",
            backtest_enabled=os.getenv("BACKTEST_ENABLED", "true").lower() == "true",
            backtest_eval_window_days=int(os.getenv("BACKTEST_EVAL_WINDOW_DAYS", "10")),
            backtest_min_age_days=int(os.getenv("BACKTEST_MIN_AGE_DAYS", "14")),
            backtest_engine_version=os.getenv("BACKTEST_ENGINE_VERSION", "v1"),
            backtest_neutral_band_pct=float(os.getenv("BACKTEST_NEUTRAL_BAND_PCT", "2.0")),
            log_dir=os.getenv("LOG_DIR", "./logs"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_workers=int(os.getenv("MAX_WORKERS", "3")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            schedule_enabled=os.getenv("SCHEDULE_ENABLED", "false").lower() == "true",
            schedule_time=os.getenv("SCHEDULE_TIME", "18:00"),
            market_review_enabled=os.getenv("MARKET_REVIEW_ENABLED", "true").lower() == "true",
            webui_enabled=os.getenv("WEBUI_ENABLED", "false").lower() == "true",
            webui_host=os.getenv("WEBUI_HOST", "127.0.0.1"),
            webui_port=int(os.getenv("WEBUI_PORT", "8000")),
            # 机器人配置
            bot_enabled=os.getenv("BOT_ENABLED", "true").lower() == "true",
            bot_command_prefix=os.getenv("BOT_COMMAND_PREFIX", "/"),
            bot_rate_limit_requests=int(os.getenv("BOT_RATE_LIMIT_REQUESTS", "10")),
            bot_rate_limit_window=int(os.getenv("BOT_RATE_LIMIT_WINDOW", "60")),
            bot_admin_users=[u.strip() for u in os.getenv("BOT_ADMIN_USERS", "").split(",") if u.strip()],
            # 飞书机器人
            feishu_verification_token=os.getenv("FEISHU_VERIFICATION_TOKEN"),
            feishu_encrypt_key=os.getenv("FEISHU_ENCRYPT_KEY"),
            feishu_stream_enabled=os.getenv("FEISHU_STREAM_ENABLED", "false").lower() == "true",
            # 实时行情增强数据配置
            enable_realtime_quote=os.getenv("ENABLE_REALTIME_QUOTE", "true").lower() == "true",
            enable_chip_distribution=os.getenv("ENABLE_CHIP_DISTRIBUTION", "true").lower() == "true",
            # 实时行情数据源优先级：
            # - tencent: 腾讯财经，有量比/换手率/PE/PB等，单股查询稳定（推荐）
            # - akshare_sina: 新浪财经，基本行情稳定，但无量比
            # - efinance/akshare_em: 东财全量接口，数据最全但容易被封
            # - tushare: Tushare Pro，需要2000积分，数据全面
            realtime_source_priority=cls._resolve_realtime_source_priority(),
            realtime_cache_ttl=int(os.getenv("REALTIME_CACHE_TTL", "600")),
            circuit_breaker_cooldown=int(os.getenv("CIRCUIT_BREAKER_COOLDOWN", "300")),
        )

    @classmethod
    def _resolve_realtime_source_priority(cls) -> str:
        """
        Resolve realtime source priority with automatic tushare injection.

        When TUSHARE_TOKEN is configured but REALTIME_SOURCE_PRIORITY is not
        explicitly set, automatically prepend 'tushare' to the default priority
        so that the paid data source is utilized for realtime quotes as well.
        """
        explicit = os.getenv("REALTIME_SOURCE_PRIORITY")
        default_priority = "tencent,akshare_sina,efinance,akshare_em"

        if explicit:
            # User explicitly set priority, respect it
            return explicit

        tushare_token = os.getenv("TUSHARE_TOKEN", "").strip()
        if tushare_token:
            # Token configured but no explicit priority override
            # Prepend tushare so the paid source is tried first
            import logging

            logger = logging.getLogger(__name__)
            resolved = f"tushare,{default_priority}"
            logger.info(f"TUSHARE_TOKEN detected, auto-injecting tushare into realtime priority: {resolved}")
            return resolved

        return default_priority

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）"""
        cls._instance = None

    def refresh_stock_list(self) -> None:
        """
        热读取 STOCK_LIST 环境变量并更新配置中的自选股列表

        支持两种配置方式：
        1. .env 文件（本地开发、定时任务模式） - 修改后下次执行自动生效
        2. 系统环境变量（GitHub Actions、Docker） - 启动时固定，运行中不变
        """
        # 优先从 .env 文件读取最新配置，这样即使在容器环境中修改了 .env 文件，
        # 也能获取到最新的股票列表配置
        stock_list_str = os.getenv("STOCK_LIST", "")
        stock_list = [code.strip() for code in stock_list_str.split(",") if code.strip()]

        if not stock_list:
            stock_list = ["000001"]

        self.stock_list = stock_list

    def validate(self) -> List[str]:
        """
        验证配置完整性

        Returns:
            缺失或无效配置项的警告列表
        """
        warnings = []

        if not self.stock_list:
            warnings.append("警告：未配置自选股列表 (STOCK_LIST)")

        if not self.gemini_api_key and not self.openai_api_key:
            warnings.append("警告：未配置 Gemini 或 OpenAI API Key，AI 分析功能将不可用")
        elif not self.gemini_api_key:
            warnings.append("提示：未配置 Gemini API Key，将使用 OpenAI 兼容 API")

        if not self.bocha_api_keys and not self.tavily_api_keys and not self.brave_api_keys and not self.serpapi_keys:
            warnings.append("提示：未配置搜索引擎 API Key (Bocha/Tavily/Brave/SerpAPI)，新闻搜索功能将不可用")

        # 检查通知配置
        has_notification = self.feishu_webhook_url
        if not has_notification:
            warnings.append("提示：未配置通知渠道，将不发送推送通知")

        return warnings

    def get_db_url(self) -> str:
        """
        获取 SQLAlchemy 数据库连接 URL

        自动创建数据库目录（如果不存在）
        """
        return f"sqlite:///{self.database_path}"


# === 便捷的配置访问函数 ===
def get_config() -> Config:
    """获取全局配置实例的快捷方式"""
    return Config.get_instance()


if __name__ == "__main__":
    # 测试配置加载
    config = get_config()
    print("=== 配置加载测试 ===")
    print(f"自选股列表: {config.stock_list}")
    print(f"数据库路径: {config.database_path}")
    print(f"最大并发数: {config.max_workers}")
    print(f"调试模式: {config.debug}")

    # 验证配置
    warnings = config.validate()
    if warnings:
        print("\n配置验证结果:")
        for w in warnings:
            print(f"  - {w}")
