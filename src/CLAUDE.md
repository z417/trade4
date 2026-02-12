# 技术栈与规范
- 环境: Python 3.12+, conda 隔离, Decimal 处理金额
- 核心库: duckdb, pandas-ta, dataclasses(扁平/禁深嵌套)
- 范式: 接口抽象、单例 (Singleton)、注入 (DI)、策略模式
- Pythonic: 遵循 Zen of Python, PEP 8/257, 全量类型注解, 中文 Docstring
- 原则: DRY, 高内聚低耦合, 可读性 > 复杂度

# 项目结构
```
src/
├── ai/        # AI集成层
├── brokers/   # 券商 SDK 适配（屏蔽差异）
├── core/      # 核心抽象/基类
├── markets/   # 市场特定行情
├── services/  # 业务逻辑 (DI 注入接口)
└── utils/     # 工具 (DuckDB/度量等)
tests/                          
```

# 常用命令
```shell
# 激活虚拟环境
conda activate .venv
# 安装/升级依赖
pip install -r requirements.txt -U
# 代码格式化
black src/
# 运行项目
python main.py
```

# 行为准则
- 批判思维: 主动质询非 Pythonic 逻辑，严厉拒绝违背 PEP 规范的实现
- 拒绝伪造: 严禁 pass 占位，所有代码须具备真实逻辑
- 逐个击破: 优先标准库，利用 REPL/交互式验证组件
- 坚韧调试: 深度使用 pdb/日志，而非盲目猜测

# 详细规范文档
- [开发指南](src/docs/dev-guidelines.md): 模块简介
